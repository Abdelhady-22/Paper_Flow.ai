"""
Voice Service — Gemini STT & TTS Providers

Cloud-based voice services using Google Gemini API.
"""

import httpx
from services.voice_service.utils.provider_interface import STTProvider, TTSProvider
from services.voice_service.models.schemas import STTResponse
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import STTException, TTSException, MissingAPIKeyException
from settings import settings

logger = get_logger(__name__)


class GeminiSTT(STTProvider):
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> STTResponse:
        if not settings.GEMINI_API_KEY:
            raise MissingAPIKeyException("GEMINI_API_KEY is not configured.")
        try:
            import google.generativeai as genai
            import base64

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            audio_b64 = base64.b64encode(audio_bytes).decode()
            response = model.generate_content([
                {"mime_type": "audio/wav", "data": audio_b64},
                "Transcribe this audio accurately. Return only the text."
            ])
            return STTResponse(text=response.text.strip(), provider="gemini", language=language)
        except Exception as e:
            logger.error("gemini_stt_error", error=str(e))
            raise STTException("Gemini STT failed.")


class GeminiTTS(TTSProvider):
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Note: Gemini doesn't have native TTS — fallback to Edge-TTS."""
        from services.voice_service.utils.edge_tts_provider import EdgeTTSProvider
        fallback = EdgeTTSProvider()
        return await fallback.synthesize(text, language)
