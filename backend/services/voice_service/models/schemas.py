"""
Voice Service — Pydantic Schemas
"""

from typing import Optional, Literal
from pydantic import BaseModel


class STTResponse(BaseModel):
    text: str
    provider: str
    language: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: Optional[str] = None
    provider: str
    language: str
    cached: bool = False
