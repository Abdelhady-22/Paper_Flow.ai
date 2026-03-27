"""
Translation Service — Pydantic Schemas
"""

from typing import Optional, Literal
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TranslateRequest(BaseModel):
    paper_id: UUID
    direction: Literal["en-ar", "ar-en"]
    mode: Literal["model", "llm"] = "model"


class TranslationResponse(BaseModel):
    content: str
    paper_id: UUID
    direction: str
    mode_used: str
    created_at: Optional[datetime] = None
