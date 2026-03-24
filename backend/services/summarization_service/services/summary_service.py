"""
Summarization Service — Business Logic

Supports two modes:
- Model mode: DistilBART (local, free, offline)
- LLM mode: Any LiteLLM provider (cloud)

Includes Redis caching with 24h TTL.
"""

from uuid import UUID
from typing import Optional
from fastapi import Depends
from services.summarization_service.repository.summary_repo import SummaryRepository
from services.summarization_service.models.schemas import SummaryResponse
from shared.llm_client.client import LLMClient
from shared.llm_client.providers import get_provider_model
from shared.llm_client.mode_selector import ModeSelector
from shared.chunking.text_chunker import chunk_text
from shared.error_handler.exceptions import PaperNotFoundException
from shared.logger.logger import get_logger
from settings import settings
from infrastructure.redis.client import get_redis_client

logger = get_logger(__name__)
mode_selector = ModeSelector()

# Lazy-loaded summarization model
_summarizer = None


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        logger.info("loading_summarization_model", model="distilbart-cnn-12-6")
        from transformers import pipeline
        _summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device=-1,  # CPU
        )
        logger.info("summarization_model_loaded")
    return _summarizer


class SummarizationService:
    """Business logic for paper summarization."""

    def __init__(self, repo: SummaryRepository = Depends()):
        self.repo = repo

    async def summarize(
        self, paper_id: UUID, user_id: UUID, mode: Optional[str] = None
    ) -> SummaryResponse:
        """
        Summarize a paper using model or LLM mode.
        Checks Redis cache first, saves result after processing.
        """
        resolved_mode = mode_selector.get_strategy("summarization", mode)

        # Check Redis cache
        redis = get_redis_client()
        cache_key = f"summary:{paper_id}:{resolved_mode}"
        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.debug("cache_hit", key=cache_key)
                return SummaryResponse(
                    content=cached,
                    paper_id=paper_id,
                    mode_used=resolved_mode,
                )
        except Exception:
            pass
        finally:
            await redis.close()

        # Get paper text
        text = await self.repo.get_paper_text(paper_id)
        if not text:
            raise PaperNotFoundException(paper_id)

        # Process based on mode
        if resolved_mode == "model":
            summary = await self._summarize_model(text)
        else:
            summary = await self._summarize_llm(text)

        # Save to database
        result = await self.repo.save_result(
            paper_id=paper_id, user_id=user_id, content=summary, mode=resolved_mode
        )

        # Cache in Redis (24h TTL)
        redis = get_redis_client()
        try:
            await redis.setex(cache_key, 86400, summary)
        except Exception:
            pass
        finally:
            await redis.close()

        return SummaryResponse(
            content=summary,
            paper_id=paper_id,
            mode_used=resolved_mode,
            created_at=result.created_at,
        )

    async def _summarize_model(self, text: str) -> str:
        """Summarize using local DistilBART model."""
        logger.info("summarize_model_start")
        chunks = chunk_text(text, chunk_size=1024)
        summarizer = _get_summarizer()

        summaries = []
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
            result = summarizer(
                chunk,
                max_length=150,
                min_length=30,
                do_sample=False,
            )
            summaries.append(result[0]["summary_text"])

        summary = " ".join(summaries)
        logger.info("summarize_model_complete", chunks=len(chunks), chars=len(summary))
        return summary

    async def _summarize_llm(self, text: str) -> str:
        """Summarize using LLM via LiteLLM."""
        logger.info("summarize_llm_start", provider=settings.LLM_PROVIDER)
        provider_model = get_provider_model(settings.LLM_PROVIDER)
        client = LLMClient(
            provider=provider_model,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
        )

        # Truncate text if too long for context window
        max_chars = 12000
        truncated_text = text[:max_chars] if len(text) > max_chars else text

        summary = await client.complete(
            system="You are an expert at summarizing academic research papers. "
                   "Provide comprehensive yet concise summaries.",
            prompt=f"""Summarize the following research paper covering:
- Objectives and Research Questions
- Methodology
- Key Findings and Results
- Conclusions
- Limitations

Text:
{truncated_text}""",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info("summarize_llm_complete", provider=settings.LLM_PROVIDER)
        return summary
