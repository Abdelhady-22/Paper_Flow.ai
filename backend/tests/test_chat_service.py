"""
Tests for the ChatService RAG pipeline.
Uses mocked dependencies (Redis, Qdrant, LLM, DB).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ═══════════════════════════════════════════════════════════════════════
# Prompt Builder Tests
# ═══════════════════════════════════════════════════════════════════════

class TestPromptBuilder:
    """Tests for the RAG prompt builder utility."""

    def test_build_rag_prompt_returns_messages(self):
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        messages = build_rag_prompt(
            question="What is attention?",
            context_chunks=[
                {"text": "Attention is a mechanism...", "page_number": 1, "section": "Introduction"},
            ],
            history=[],
        )
        assert isinstance(messages, list)
        assert len(messages) >= 2  # system + user at minimum
        assert messages[0]["role"] == "system"

    def test_build_prompt_includes_context(self):
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        messages = build_rag_prompt(
            question="Explain transformers",
            context_chunks=[
                {"text": "Transformers use self-attention.", "page_number": 1, "section": "Intro"},
            ],
            history=[],
        )
        # The system message should contain the context
        system_content = messages[0]["content"]
        assert "self-attention" in system_content or "Transformers" in system_content

    def test_build_prompt_with_empty_history(self):
        """Empty history should produce exactly 2 messages: system + user."""
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        messages = build_rag_prompt(
            question="What is attention?",
            context_chunks=[],
            history=[],
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "What is attention?"

    def test_build_prompt_with_multi_turn_history(self):
        """History with 3+ items should include the intermediate entries (excluding last)."""
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        msg1 = MagicMock(role="user", content="First question")
        msg2 = MagicMock(role="assistant", content="First answer")
        msg3 = MagicMock(role="user", content="Follow-up")

        messages = build_rag_prompt(
            question="Current question",
            context_chunks=[],
            history=[msg1, msg2, msg3],
        )
        # system + 2 history entries (msg1, msg2, NOT msg3 since it's :-1) + user
        assert len(messages) == 4
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "First question"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "First answer"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Current question"

    def test_no_context_adds_note(self):
        """When no context chunks are provided, system message should note it."""
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        messages = build_rag_prompt(
            question="Anything",
            context_chunks=[],
            history=None,
        )
        assert "No relevant paper content" in messages[0]["content"]
