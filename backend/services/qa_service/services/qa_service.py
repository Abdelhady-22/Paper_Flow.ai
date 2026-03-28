"""
Q&A Service — Business Logic

Supports two modes:
- Model mode: T5-small (local)
- LLM mode: Any LiteLLM provider

Includes Redis caching with 24h TTL.
"""

import re
import json
from uuid import UUID
from typing import Optional, List
from fastapi import Depends
from services.qa_service.repository.qa_repo import QARepository
from services.qa_service.models.schemas import QAResponse, QAPair
from shared.llm_client.client import LLMClient
from shared.llm_client.providers import get_provider_model, get_provider_api_key
from shared.llm_client.mode_selector import ModeSelector
from shared.chunking.text_chunker import chunk_text
from shared.error_handler.exceptions import PaperNotFoundException
from shared.logger.logger import get_logger
from settings import settings
from infrastructure.redis.client import get_redis_client

logger = get_logger(__name__)
mode_selector = ModeSelector()

_qa_pipeline = None


def _get_qa_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        logger.info("loading_qa_model", model="t5-small")
        from transformers import pipeline
        _qa_pipeline = pipeline(
            "text2text-generation",
            model="t5-small",
            device=-1,
        )
        logger.info("qa_model_loaded")
    return _qa_pipeline


def parse_qa_pairs(text: str) -> List[QAPair]:
    """Parse Q&A pairs from text in Q: ... A: ... format."""
    pairs = []
    pattern = r"Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    for q, a in matches:
        q, a = q.strip(), a.strip()
        if q and a:
            pairs.append(QAPair(question=q, answer=a))
    return pairs


class QAService:
    def __init__(self, repo: QARepository = Depends()):
        self.repo = repo

    async def generate_qa(
        self, paper_id: UUID, user_id: UUID, mode: Optional[str] = None, num_questions: int = 10
    ) -> QAResponse:
        resolved_mode = mode_selector.get_strategy("qa", mode)

        # Check Redis cache
        redis = get_redis_client()
        cache_key = f"qa:{paper_id}:{resolved_mode}"
        try:
            cached = await redis.get(cache_key)
            if cached:
                qa_data = json.loads(cached)
                return QAResponse(
                    qa_pairs=[QAPair(question=qa["q"], answer=qa["a"]) for qa in qa_data],
                    paper_id=paper_id, mode_used=resolved_mode,
                    total_questions=len(qa_data),
                )
        except Exception:
            pass
        finally:
            await redis.close()

        text = await self.repo.get_paper_text(paper_id)
        if not text:
            raise PaperNotFoundException(paper_id)

        if resolved_mode == "model":
            qa_pairs = await self._generate_model(text, num_questions)
        else:
            qa_pairs = await self._generate_llm(text, num_questions)

        result = await self.repo.save_result(
            paper_id=paper_id, user_id=user_id, qa_pairs=qa_pairs, mode=resolved_mode,
        )

        # Cache (24h)
        redis = get_redis_client()
        try:
            await redis.setex(
                cache_key, 86400,
                json.dumps([{"q": qa.question, "a": qa.answer} for qa in qa_pairs]),
            )
        except Exception:
            pass
        finally:
            await redis.close()

        return QAResponse(
            qa_pairs=qa_pairs, paper_id=paper_id,
            mode_used=resolved_mode, total_questions=len(qa_pairs),
            created_at=result.created_at,
        )

    async def _generate_model(self, text: str, num_questions: int) -> List[QAPair]:
        logger.info("qa_model_start")
        pipeline = _get_qa_pipeline()
        chunks = chunk_text(text, chunk_size=512)
        all_pairs = []

        for chunk in chunks[:5]:  # Limit chunks for model mode
            output = pipeline(
                f"generate questions: {chunk}",
                max_length=512,
                num_return_sequences=1,
            )
            pairs = parse_qa_pairs(output[0]["generated_text"])
            all_pairs.extend(pairs)
            if len(all_pairs) >= num_questions:
                break

        result = all_pairs[:num_questions]
        logger.info("qa_model_complete", questions=len(result))
        return result

    async def _generate_llm(self, text: str, num_questions: int) -> List[QAPair]:
        _provider_key = settings.QA_LLM_PROVIDER or settings.LLM_PROVIDER
        logger.info("qa_llm_start", provider=_provider_key)
        provider_model = get_provider_model(_provider_key)
        client = LLMClient(
            provider=provider_model,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
            api_key=get_provider_api_key(_provider_key),
        )

        max_chars = 12000
        truncated = text[:max_chars] if len(text) > max_chars else text

        response = await client.complete(
            system="You are an expert at generating educational Q&A from academic content.",
            prompt=f"""Generate {num_questions} comprehensive Q&A pairs from this research paper.
Format strictly as:
Q: [question]
A: [answer]

Content:
{truncated}""",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=2000,
        )

        pairs = parse_qa_pairs(response)
        logger.info("qa_llm_complete", questions=len(pairs))
        return pairs
