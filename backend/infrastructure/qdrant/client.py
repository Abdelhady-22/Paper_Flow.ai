"""
Infrastructure — Qdrant Vector Database Client

Provides async Qdrant client for storing and searching paper chunk embeddings.
Collection: 'papers' with 384-dimensional vectors (all-MiniLM-L6-v2).
"""

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)
from settings import settings
from shared.logger.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "papers"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension


def get_qdrant_client() -> AsyncQdrantClient:
    """Create and return an async Qdrant client."""
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


async def ensure_collection(client: AsyncQdrantClient) -> None:
    """Ensure the papers collection exists with correct configuration."""
    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if COLLECTION_NAME not in collection_names:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        logger.info(
            "qdrant_collection_created",
            collection=COLLECTION_NAME,
            vector_size=VECTOR_SIZE,
        )
    else:
        logger.info(
            "qdrant_collection_exists",
            collection=COLLECTION_NAME,
        )


async def init_qdrant() -> AsyncQdrantClient:
    """Initialize Qdrant client and ensure collection exists."""
    client = get_qdrant_client()
    await ensure_collection(client)
    return client


async def close_qdrant(client: AsyncQdrantClient) -> None:
    """Close Qdrant client connection."""
    await client.close()
