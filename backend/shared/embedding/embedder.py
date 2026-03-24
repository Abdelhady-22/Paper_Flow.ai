"""
Shared — Sentence Transformers Embedding Wrapper

Wraps the all-MiniLM-L6-v2 model for generating 384-dimensional embeddings.
Used by the RAG pipeline to embed paper chunks and user queries.

Model is loaded lazily on first use and cached for subsequent calls.
"""

from typing import List
from shared.logger.logger import get_logger

logger = get_logger(__name__)

# Lazy-loaded model singleton
_model = None
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        logger.info("embedding_model_loading", model=MODEL_NAME)
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)
        logger.info("embedding_model_loaded", model=MODEL_NAME, dim=VECTOR_SIZE)
    return _model


def embed_text(text: str) -> List[float]:
    """
    Generate a 384-dimensional embedding for a single text.

    Args:
        text: The text to embed

    Returns:
        List of 384 floats representing the embedding vector
    """
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batch.
    More efficient than calling embed_text() in a loop.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors (each 384-dim)
    """
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return embeddings.tolist()
