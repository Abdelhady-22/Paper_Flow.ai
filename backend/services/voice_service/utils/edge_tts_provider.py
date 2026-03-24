"""
Voice Service — Edge-TTS Provider

Free, high-quality text-to-speech using Microsoft Edge TTS.
Supports multiple languages and voice configurations.
"""

import edge_tts
import tempfile
import os
from services.voice_service.utils.provider_interface import TTSProvider
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import TTSException

logger = get_logger(__name__)

VOICE_MAP = {
    "en": "en-US-AriaNeural",
    "ar": "ar-SA-ZariyahNeural",
}


class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        try:
            voice = VOICE_MAP.get(language, VOICE_MAP["en"])
            communicate = edge_tts.Communicate(text, voice)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                await communicate.save(tmp_path)
                with open(tmp_path, "rb") as f:
                    audio_bytes = f.read()
                logger.info("edge_tts_complete", language=language, bytes=len(audio_bytes))
                return audio_bytes
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            logger.error("edge_tts_error", error=str(e))
            raise TTSException("Text-to-speech failed. Please try again.")
