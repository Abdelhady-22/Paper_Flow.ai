"""
Chatbot Service — Action Service

Handles message feedback (like/dislike) actions from Section 13.5.
"""

from uuid import UUID
from typing import Optional
from fastapi import Depends
from services.chatbot_service.repository.chat_repo import ChatRepository
from services.chatbot_service.models.schemas import MessageFeedbackResponse
from shared.error_handler.exceptions import (
    MessageNotFoundException,
    InvalidFeedbackTargetException,
)
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class ActionService:
    """Handles message feedback actions."""

    def __init__(self, chat_repo: ChatRepository = Depends()):
        self.chat_repo = chat_repo

    async def set_feedback(
        self, message_id: UUID, feedback: Optional[str]
    ) -> MessageFeedbackResponse:
        message = await self.chat_repo.get_message(message_id)
        if not message:
            raise MessageNotFoundException(message_id)
        if message.role != "assistant":
            raise InvalidFeedbackTargetException(
                "Feedback can only be given on assistant messages."
            )

        await self.chat_repo.update_feedback(message_id, feedback)
        logger.info("message_feedback", message_id=str(message_id), feedback=feedback)
        return MessageFeedbackResponse(message_id=message_id, feedback=feedback)
