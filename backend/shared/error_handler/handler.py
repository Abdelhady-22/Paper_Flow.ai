"""
Shared — Global Exception Handlers

Registers exception handlers on FastAPI app to enforce the two-layer error strategy:
- AppBaseException → 400 with user-friendly message
- LLMRateLimitException → 429
- Unhandled Exception → 500 with generic message (never expose internals)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import (
    AppBaseException,
    LLMRateLimitException,
    LLMTimeoutException,
    OCRTimeoutException,
    STTTimeoutException,
    TTSTimeoutException,
    FileTooLargeException,
)

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(LLMRateLimitException)
    async def llm_rate_limit_handler(
        request: Request, exc: LLMRateLimitException
    ) -> JSONResponse:
        logger.warning(
            "llm_rate_limit_hit",
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=429,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(LLMTimeoutException)
    async def llm_timeout_handler(
        request: Request, exc: LLMTimeoutException
    ) -> JSONResponse:
        logger.error(
            "llm_timeout",
            path=request.url.path,
            internal_detail=exc.internal_detail,
        )
        return JSONResponse(
            status_code=504,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(OCRTimeoutException)
    async def ocr_timeout_handler(
        request: Request, exc: OCRTimeoutException
    ) -> JSONResponse:
        logger.error("ocr_timeout", path=request.url.path)
        return JSONResponse(
            status_code=504,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(STTTimeoutException)
    async def stt_timeout_handler(
        request: Request, exc: STTTimeoutException
    ) -> JSONResponse:
        logger.error("stt_timeout", path=request.url.path)
        return JSONResponse(
            status_code=504,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(TTSTimeoutException)
    async def tts_timeout_handler(
        request: Request, exc: TTSTimeoutException
    ) -> JSONResponse:
        logger.error("tts_timeout", path=request.url.path)
        return JSONResponse(
            status_code=504,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(FileTooLargeException)
    async def file_too_large_handler(
        request: Request, exc: FileTooLargeException
    ) -> JSONResponse:
        logger.warning("file_too_large", path=request.url.path)
        return JSONResponse(
            status_code=413,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(AppBaseException)
    async def app_exception_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        logger.error(
            "app_exception",
            path=request.url.path,
            user_message=exc.user_message,
            internal_detail=exc.internal_detail,
            exc_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=400,
            content={"error": exc.user_message, "success": False},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "unexpected_error",
            path=request.url.path,
            error=str(exc),
            exc_type=type(exc).__name__,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Something went wrong. Please try again.",
                "success": False,
            },
        )
