"""
Summarization Service — API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from services.summarization_service.services.summary_service import SummarizationService
from services.summarization_service.models.schemas import SummarizeRequest
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/summarize", tags=["Summarization"])


@router.post("/")
@limiter.limit("10/minute")
async def summarize_paper(
    request: Request,
    body: SummarizeRequest,
    user_id: UUID = Query(..., description="User ID"),
    service: SummarizationService = Depends(),
):
    """Summarize a paper using model or LLM mode."""
    result = await service.summarize(
        paper_id=body.paper_id,
        user_id=user_id,
        mode=body.mode,
    )
    return success_response(result.model_dump(mode="json"))
