"""
Voice Service — API Routes
"""

from fastapi import APIRouter, File, UploadFile, Query, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from services.voice_service.services.voice_service import VoiceService
from shared.security.file_validator import FileValidator
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/voice", tags=["Voice"])
file_validator = FileValidator()
voice_service = VoiceService()


@router.post("/stt")
@limiter.limit("20/minute")
async def speech_to_text(
    request: Request,
    file: UploadFile = File(...),
    provider: str = Query("whisper", description="STT provider: whisper, elevenlabs, gemini"),
    language: str = Query("en", description="Language: en, ar"),
):
    """Convert speech audio to text."""
    audio_bytes = await file_validator.validate(file, context="audio")
    result = await voice_service.speech_to_text(audio_bytes, provider, language)
    return success_response(result.model_dump())


@router.post("/tts")
@limiter.limit("20/minute")
async def text_to_speech(
    request: Request,
    text: str = Query(..., description="Text to convert to speech"),
    provider: str = Query("edge_tts", description="TTS provider: edge_tts, elevenlabs, gemini, speecht5"),
    language: str = Query("en", description="Language: en, ar"),
):
    """Convert text to speech audio."""
    audio_bytes, meta = await voice_service.text_to_speech(text, provider, language)
    return StreamingResponse(
        BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"X-TTS-Provider": meta.provider, "X-TTS-Cached": str(meta.cached)},
    )
