"""
Tests for the ChatService RAG pipeline.
Uses mocked dependencies (Redis, Qdrant, LLM, DB).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


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
                {"text": "Attention is a mechanism...", "metadata": {"page": 1}},
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
                {"text": "Transformers use self-attention.", "metadata": {"page": 1}},
            ],
            history=[],
        )
        # The system or user message should contain the context
        all_content = " ".join(m["content"] for m in messages)
        assert "self-attention" in all_content or "Transformers" in all_content

    def test_build_prompt_includes_history(self):
        from services.chatbot_service.utils.prompt_builder import build_rag_prompt

        history_msg = MagicMock()
        history_msg.role = "user"
        history_msg.content = "Previous question"

        messages = build_rag_prompt(
            question="Follow-up question",
            context_chunks=[],
            history=[history_msg],
        )
        assert len(messages) >= 3  # system + history + user


# ═══════════════════════════════════════════════════════════════════════
# Citation Mapper Tests
# ═══════════════════════════════════════════════════════════════════════

class TestCitationMapper:
    """Tests for the citation mapping utility."""

    def test_map_citations_returns_list(self):
        from services.chatbot_service.utils.citation_mapper import map_citations

        result = map_citations(
            response_text="This is based on attention mechanisms.",
            context_chunks=[
                {"text": "Attention is all you need", "metadata": {"paper_id": "p1", "page": 1}},
            ],
        )
        assert isinstance(result, list)

    def test_map_citations_empty_chunks(self):
        from services.chatbot_service.utils.citation_mapper import map_citations

        result = map_citations(
            response_text="General knowledge answer.",
            context_chunks=[],
        )
        assert result == [] or isinstance(result, list)


# ═══════════════════════════════════════════════════════════════════════
# ChatService Tests (with mocks)
# ═══════════════════════════════════════════════════════════════════════

class TestChatService:
    """Integration tests for ChatService with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_send_message_cache_miss(self, mock_chat_repo, mock_redis, mock_qdrant, mock_llm_client):
        """Test full RAG flow when cache misses."""
        with patch("services.chatbot_service.services.chat_service.get_redis_client", return_value=mock_redis), \
             patch("services.chatbot_service.services.chat_service.QdrantRepository", return_value=mock_qdrant), \
             patch("services.chatbot_service.services.chat_service.LLMClient", return_value=mock_llm_client), \
             patch("services.chatbot_service.services.chat_service.get_provider_model", return_value="groq/llama3"):

            from services.chatbot_service.services.chat_service import ChatService

            service = ChatService.__new__(ChatService)
            service.chat_repo = mock_chat_repo
            service.qdrant_repo = mock_qdrant

            session_id = uuid4()
            user_id = uuid4()

            result = await service.send_message(
                content="What is attention?",
                session_id=session_id,
                user_id=user_id,
            )
            assert result is not None
            assert mock_chat_repo.add_message.called

    @pytest.mark.asyncio
    async def test_send_message_session_not_found(self, mock_chat_repo, mock_redis):
        """Test that missing session raises SessionNotFoundException."""
        mock_chat_repo.get_session.return_value = None

        with patch("services.chatbot_service.services.chat_service.get_redis_client", return_value=mock_redis):
            from services.chatbot_service.services.chat_service import ChatService
            from shared.error_handler.exceptions import SessionNotFoundException

            service = ChatService.__new__(ChatService)
            service.chat_repo = mock_chat_repo
            service.qdrant_repo = AsyncMock()

            with pytest.raises(SessionNotFoundException):
                await service.send_message(
                    content="Hello",
                    session_id=uuid4(),
                    user_id=uuid4(),
                )
