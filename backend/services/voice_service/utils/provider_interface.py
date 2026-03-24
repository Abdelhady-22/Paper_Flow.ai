"""
Voice Service — STT/TTS Abstract Interfaces & Implementations

Strategy pattern: each provider implements the same interface.
Provider selection happens at runtime via VoiceProviderSelector.
"""

from abc import ABC, abstractmethod
from services.voice_service.models.schemas import STTResponse, TTSResponse


class STTProvider(ABC):
    """Abstract interface for Speech-to-Text providers."""
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> STTResponse: ...


class TTSProvider(ABC):
    """Abstract interface for Text-to-Speech providers."""
    @abstractmethod
    async def synthesize(self, text: str, language: str = "en") -> bytes: ...
