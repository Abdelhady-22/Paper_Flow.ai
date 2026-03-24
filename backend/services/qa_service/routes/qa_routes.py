"""
Q&A Service — API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from services.qa_service.services.qa_service import QAService
from services.qa_service.models.schemas import QARequest
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/qa", tags=["Q&A Generation"])


@router.post("/generate")
@limiter.limit("10/minute")
async def generate_qa(
    request: Request,
    body: QARequest,
    user_id: UUID = Query(..., description="User ID"),
    service: QAService = Depends(),
):
    """Generate Q&A pairs from a paper."""
    result = await service.generate_qa(
        paper_id=body.paper_id,
        user_id=user_id,
        mode=body.mode,
        num_questions=body.num_questions,
    )
    return success_response(result.model_dump(mode="json"))
