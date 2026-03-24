"""
Chatbot Service — Qdrant Repository

Handles vector search operations for RAG retrieval.
"""

from typing import List
from uuid import UUID
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from shared.embedding.embedder import embed_text, embed_texts
from shared.logger.logger import get_logger
from infrastructure.qdrant.client import COLLECTION_NAME, get_qdrant_client

logger = get_logger(__name__)


class QdrantRepository:
    """Repository for vector operations — search and index embeddings."""

    async def search_similar(
        self, query: str, user_id: str, limit: int = 5
    ) -> List[dict]:
        """
        Search for paper chunks similar to the query.
        Filters by user_id to only return user's papers.
        """
        client = get_qdrant_client()
        try:
            query_vector = embed_text(query)

            results = await client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id),
                        )
                    ]
                ),
                limit=limit,
            )

            chunks = []
            for result in results:
                chunks.append({
                    "text": result.payload.get("text", ""),
                    "paper_id": result.payload.get("paper_id", ""),
                    "page_number": result.payload.get("page_number"),
                    "section": result.payload.get("section", ""),
                    "score": result.score,
                })

            logger.info(
                "qdrant_search_complete",
                query_len=len(query),
                results=len(chunks),
            )
            return chunks
        finally:
            await client.close()

    async def index_paper_chunks(
        self, paper_id: str, user_id: str, chunks: List[dict]
    ) -> int:
        """
        Index paper text chunks into Qdrant.
        Each chunk has: text, page_number, section, chunk_index.
        """
        client = get_qdrant_client()
        try:
            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)

            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                import uuid as uuid_mod
                points.append(
                    PointStruct(
                        id=str(uuid_mod.uuid4()),
                        vector=embedding,
                        payload={
                            "paper_id": paper_id,
                            "user_id": user_id,
                            "text": chunk["text"],
                            "page_number": chunk.get("page_number"),
                            "section": chunk.get("section", ""),
                            "chunk_index": i,
                            "token_count": chunk.get("token_count", 0),
                        },
                    )
                )

            await client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
            )

            logger.info(
                "qdrant_indexed",
                paper_id=paper_id,
                chunks_count=len(points),
            )
            return len(points)
        finally:
            await client.close()
