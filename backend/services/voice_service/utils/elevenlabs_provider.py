"""
Voice Service — ElevenLabs STT & TTS Providers

Cloud-based voice services requiring ELEVENLABS_API_KEY.
"""

import httpx
from services.voice_service.utils.provider_interface import STTProvider, TTSProvider
from services.voice_service.models.schemas import STTResponse
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import STTException, TTSException, MissingAPIKeyException
from settings import settings

logger = get_logger(__name__)


class ElevenLabsSTT(STTProvider):
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> STTResponse:
        if not settings.ELEVENLABS_API_KEY:
            raise MissingAPIKeyException("ELEVENLABS_API_KEY is not configured.")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.elevenlabs.io/v1/speech-to-text",
                    headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                    files={"file": ("audio.wav", audio_bytes, "audio/wav")},
                )
                response.raise_for_status()
                data = response.json()
                return STTResponse(
                    text=data.get("text", ""),
                    provider="elevenlabs",
                    language=language,
                )
        except Exception as e:
            logger.error("elevenlabs_stt_error", error=str(e))
            raise STTException("ElevenLabs transcription failed.")


class ElevenLabsTTS(TTSProvider):
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        if not settings.ELEVENLABS_API_KEY:
            raise MissingAPIKeyException("ELEVENLABS_API_KEY is not configured.")
        try:
            voice_id = (
                settings.ELEVENLABS_STT_VOICE_AR if language == "ar"
                else settings.ELEVENLABS_TTS_VOICE_EN or "21m00Tcm4TlvDq8ikWAM"
            )
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
                    json={"text": text, "model_id": "eleven_multilingual_v2"},
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error("elevenlabs_tts_error", error=str(e))
            raise TTSException("ElevenLabs TTS failed.")
