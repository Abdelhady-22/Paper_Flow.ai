"""
Q&A Service — Repository Layer
"""

from uuid import UUID
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import json
from infrastructure.postgres.database import get_db
from shared.models.domain import Paper, ToolResult
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class QARepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_paper_text(self, paper_id: UUID) -> Optional[str]:
        result = await self.session.execute(
            select(Paper.extracted_text).where(Paper.id == paper_id)
        )
        return result.scalar_one_or_none()

    async def save_result(
        self, paper_id: UUID, user_id: UUID, qa_pairs: list, mode: str
    ) -> ToolResult:
        content = json.dumps([{"q": qa.question, "a": qa.answer} for qa in qa_pairs])
        result = ToolResult(
            paper_id=paper_id,
            user_id=user_id,
            tool_type="qa",
            mode_used=mode,
            content=content,
        )
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        return result
