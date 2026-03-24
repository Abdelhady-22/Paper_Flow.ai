"""
Chatbot Service — Chat Routes

Endpoints for chat sessions, messages, and RAG-powered Q&A.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from services.chatbot_service.services.chat_service import ChatService
from services.chatbot_service.models.schemas import (
    ChatMessageRequest,
    CreateSessionRequest,
)
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/sessions")
@limiter.limit("30/minute")
async def create_session(
    request: Request,
    body: CreateSessionRequest,
    user_id: UUID = Query(..., description="User ID"),
    service: ChatService = Depends(),
):
    """Create a new chat session."""
    session = await service.chat_repo.create_session(
        user_id=user_id, title=body.title
    )
    return success_response({
        "session_id": str(session.id),
        "title": session.title,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    })


@router.get("/sessions")
@limiter.limit("30/minute")
async def list_sessions(
    request: Request,
    user_id: UUID = Query(..., description="User ID"),
    service: ChatService = Depends(),
):
    """List all chat sessions for a user."""
    sessions = await service.chat_repo.get_user_sessions(user_id)
    return success_response([
        {
            "session_id": str(s.id),
            "title": s.title,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ])


@router.post("/message")
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    body: ChatMessageRequest,
    user_id: UUID = Query(..., description="User ID"),
    service: ChatService = Depends(),
):
    """Send a message and receive RAG-powered response."""
    result = await service.send_message(
        content=body.content,
        session_id=body.session_id,
        user_id=user_id,
        input_type=body.input_type,
    )
    return success_response(result.model_dump(mode="json"))


@router.get("/sessions/{session_id}/messages")
@limiter.limit("30/minute")
async def get_messages(
    request: Request,
    session_id: UUID,
    service: ChatService = Depends(),
):
    """Get all messages in a chat session."""
    messages = await service.chat_repo.get_session_messages(session_id)
    return success_response([
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "citations": m.citations,
            "input_type": m.input_type,
            "feedback": m.feedback,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ])
