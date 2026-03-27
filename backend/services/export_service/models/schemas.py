"""
Export Service — Pydantic Schemas
"""

from typing import Optional, Literal
from pydantic import BaseModel
from uuid import UUID


class ExportRequest(BaseModel):
    content: str
    format: Literal["txt", "docx", "pdf"]
    title: Optional[str] = "Research Paper Assistant Export"
    language: str = "en"


class ExportResponse(BaseModel):
    filename: str
    format: str
    size_bytes: int
