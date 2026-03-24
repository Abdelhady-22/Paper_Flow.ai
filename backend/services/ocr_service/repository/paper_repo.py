"""
OCR Service — Repository Layer

Database access for papers and OCR results.
Repository pattern — services never make direct DB queries.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from infrastructure.postgres.database import get_db
from shared.models.domain import Paper
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class PaperRepository:
    """Repository for paper CRUD operations."""

    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create_paper(
        self,
        user_id: UUID,
        filename: str,
        file_path: str,
        source: str = "upload",
        extracted_text: Optional[str] = None,
        page_count: Optional[int] = None,
        language: str = "en",
        status: str = "pending",
    ) -> Paper:
        """Create a new paper record."""
        paper = Paper(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            source=source,
            extracted_text=extracted_text,
            page_count=page_count,
            language=language,
            status=status,
        )
        self.session.add(paper)
        await self.session.commit()
        await self.session.refresh(paper)

        logger.info("paper_created", paper_id=str(paper.id), filename=filename)
        return paper

    async def get_paper(self, paper_id: UUID) -> Optional[Paper]:
        """Get a paper by ID."""
        result = await self.session.execute(
            select(Paper).where(Paper.id == paper_id)
        )
        return result.scalar_one_or_none()

    async def get_paper_text(self, paper_id: UUID) -> Optional[str]:
        """Get extracted text for a paper."""
        result = await self.session.execute(
            select(Paper.extracted_text).where(Paper.id == paper_id)
        )
        return result.scalar_one_or_none()

    async def update_paper_text(
        self,
        paper_id: UUID,
        extracted_text: str,
        page_count: Optional[int] = None,
        status: str = "processed",
    ) -> None:
        """Update paper with extracted text and set status."""
        values = {
            "extracted_text": extracted_text,
            "status": status,
        }
        if page_count is not None:
            values["page_count"] = page_count

        await self.session.execute(
            update(Paper).where(Paper.id == paper_id).values(**values)
        )
        await self.session.commit()

        logger.info(
            "paper_text_updated",
            paper_id=str(paper_id),
            chars=len(extracted_text),
            status=status,
        )

    async def update_paper_status(self, paper_id: UUID, status: str) -> None:
        """Update paper processing status."""
        await self.session.execute(
            update(Paper).where(Paper.id == paper_id).values(status=status)
        )
        await self.session.commit()

    async def get_papers_by_user(self, user_id: UUID) -> list[Paper]:
        """Get all papers for a user."""
        result = await self.session.execute(
            select(Paper).where(Paper.user_id == user_id).order_by(Paper.created_at.desc())
        )
        return list(result.scalars().all())
