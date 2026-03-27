"""
Q&A Service — Pydantic Schemas
"""

from typing import Optional, Literal, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class QAPair(BaseModel):
    question: str
    answer: str


class QARequest(BaseModel):
    paper_id: UUID
    mode: Literal["model", "llm"] = "model"
    num_questions: int = 10


class QAResponse(BaseModel):
    qa_pairs: List[QAPair]
    paper_id: UUID
    mode_used: str
    total_questions: int
    created_at: Optional[datetime] = None
