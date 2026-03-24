"""
Voice Service — Provider Selector (Strategy + Factory Pattern)

Selects STT/TTS providers at runtime based on configuration.
"""

from services.voice_service.utils.provider_interface import STTProvider, TTSProvider
from services.voice_service.utils.whisper_stt import WhisperSTT
from services.voice_service.utils.edge_tts_provider import EdgeTTSProvider
from services.voice_service.utils.elevenlabs_provider import ElevenLabsSTT, ElevenLabsTTS
from services.voice_service.utils.gemini_provider import GeminiSTT, GeminiTTS
from services.voice_service.utils.speecht5_provider import SpeechT5Provider
from shared.error_handler.exceptions import InvalidProviderException


class VoiceProviderSelector:
    """Factory that returns the correct STT/TTS provider."""

    STT_PROVIDERS = {
        "whisper": WhisperSTT,
        "elevenlabs": ElevenLabsSTT,
        "gemini": GeminiSTT,
    }

    TTS_PROVIDERS = {
        "edge_tts": EdgeTTSProvider,
        "elevenlabs": ElevenLabsTTS,
        "gemini": GeminiTTS,
        "speecht5": SpeechT5Provider,
    }

    def get_stt(self, provider: str) -> STTProvider:
        cls = self.STT_PROVIDERS.get(provider)
        if not cls:
            raise InvalidProviderException(
                f"Unknown STT provider: '{provider}'. "
                f"Available: {', '.join(self.STT_PROVIDERS.keys())}"
            )
        return cls()

    def get_tts(self, provider: str) -> TTSProvider:
        cls = self.TTS_PROVIDERS.get(provider)
        if not cls:
            raise InvalidProviderException(
                f"Unknown TTS provider: '{provider}'. "
                f"Available: {', '.join(self.TTS_PROVIDERS.keys())}"
            )
        return cls()
