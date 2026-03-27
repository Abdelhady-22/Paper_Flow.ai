"""
OCR Service — Pydantic Schemas

Request/response schemas for OCR endpoints.
"""

from typing import Optional, Literal
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class OCRRequest(BaseModel):
    """Request schema for OCR extraction."""
    engine: Literal["paddle", "mistral", "lighton"] = "paddle"
    language: Literal["en", "ar"] = "en"


class OCRResult(BaseModel):
    """Result from an OCR engine."""
    text: str
    engine: str
    page_count: Optional[int] = None
    confidence: Optional[float] = None


class OCRResponse(BaseModel):
    """API response for OCR extraction."""
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None


class PaperUploadResponse(BaseModel):
    """Response after uploading and processing a paper."""
    paper_id: str
    filename: str
    status: str
    extracted_text: Optional[str] = None
    page_count: Optional[int] = None
    source: str = "upload"
