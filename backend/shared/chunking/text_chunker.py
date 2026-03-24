"""
Shared — Text Chunker

Splits text into overlapping chunks using tiktoken for token counting
and NLTK for sentence boundary detection.

Parameters from Section 25.2:
- Chunk size: 500 tokens
- Overlap: 50 tokens
- Tokenizer: tiktoken (cl100k_base)
- Boundary: NLTK sentence tokenizer
"""

from typing import List
import nltk
import tiktoken
from shared.logger.logger import get_logger

logger = get_logger(__name__)

# Ensure NLTK punkt tokenizer is available
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[str]:
    """
    Split text into overlapping chunks using tiktoken + NLTK.

    Args:
        text: The text to split
        chunk_size: Maximum tokens per chunk (default: 500)
        overlap: Number of sentences to overlap between chunks (default: 50)

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return [text] if text.strip() else []

    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0
    enc = tiktoken.get_encoding("cl100k_base")

    for sentence in sentences:
        tokens = len(enc.encode(sentence))

        if current_tokens + tokens > chunk_size and current:
            chunks.append(" ".join(current))
            # Keep last few sentences for overlap
            overlap_sentences = current[-overlap:] if overlap > 0 else []
            current = list(overlap_sentences)
            current_tokens = sum(len(enc.encode(s)) for s in current)

        current.append(sentence)
        current_tokens += tokens

    if current:
        chunks.append(" ".join(current))

    logger.debug(
        "text_chunked",
        total_chunks=len(chunks),
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return chunks


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text using tiktoken."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))
