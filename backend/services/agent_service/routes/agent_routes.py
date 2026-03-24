"""
Agent Service — API Routes

Two endpoints:
- POST /agent/search → Quick Semantic Scholar search
- POST /agent/discover → Full CrewAI pipeline (keyword → search → download → import → report)
"""

from uuid import UUID
from fastapi import APIRouter, Query, Request
from services.agent_service.services.agent_service import AgentService
from services.agent_service.models.schemas import PaperSearchRequest, DiscoverRequest
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/agent", tags=["AI Agent"])
agent_service = AgentService()


@router.post("/search")
@limiter.limit("10/minute")
async def search_papers(request: Request, body: PaperSearchRequest):
    """Quick search — Semantic Scholar only, no download or import."""
    result = await agent_service.search_papers(
        query=body.query,
        max_results=body.max_results,
        fields=body.fields,
    )
    return success_response(result.model_dump())


@router.post("/discover")
@limiter.limit("5/minute")
async def discover_papers(
    request: Request,
    body: DiscoverRequest,
    user_id: UUID = Query(..., description="User ID"),
):
    """
    Full discovery pipeline:
    keyword_agent → search_agent → download_agent → import_agent → report_agent

    Returns a discovery report with:
    - Papers found on Semantic Scholar
    - Papers downloaded
    - Papers imported into knowledge base (Qdrant + PostgreSQL)
    - Structured report with ranked papers

    Progress is streamed via WebSocket at /ws/progress.
    """
    result = await agent_service.discover_and_import(
        query=body.query,
        user_id=str(user_id),
        max_papers=body.max_papers,
        auto_import=body.auto_import,
    )
    return success_response(result.model_dump())
