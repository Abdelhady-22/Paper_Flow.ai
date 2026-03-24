"""
Chatbot Service — Repository Layer

Database access for chat sessions and messages.
"""

from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from infrastructure.postgres.database import get_db
from shared.models.domain import ChatSession, ChatMessage
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class ChatRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    # ── Sessions ──────────────────────────────────────────────
    async def create_session(self, user_id: UUID, title: Optional[str] = None) -> ChatSession:
        chat_session = ChatSession(user_id=user_id, title=title)
        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)
        return chat_session

    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        result = await self.session.execute(
            select(ChatSession).where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    # ── Messages ──────────────────────────────────────────────
    async def add_message(
        self, session_id: UUID, role: str, content: str,
        citations: Optional[list] = None, input_type: str = "text"
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations or [],
            input_type=input_type,
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_message(self, message_id: UUID) -> Optional[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def update_feedback(self, message_id: UUID, feedback: Optional[str]) -> ChatMessage:
        await self.session.execute(
            update(ChatMessage).where(ChatMessage.id == message_id)
            .values(feedback=feedback)
        )
        await self.session.commit()
        result = await self.get_message(message_id)
        return result
