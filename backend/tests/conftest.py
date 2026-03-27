"""
Shared test fixtures and mocks for all unit tests.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Mock settings before any service imports ─────────────────────────
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Provide a minimal settings object for tests without requiring .env."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("QDRANT_HOST", "localhost")
    monkeypatch.setenv("QDRANT_PORT", "6333")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("STT_PROVIDER", "whisper")
    monkeypatch.setenv("TTS_PROVIDER", "edge_tts")
    monkeypatch.setenv("OCR_ENGINE", "paddle")
    monkeypatch.setenv("DEBUG", "true")


# ── LLM Mocks ────────────────────────────────────────────────────────
@pytest.fixture
def mock_llm_client():
    """Mock LLMClient for tests that don't need real LLM calls."""
    client = AsyncMock()
    client.complete.return_value = "Mock LLM response"
    client.complete_chat.return_value = "Mock chat response with citations."
    return client


# ── Redis Mocks ──────────────────────────────────────────────────────
@pytest.fixture
def mock_redis():
    """Mock async Redis client."""
    redis = AsyncMock()
    redis.get.return_value = None
    redis.setex.return_value = True
    redis.close.return_value = None
    return redis


# ── Qdrant Mocks ─────────────────────────────────────────────────────
@pytest.fixture
def mock_qdrant():
    """Mock Qdrant repository."""
    repo = AsyncMock()
    repo.search_similar.return_value = [
        {"text": "Attention is all you need.", "metadata": {"paper_id": "p1", "page": 1}},
        {"text": "Transformer architecture overview.", "metadata": {"paper_id": "p1", "page": 2}},
    ]
    return repo


# ── Database Mocks ───────────────────────────────────────────────────
@pytest.fixture
def mock_chat_repo():
    """Mock ChatRepository."""
    repo = AsyncMock()
    repo.get_session.return_value = MagicMock(id="session-1")
    repo.add_message.return_value = MagicMock(
        id="msg-1",
        session_id="session-1",
        role="assistant",
        content="Test response",
        citations=[],
        input_type="text",
        feedback=None,
        created_at="2024-01-01T00:00:00",
    )
    repo.get_session_messages.return_value = []
    return repo
