"""
Chatbot Service — RAG Service (Business Logic)

Full RAG pipeline:
1. Embed query → Qdrant vector search → retrieve context chunks
2. Build prompt with system + context + conversation history
3. Call LLM via LiteLLM
4. Map response to citations
5. Save to PostgreSQL
"""

from uuid import UUID
from typing import Optional, List
import hashlib
from fastapi import Depends
from services.chatbot_service.repository.chat_repo import ChatRepository
from services.chatbot_service.repository.qdrant_repo import QdrantRepository
from services.chatbot_service.models.schemas import ChatMessageResponse, Citation
from services.chatbot_service.utils.prompt_builder import build_rag_prompt
from services.chatbot_service.utils.citation_mapper import map_citations
from shared.llm_client.client import LLMClient
from shared.llm_client.providers import get_provider_model
from shared.error_handler.exceptions import SessionNotFoundException
from shared.logger.logger import get_logger
from settings import settings
from infrastructure.redis.client import get_redis_client

logger = get_logger(__name__)


class ChatService:
    """RAG-powered chat service."""

    def __init__(
        self,
        chat_repo: ChatRepository = Depends(),
    ):
        self.chat_repo = chat_repo
        self.qdrant_repo = QdrantRepository()

    async def send_message(
        self,
        content: str,
        session_id: UUID,
        user_id: UUID,
        input_type: str = "text",
    ) -> ChatMessageResponse:
        """
        Process a user message and generate a RAG-powered response.
        """
        # Verify session exists
        session = await self.chat_repo.get_session(session_id)
        if not session:
            raise SessionNotFoundException(session_id)

        # Save user message
        user_msg = await self.chat_repo.add_message(
            session_id=session_id,
            role="user",
            content=content,
            input_type=input_type,
        )

        # Check Redis cache
        prompt_hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()
        redis = get_redis_client()
        cache_key = f"llm:{prompt_hash}"
        cached_response = None
        try:
            cached_response = await redis.get(cache_key)
        except Exception:
            pass
        finally:
            await redis.close()

        if cached_response:
            logger.debug("cache_hit", key=cache_key)
            assistant_msg = await self.chat_repo.add_message(
                session_id=session_id,
                role="assistant",
                content=cached_response,
                citations=[],
            )
            return self._to_response(assistant_msg)

        # RAG: Retrieve relevant chunks from Qdrant
        context_chunks = await self.qdrant_repo.search_similar(
            query=content, user_id=str(user_id), limit=5
        )

        # Get conversation history (last 10 messages)
        history = await self.chat_repo.get_session_messages(session_id)
        recent_history = history[-10:]

        # Build RAG prompt
        messages = build_rag_prompt(
            question=content,
            context_chunks=context_chunks,
            history=recent_history,
        )

        # Call LLM
        provider_model = get_provider_model(settings.CHAT_LLM_PROVIDER or settings.LLM_PROVIDER)
        client = LLMClient(
            provider=provider_model,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
        )
        response_text = await client.complete_chat(
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        # Map citations
        citations = map_citations(response_text, context_chunks)
        citations_dicts = [c.model_dump() for c in citations]

        # Save assistant message
        assistant_msg = await self.chat_repo.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            citations=citations_dicts,
        )

        # Cache LLM response (6h)
        redis = get_redis_client()
        try:
            await redis.setex(cache_key, 21600, response_text)
        except Exception:
            pass
        finally:
            await redis.close()

        logger.info(
            "chat_response_generated",
            session_id=str(session_id),
            context_chunks=len(context_chunks),
            citations=len(citations),
        )

        return self._to_response(assistant_msg, citations)

    def _to_response(
        self, msg, citations: Optional[List[Citation]] = None
    ) -> ChatMessageResponse:
        return ChatMessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            citations=citations,
            input_type=msg.input_type,
            feedback=msg.feedback,
            created_at=msg.created_at,
        )
