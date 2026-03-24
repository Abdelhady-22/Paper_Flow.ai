"""
OCR Service — API Routes

Endpoints for OCR extraction and paper upload.
Zero business logic — delegates to OCRService.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Query, Request
from services.ocr_service.services.ocr_service import OCRService
from shared.error_handler.responses import success_response
from shared.security.file_validator import FileValidator
from shared.rate_limiter.api_limiter import limiter

router = APIRouter(prefix="/ocr", tags=["OCR"])

file_validator = FileValidator()


@router.post("/extract")
@limiter.limit("5/minute")
async def extract_text(
    request: Request,
    file: UploadFile = File(...),
    engine: str = Query("paddle", description="OCR engine: paddle, mistral, lighton"),
    service: OCRService = Depends(),
):
    """
    Extract text from an uploaded file using OCR.
    Supports: PDF, DOCX, PNG, JPG, JPEG, TIFF, BMP.
    """
    file_bytes = await file_validator.validate(file, context="document")
    result = await service.extract_text_from_file(
        file_bytes, file.filename or "upload", engine
    )
    return success_response(
        {
            "text": result.text,
            "engine": result.engine,
            "page_count": result.page_count,
        }
    )


@router.post("/upload")
@limiter.limit("5/minute")
async def upload_paper(
    request: Request,
    file: UploadFile = File(...),
    user_id: UUID = Query(..., description="User ID"),
    engine: str = Query("paddle", description="OCR engine for fallback"),
    language: str = Query("en", description="Paper language: en, ar"),
    service: OCRService = Depends(),
):
    """
    Upload a paper, extract text (with OCR fallback), and save to database.
    Returns paper_id for use in other services.
    """
    result = await service.upload_and_process_paper(
        file=file, user_id=user_id, engine=engine, language=language
    )
    return success_response(result.model_dump())


@router.get("/papers")
@limiter.limit("30/minute")
async def list_papers(
    request: Request,
    user_id: UUID = Query(..., description="User ID"),
    service: OCRService = Depends(),
):
    """List all papers for a user."""
    papers = await service.paper_repo.get_papers_by_user(user_id)
    return success_response(
        [
            {
                "paper_id": str(p.id),
                "filename": p.filename,
                "status": p.status,
                "language": p.language,
                "source": p.source,
                "page_count": p.page_count,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in papers
        ]
    )


@router.get("/papers/{paper_id}/text")
@limiter.limit("30/minute")
async def get_paper_text(
    request: Request,
    paper_id: UUID,
    service: OCRService = Depends(),
):
    """Get extracted text for a specific paper."""
    from shared.error_handler.exceptions import PaperNotFoundException

    paper = await service.paper_repo.get_paper(paper_id)
    if not paper:
        raise PaperNotFoundException(paper_id)

    return success_response(
        {
            "paper_id": str(paper.id),
            "filename": paper.filename,
            "extracted_text": paper.extracted_text,
            "status": paper.status,
        }
    )
