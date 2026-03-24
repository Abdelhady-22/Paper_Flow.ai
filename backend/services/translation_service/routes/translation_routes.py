"""
Translation Service — API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from services.translation_service.services.translation_service import TranslationService
from services.translation_service.models.schemas import TranslateRequest
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/translate", tags=["Translation"])


@router.post("/")
@limiter.limit("10/minute")
async def translate_paper(
    request: Request,
    body: TranslateRequest,
    user_id: UUID = Query(..., description="User ID"),
    service: TranslationService = Depends(),
):
    """Translate a paper between English and Arabic."""
    result = await service.translate(
        paper_id=body.paper_id,
        user_id=user_id,
        direction=body.direction,
        mode=body.mode,
    )
    return success_response(result.model_dump(mode="json"))
