"""
Voice Service — Repository Layer (Section 6)

Database access for voice session logging.
"""

from uuid import UUID
from infrastructure.postgres.database import AsyncSessionFactory
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class VoiceRepository:
    """Repository for voice session data access."""

    async def log_stt_usage(
        self, user_id: UUID, provider: str, language: str, text_length: int
    ) -> None:
        """Log STT transcription usage (for analytics)."""
        logger.info(
            "stt_usage_logged",
            user_id=str(user_id),
            provider=provider,
            language=language,
            text_length=text_length,
        )

    async def log_tts_usage(
        self, user_id: UUID, provider: str, language: str, audio_bytes: int
    ) -> None:
        """Log TTS synthesis usage (for analytics)."""
        logger.info(
            "tts_usage_logged",
            user_id=str(user_id),
            provider=provider,
            language=language,
            audio_bytes=audio_bytes,
        )
