"""
Translation Service — Business Logic

Supports:
- Model mode: Helsinki-NLP/opus-mt-en-ar and opus-mt-ar-en (MarianNMT)
- LLM mode: Any LiteLLM provider

Includes Redis caching with 48h TTL.
"""

from uuid import UUID
from typing import Optional
from fastapi import Depends
from services.translation_service.repository.translation_repo import TranslationRepository
from services.translation_service.models.schemas import TranslationResponse
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

# Lazy-loaded translation models
_models = {}


def _get_translation_model(direction: str):
    if direction not in _models:
        model_map = {
            "en-ar": "Helsinki-NLP/opus-mt-en-ar",
            "ar-en": "Helsinki-NLP/opus-mt-ar-en",
        }
        model_name = model_map[direction]
        logger.info("loading_translation_model", model=model_name, direction=direction)
        from transformers import MarianTokenizer, MarianMTModel

        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        _models[direction] = (tokenizer, model)
        logger.info("translation_model_loaded", model=model_name)
    return _models[direction]


class TranslationService:
    def __init__(self, repo: TranslationRepository = Depends()):
        self.repo = repo

    async def translate(
        self, paper_id: UUID, user_id: UUID, direction: str, mode: Optional[str] = None
    ) -> TranslationResponse:
        mode_key = f"translation_{direction.replace('-', '_')}"
        resolved_mode = mode_selector.get_strategy(mode_key, mode)

        # Check Redis cache
        redis = get_redis_client()
        cache_key = f"trans:{direction}:{paper_id}:{resolved_mode}"
        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.debug("cache_hit", key=cache_key)
                return TranslationResponse(
                    content=cached, paper_id=paper_id,
                    direction=direction, mode_used=resolved_mode,
                )
        except Exception:
            pass
        finally:
            await redis.close()

        text = await self.repo.get_paper_text(paper_id)
        if not text:
            raise PaperNotFoundException(paper_id)

        if resolved_mode == "model":
            translation = await self._translate_model(text, direction)
        else:
            translation = await self._translate_llm(text, direction)

        result = await self.repo.save_result(
            paper_id=paper_id, user_id=user_id,
            content=translation, mode=resolved_mode, direction=direction,
        )

        # Cache (48h TTL)
        redis = get_redis_client()
        try:
            await redis.setex(cache_key, 172800, translation)
        except Exception:
            pass
        finally:
            await redis.close()

        return TranslationResponse(
            content=translation, paper_id=paper_id,
            direction=direction, mode_used=resolved_mode,
            created_at=result.created_at,
        )

    async def _translate_model(self, text: str, direction: str) -> str:
        logger.info("translate_model_start", direction=direction)
        tokenizer, model = _get_translation_model(direction)

        chunks = chunk_text(text, chunk_size=400)
        translated_parts = []

        for chunk in chunks:
            tokens = tokenizer([chunk], return_tensors="pt", padding=True, truncation=True, max_length=512)
            translated = model.generate(**tokens)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            translated_parts.append(translated_text)

        result = "\n\n".join(translated_parts)
        logger.info("translate_model_complete", direction=direction, chunks=len(chunks))
        return result

    async def _translate_llm(self, text: str, direction: str) -> str:
        _provider_key = settings.TRANSLATION_LLM_PROVIDER or settings.LLM_PROVIDER
        logger.info("translate_llm_start", direction=direction, provider=_provider_key)
        target = {"en-ar": "Arabic", "ar-en": "English"}[direction]
        provider_model = get_provider_model(_provider_key)
        client = LLMClient(
            provider=provider_model,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
            api_key=get_provider_api_key(_provider_key),
        )

        max_chars = 12000
        truncated = text[:max_chars] if len(text) > max_chars else text

        translation = await client.complete(
            system=f"You are an expert scientific translator. Translate accurately to {target}. "
                   f"Preserve all technical terms and formatting.",
            prompt=f"Translate this research paper text to {target}. "
                   f"Preserve all technical terms.\n\n{truncated}",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info("translate_llm_complete", direction=direction)
        return translation
