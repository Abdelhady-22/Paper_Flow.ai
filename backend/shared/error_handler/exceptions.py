"""
Shared — Custom Exception Hierarchy

Two-layer error strategy:
1. Internal: Logged with full technical detail (stack traces, IDs)
2. External: Users only see clean, friendly messages

Every custom exception extends AppBaseException with user_message and internal_detail.
"""


class AppBaseException(Exception):
    """Base class for all application exceptions."""

    def __init__(self, user_message: str, internal_detail: str = ""):
        self.user_message = user_message
        self.internal_detail = internal_detail
        super().__init__(internal_detail or user_message)


# ── LLM Exceptions ────────────────────────────────────────────────────
class LLMServiceException(AppBaseException):
    pass


class LLMRateLimitException(AppBaseException):
    pass


class LLMTimeoutException(AppBaseException):
    pass


class LLMAuthException(AppBaseException):
    pass


# ── OCR Exceptions ────────────────────────────────────────────────────
class OCRExtractionException(AppBaseException):
    pass


class OCRTimeoutException(AppBaseException):
    pass


class OCRProviderException(AppBaseException):
    pass


class OCREngineNotFoundException(AppBaseException):
    pass


# ── Voice Exceptions ──────────────────────────────────────────────────
class STTException(AppBaseException):
    pass


class STTTimeoutException(AppBaseException):
    pass


class TTSException(AppBaseException):
    pass


class TTSTimeoutException(AppBaseException):
    pass


class InvalidProviderException(AppBaseException):
    pass


# ── Data Exceptions ───────────────────────────────────────────────────
class PaperNotFoundException(AppBaseException):
    def __init__(self, paper_id):
        super().__init__(
            user_message="Paper not found.",
            internal_detail=f"Paper with ID {paper_id} does not exist.",
        )


class MessageNotFoundException(AppBaseException):
    def __init__(self, message_id):
        super().__init__(
            user_message="Message not found.",
            internal_detail=f"Message {message_id} not found.",
        )


class SessionNotFoundException(AppBaseException):
    def __init__(self, session_id):
        super().__init__(
            user_message="Chat session not found.",
            internal_detail=f"Session {session_id} not found.",
        )


class InvalidFeedbackTargetException(AppBaseException):
    pass


class InvalidModeException(AppBaseException):
    pass


class MissingAPIKeyException(AppBaseException):
    pass


# ── Export Exceptions ─────────────────────────────────────────────────
class ExportException(AppBaseException):
    pass


class UnsupportedFormatException(AppBaseException):
    pass


# ── File Security Exceptions ─────────────────────────────────────────
class FileTooLargeException(AppBaseException):
    pass


class UnsupportedFileTypeException(AppBaseException):
    pass


class CorruptedFileException(AppBaseException):
    pass


class SuspiciousFileException(AppBaseException):
    pass


# ── Agent Exceptions ──────────────────────────────────────────────────
class AgentException(AppBaseException):
    pass


class PaperDiscoveryException(AppBaseException):
    pass
