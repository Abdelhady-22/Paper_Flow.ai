"""
Agent Service — Paper Import Pipeline

Runs the full ingestion pipeline on downloaded PDFs:
PDF → text extraction → OCR (if needed) → chunk → embed → Qdrant + PostgreSQL

Used by the import_agent in the CrewAI pipeline.
Implements Section 8.4 from the guide.
"""

import asyncio
from uuid import UUID, uuid4
from pathlib import Path
from typing import Optional

from shared.chunking.text_chunker import chunk_text, count_tokens
from shared.embedding.embedder import embed_texts
from shared.logger.logger import get_logger
from shared.progress.tracker import progress_tracker
from services.ocr_service.utils.file_parser import extract_text_from_pdf
from infrastructure.qdrant.client import get_qdrant_client, COLLECTION_NAME
from infrastructure.postgres.database import AsyncSessionFactory
from shared.models.domain import Paper
from qdrant_client.models import PointStruct

logger = get_logger(__name__)


async def import_paper(
    file_path: str,
    title: str,
    user_id: str,
    paper_id: str,
    task_id: Optional[str] = None,
) -> dict:
    """
    Full import pipeline for a single paper:
    1. Read PDF bytes
    2. Extract text (PyPDF2/pdfplumber + OCR fallback)
    3. Chunk text (tiktoken + NLTK, 500 tokens, 50 overlap)
    4. Embed chunks (sentence-transformers 384-dim)
    5. Store in Qdrant (vector DB)
    6. Save paper record to PostgreSQL

    Args:
        file_path: Path to the downloaded PDF
        title: Paper title
        user_id: User ID
        paper_id: Pre-generated paper ID
        task_id: Optional task ID for progress tracking

    Returns:
        Dict with import status and details
    """
    try:
        # Step 1: Read file
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            return {"paper_id": paper_id, "success": False, "error": "File not found"}

        content = pdf_path.read_bytes()

        if task_id:
            await progress_tracker.publish(task_id, "importing", 0.1, f"Extracting text from: {title}")

        # Step 2: Extract text
        text = await extract_text_from_pdf(content, title)

        if not text:
            # Fallback to PaddleOCR
            try:
                from services.ocr_service.utils.paddle_wrapper import PaddleOCREngine
                ocr = PaddleOCREngine()
                ocr_result = await ocr.extract(content, f"{title}.pdf")
                text = ocr_result.text
            except Exception as e:
                logger.warning("import_ocr_fallback_failed", title=title, error=str(e))

        if not text or len(text.strip()) < 50:
            return {
                "paper_id": paper_id,
                "title": title,
                "success": False,
                "error": "Could not extract meaningful text from PDF",
            }

        if task_id:
            await progress_tracker.publish(task_id, "importing", 0.3, f"Chunking text: {title}")

        # Step 3: Chunk text
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        chunk_dicts = []
        for i, chunk in enumerate(chunks):
            chunk_dicts.append({
                "text": chunk,
                "chunk_index": i,
                "token_count": count_tokens(chunk),
                "page_number": None,
                "section": "",
            })

        if task_id:
            await progress_tracker.publish(task_id, "importing", 0.5, f"Embedding {len(chunks)} chunks: {title}")

        # Step 4: Embed chunks
        chunk_texts = [c["text"] for c in chunk_dicts]
        embeddings = embed_texts(chunk_texts)

        if task_id:
            await progress_tracker.publish(task_id, "importing", 0.7, f"Storing in Qdrant: {title}")

        # Step 5: Store in Qdrant
        client = get_qdrant_client()
        try:
            points = []
            for chunk_dict, embedding in zip(chunk_dicts, embeddings):
                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=embedding,
                        payload={
                            "paper_id": paper_id,
                            "user_id": user_id,
                            "text": chunk_dict["text"],
                            "chunk_index": chunk_dict["chunk_index"],
                            "page_number": chunk_dict.get("page_number"),
                            "section": chunk_dict.get("section", ""),
                            "token_count": chunk_dict["token_count"],
                        },
                    )
                )

            await client.upsert(collection_name=COLLECTION_NAME, points=points)
        finally:
            await client.close()

        if task_id:
            await progress_tracker.publish(task_id, "importing", 0.9, f"Saving to PostgreSQL: {title}")

        # Step 6: Save to PostgreSQL
        async with AsyncSessionFactory() as session:
            paper = Paper(
                id=UUID(paper_id),
                user_id=UUID(user_id),
                filename=f"{title}.pdf",
                file_path=file_path,
                extracted_text=text,
                source="agent",
                page_count=None,
                language="en",
                status="processed",
            )
            session.add(paper)
            await session.commit()

        logger.info(
            "paper_imported",
            paper_id=paper_id,
            title=title,
            chunks=len(chunks),
            chars=len(text),
        )

        return {
            "paper_id": paper_id,
            "title": title,
            "success": True,
            "chunks_indexed": len(chunks),
            "text_length": len(text),
        }

    except Exception as e:
        logger.error("import_pipeline_error", paper_id=paper_id, title=title, error=str(e))
        return {
            "paper_id": paper_id,
            "title": title,
            "success": False,
            "error": str(e),
        }


async def batch_import_papers(
    papers: list,
    user_id: str,
    task_id: Optional[str] = None,
) -> list:
    """
    Import multiple papers concurrently using asyncio.gather.
    Implements batch processing from Section 22-23.
    """
    tasks = [
        import_paper(
            file_path=p.get("file_path", ""),
            title=p.get("title", "Unknown"),
            user_id=user_id,
            paper_id=p.get("paper_id", str(uuid4())),
            task_id=task_id,
        )
        for p in papers
        if p.get("file_path") and p.get("success", False)
    ]

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    clean_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error("batch_import_exception", error=str(result))
            clean_results.append({"success": False, "error": str(result)})
        else:
            clean_results.append(result)

    return clean_results
