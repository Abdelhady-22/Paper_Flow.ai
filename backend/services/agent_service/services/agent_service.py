"""
Agent Service — Full Agent Service

Combines simple search with the full CrewAI discovery pipeline.
"""

from services.agent_service.models.schemas import (
    DiscoveredPaper,
    DiscoveryResponse,
    DiscoveryReport,
)
from services.agent_service.utils.semantic_scholar import search_papers
from services.agent_service.services.orchestrator import AgentOrchestrator
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import AgentException

logger = get_logger(__name__)

orchestrator = AgentOrchestrator()


class AgentService:
    """
    AI-powered paper discovery and import service.

    Two modes:
    - search: Quick Semantic Scholar search (no download/import)
    - discover: Full pipeline (keyword → search → download → import → report)
    """

    async def search_papers(
        self, query: str, max_results: int = 5, fields: list = None
    ) -> DiscoveryResponse:
        """Quick search — Semantic Scholar only, no download or import."""
        try:
            papers = await search_papers(
                query=query, max_results=max_results, fields=fields
            )
            return DiscoveryResponse(
                papers=papers, query=query, total_found=len(papers)
            )
        except Exception as e:
            logger.error("agent_search_error", query=query, error=str(e))
            raise AgentException("Paper search failed. Please try a different query.")

    async def discover_and_import(
        self, query: str, user_id: str, max_papers: int = 5, auto_import: bool = True
    ) -> DiscoveryReport:
        """
        Full discovery pipeline:
        keyword_agent → search_agent → download_agent → import_agent → report_agent
        """
        try:
            return await orchestrator.run_discovery(
                query=query,
                user_id=user_id,
                max_papers=max_papers,
                auto_import=auto_import,
            )
        except Exception as e:
            logger.error("agent_discovery_error", query=query, error=str(e))
            raise AgentException("Paper discovery pipeline failed. Please try again.")
