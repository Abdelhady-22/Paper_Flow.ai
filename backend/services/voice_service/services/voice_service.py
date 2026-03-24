"""
Voice Service — Business Logic

Orchestrates STT and TTS using provider selector pattern.
Includes Redis caching for TTS audio responses.
"""

import hashlib
from services.voice_service.utils.provider_selector import VoiceProviderSelector
from services.voice_service.models.schemas import STTResponse, TTSResponse
from shared.security.file_validator import FileValidator
from shared.logger.logger import get_logger
from settings import settings
from infrastructure.redis.client import get_redis_binary_client

logger = get_logger(__name__)
provider_selector = VoiceProviderSelector()
file_validator = FileValidator()


class VoiceService:
    async def speech_to_text(
        self, audio_bytes: bytes, provider: str = None, language: str = "en"
    ) -> STTResponse:
        provider_name = provider or settings.STT_PROVIDER
        stt = provider_selector.get_stt(provider_name)
        result = await stt.transcribe(audio_bytes, language)
        logger.info("stt_complete", provider=provider_name, language=language, chars=len(result.text))
        return result

    async def text_to_speech(
        self, text: str, provider: str = None, language: str = "en"
    ) -> tuple[bytes, TTSResponse]:
        provider_name = provider or settings.TTS_PROVIDER

        # Check Redis cache
        text_hash = hashlib.md5(f"{text}:{language}:{provider_name}".encode()).hexdigest()
        cache_key = f"tts:{text_hash}"
        redis = get_redis_binary_client()
        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.debug("tts_cache_hit", cache_key=cache_key)
                meta = TTSResponse(provider=provider_name, language=language, cached=True)
                return cached, meta
        except Exception:
            pass
        finally:
            await redis.close()

        # Generate TTS
        tts = provider_selector.get_tts(provider_name)
        audio_bytes = await tts.synthesize(text, language)

        # Cache (12h)
        redis = get_redis_binary_client()
        try:
            await redis.setex(cache_key, 43200, audio_bytes)
        except Exception:
            pass
        finally:
            await redis.close()

        meta = TTSResponse(provider=provider_name, language=language)
        logger.info("tts_complete", provider=provider_name, language=language, bytes=len(audio_bytes))
        return audio_bytes, meta
