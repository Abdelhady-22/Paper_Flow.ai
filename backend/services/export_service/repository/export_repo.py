"""
Export Service — Repository Layer 

Database access for tool results when exporting.
"""

from uuid import UUID
from sqlalchemy import select
from infrastructure.postgres.database import AsyncSessionFactory
from shared.models.domain import ToolResult
from shared.error_handler.exceptions import ExportException
from shared.logger.logger import get_logger

logger = get_logger(__name__)


class ExportRepository:
    """Repository for fetching tool results for export."""

    async def get_tool_result(self, result_id: UUID) -> ToolResult:
        """Fetch a tool result by ID."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(ToolResult).where(ToolResult.id == result_id)
            )
            tool_result = result.scalar_one_or_none()
            if not tool_result:
                raise ExportException("Result not found. Cannot export.")
            return tool_result

    async def get_tool_result_by_paper(
        self, paper_id: UUID, tool_type: str
    ) -> ToolResult:
        """Fetch a tool result by paper ID and tool type."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(ToolResult).where(
                    ToolResult.paper_id == paper_id,
                    ToolResult.tool_type == tool_type,
                ).order_by(ToolResult.created_at.desc())
            )
            tool_result = result.scalars().first()
            if not tool_result:
                raise ExportException(
                    f"No {tool_type} result found for this paper."
                )
            return tool_result
