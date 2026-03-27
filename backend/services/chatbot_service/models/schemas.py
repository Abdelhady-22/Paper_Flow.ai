"""
Chatbot Service — Pydantic Schemas

Schemas for chat messages, sessions, citations, and feedback.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ChatMessageRequest(BaseModel):
    content: str
    session_id: UUID
    input_type: Literal["text", "voice"] = "text"


class Citation(BaseModel):
    paper_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    text_snippet: str


class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    input_type: str = "text"
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageFeedbackResponse(BaseModel):
    message_id: UUID
    feedback: Optional[str] = None
