"""
Summarization Service — Pydantic Schemas
"""

from typing import Optional, Literal
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SummarizeRequest(BaseModel):
    paper_id: UUID
    mode: Literal["model", "llm"] = "model"
    language: Literal["en", "ar"] = "en"


class SummaryResponse(BaseModel):
    content: str
    paper_id: UUID
    mode_used: str
    created_at: Optional[datetime] = None
