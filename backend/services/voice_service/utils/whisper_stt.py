"""
Voice Service — Faster Whisper STT Provider

Local speech-to-text using faster-whisper (CTranslate2).
"""

import tempfile
import os
from services.voice_service.utils.provider_interface import STTProvider
from services.voice_service.models.schemas import STTResponse
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import STTException

logger = get_logger(__name__)
_whisper_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        logger.info("loading_whisper_model")
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("whisper_model_loaded")
    return _whisper_model


class WhisperSTT(STTProvider):
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> STTResponse:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                model = _get_whisper()
                segments, info = model.transcribe(tmp_path, language=language)
                text = " ".join(seg.text for seg in segments)
                return STTResponse(text=text.strip(), provider="whisper", language=language)
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            logger.error("whisper_stt_error", error=str(e))
            raise STTException("Voice transcription failed. Please try again.")
