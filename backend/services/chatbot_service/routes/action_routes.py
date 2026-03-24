"""
Chatbot Service — Action Routes

Endpoints for message feedback (like/dislike) from Section 13.4.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from services.chatbot_service.services.action_service import ActionService
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/chat/messages", tags=["Message Actions"])


@router.patch("/{message_id}/like")
@limiter.limit("30/minute")
async def like_message(
    request: Request,
    message_id: UUID,
    service: ActionService = Depends(),
):
    """Like an assistant message."""
    result = await service.set_feedback(message_id, "like")
    return success_response(result.model_dump(mode="json"))


@router.patch("/{message_id}/dislike")
@limiter.limit("30/minute")
async def dislike_message(
    request: Request,
    message_id: UUID,
    service: ActionService = Depends(),
):
    """Dislike an assistant message."""
    result = await service.set_feedback(message_id, "dislike")
    return success_response(result.model_dump(mode="json"))


@router.patch("/{message_id}/remove-feedback")
@limiter.limit("30/minute")
async def remove_feedback(
    request: Request,
    message_id: UUID,
    service: ActionService = Depends(),
):
    """Remove feedback from an assistant message."""
    result = await service.set_feedback(message_id, None)
    return success_response(result.model_dump(mode="json"))
