"""
Export Service — API Routes
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from services.export_service.models.schemas import ExportRequest
from services.export_service.services.export_service import ExportService
from shared.error_handler.responses import success_response
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/export", tags=["Export"])
export_service = ExportService()


@router.post("/")
@limiter.limit("10/minute")
async def export_content(request: Request, body: ExportRequest):
    """Export content as TXT, DOCX, or PDF."""
    content_bytes, content_type, filename = await export_service.export(body)
    return StreamingResponse(
        BytesIO(content_bytes),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
