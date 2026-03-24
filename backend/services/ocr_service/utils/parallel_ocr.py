"""
OCR Service — Page-Level Parallel OCR (Section 21.2)

Splits large PDFs into page chunks and processes them
concurrently using asyncio.gather for faster processing.
"""

import asyncio
from typing import List
from shared.logger.logger import get_logger

logger = get_logger(__name__)


async def ocr_large_pdf(
    pdf_bytes: bytes,
    engine,
    filename: str,
    chunk_size: int = 10,
) -> str:
    """
    Process a large PDF by splitting into page chunks and OCR-ing in parallel.

    Args:
        pdf_bytes: Raw PDF bytes
        engine: OCR engine instance (PaddleOCR, Mistral, LightOn)
        filename: Original filename for logging
        chunk_size: Number of pages per concurrent chunk

    Returns:
        Merged OCR text from all pages
    """
    try:
        from pypdf import PdfReader, PdfWriter
        from io import BytesIO

        reader = PdfReader(BytesIO(pdf_bytes))
        total_pages = len(reader.pages)

        if total_pages <= chunk_size:
            # Small PDF — process directly
            result = await engine.extract(pdf_bytes, filename)
            return result.text

        # Split into page chunks
        page_chunks = []
        for i in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            for page_num in range(i, min(i + chunk_size, total_pages)):
                writer.add_page(reader.pages[page_num])
            buffer = BytesIO()
            writer.write(buffer)
            page_chunks.append(buffer.getvalue())

        logger.info(
            "parallel_ocr_start",
            filename=filename,
            total_pages=total_pages,
            chunks=len(page_chunks),
        )

        # Process chunks concurrently
        async def ocr_chunk(chunk_bytes: bytes, chunk_idx: int) -> str:
            chunk_name = f"{filename}_chunk_{chunk_idx}"
            result = await engine.extract(chunk_bytes, chunk_name)
            return result.text

        tasks = [ocr_chunk(chunk, i) for i, chunk in enumerate(page_chunks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge results in order
        merged_text = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning("ocr_chunk_failed", chunk=i, error=str(result))
                merged_text.append(f"[OCR failed for pages {i * chunk_size + 1}-{min((i + 1) * chunk_size, total_pages)}]")
            else:
                merged_text.append(result)

        final = "\n\n".join(merged_text)
        logger.info(
            "parallel_ocr_complete",
            filename=filename,
            total_pages=total_pages,
            total_chars=len(final),
        )
        return final

    except Exception as e:
        logger.error("parallel_ocr_error", filename=filename, error=str(e))
        # Fallback to sequential processing
        result = await engine.extract(pdf_bytes, filename)
        return result.text
