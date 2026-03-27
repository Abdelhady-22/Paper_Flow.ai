"""
Tests for shared utility modules:
- filename_sanitizer
- text_chunker (mocked)
- exceptions
"""

import pytest
from shared.security.filename_sanitizer import sanitize_filename
from shared.error_handler.exceptions import (
    AppBaseException,
    LLMServiceException,
    PaperNotFoundException,
    SessionNotFoundException,
    FileTooLargeException,
)


# ═══════════════════════════════════════════════════════════════════════
# Filename Sanitizer Tests
# ═══════════════════════════════════════════════════════════════════════

class TestFilenameSanitizer:
    """Tests for the filename sanitizer security utility."""

    def test_normal_filename(self):
        assert sanitize_filename("paper.pdf") == "paper.pdf"

    def test_preserves_extension(self):
        result = sanitize_filename("my_document.docx")
        assert result.endswith(".docx")

    def test_strips_directory_traversal(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_replaces_special_characters(self):
        result = sanitize_filename("file <with> special|chars?.pdf")
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert "?" not in result
        assert result.endswith(".pdf")

    def test_removes_leading_dots(self):
        result = sanitize_filename(".hidden_file.pdf")
        assert not result.startswith(".")

    def test_truncates_long_filename(self):
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_handles_empty_filename(self):
        result = sanitize_filename("")
        assert result  # Should not be empty

    def test_handles_only_dots(self):
        result = sanitize_filename("...")
        assert result  # Should not be empty
        assert not result.startswith(".")

    def test_unicode_characters(self):
        # Arabic/Unicode characters should be replaced
        result = sanitize_filename("ملف_بحثي.pdf")
        assert result.endswith(".pdf")

    def test_windows_path_traversal(self):
        result = sanitize_filename("C:\\Windows\\System32\\config.pdf")
        assert ":" not in result
        assert "\\" not in result


# ═══════════════════════════════════════════════════════════════════════
# Exception Hierarchy Tests
# ═══════════════════════════════════════════════════════════════════════

class TestExceptionHierarchy:
    """Tests for the custom exception system."""

    def test_base_exception_user_message(self):
        exc = AppBaseException("User-facing message", "Internal detail")
        assert exc.user_message == "User-facing message"
        assert exc.internal_detail == "Internal detail"

    def test_base_exception_str_uses_internal(self):
        exc = AppBaseException("User msg", "Internal detail")
        assert str(exc) == "Internal detail"

    def test_base_exception_str_fallback_to_user_msg(self):
        exc = AppBaseException("User msg")
        assert str(exc) == "User msg"

    def test_llm_exception_is_app_exception(self):
        exc = LLMServiceException("Service unavailable")
        assert isinstance(exc, AppBaseException)

    def test_paper_not_found_exception(self):
        exc = PaperNotFoundException("paper-123")
        assert exc.user_message == "Paper not found."
        assert "paper-123" in exc.internal_detail

    def test_session_not_found_exception(self):
        exc = SessionNotFoundException("session-456")
        assert exc.user_message == "Chat session not found."
        assert "session-456" in exc.internal_detail

    def test_file_too_large_exception(self):
        exc = FileTooLargeException("File is too large")
        assert isinstance(exc, AppBaseException)


# ═══════════════════════════════════════════════════════════════════════
# Settings Tests
# ═══════════════════════════════════════════════════════════════════════

class TestSettings:
    """Tests for application settings configuration."""

    def test_settings_loads(self):
        from settings import Settings
        s = Settings()
        assert s.LLM_PROVIDER == "groq"

    def test_cors_origins_list(self):
        from settings import Settings
        s = Settings()
        origins = s.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) >= 1

    def test_default_values(self):
        from settings import Settings
        s = Settings()
        assert s.QDRANT_PORT == 6333
        assert s.LLM_TIMEOUT == 30
        assert s.LLM_MAX_RETRIES == 3
