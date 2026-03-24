"""
OCR Service — Business Logic Layer

Orchestrates OCR extraction: validates files, selects engine, extracts text,
stores results. Uses file parser for PDF/DOCX text extraction with OCR fallback.
"""

from uuid import UUID
from typing import Optional
from fastapi import Depends, UploadFile
from services.ocr_service.services.engine_selector import OCREngineSelector
from services.ocr_service.repository.paper_repo import PaperRepository
from services.ocr_service.utils.file_parser import extract_text
from services.ocr_service.models.schemas import OCRResult, PaperUploadResponse
from shared.security.file_validator import FileValidator
from shared.storage.file_storage import store_file
from shared.logger.logger import get_logger
from settings import settings

logger = get_logger(__name__)

file_validator = FileValidator()
engine_selector = OCREngineSelector()


class OCRService:
    """Business logic for OCR and paper ingestion."""

    def __init__(self, paper_repo: PaperRepository = Depends()):
        self.paper_repo = paper_repo

    async def extract_text_from_file(
        self, file_bytes: bytes, filename: str, engine: str = "paddle"
    ) -> OCRResult:
        """
        Extract text from a file using the specified OCR engine.
        Used for direct OCR requests (not full paper upload).
        """
        ocr_engine = engine_selector.get_engine(engine)
        return await ocr_engine.extract(file_bytes, filename)

    async def upload_and_process_paper(
        self,
        file: UploadFile,
        user_id: UUID,
        engine: str = "paddle",
        language: str = "en",
    ) -> PaperUploadResponse:
        """
        Full paper upload pipeline:
        1. Validate file
        2. Store file securely (UUID path)
        3. Try text extraction (PDF/DOCX)
        4. If no text, fall back to OCR
        5. Save paper record to PostgreSQL
        """
        # Step 1: Validate
        file_bytes = await file_validator.validate(file, context="document")

        # Step 2: Store securely
        storage_info = await store_file(
            content=file_bytes,
            original_filename=file.filename or "upload",
            user_id=str(user_id),
            base_dir=settings.UPLOAD_DIR,
        )

        # Step 3: Try direct text extraction
        extracted_text = await extract_text(
            file_bytes, file.filename or "upload"
        )

        page_count = None

        # Step 4: If no text, OCR fallback
        if not extracted_text:
            logger.info(
                "ocr_fallback",
                filename=file.filename,
                engine=engine,
            )
            ocr_result = await self.extract_text_from_file(
                file_bytes, file.filename or "upload", engine
            )
            extracted_text = ocr_result.text
            page_count = ocr_result.page_count

        # Step 5: Save paper to database
        status = "processed" if extracted_text else "failed"

        paper = await self.paper_repo.create_paper(
            user_id=user_id,
            filename=storage_info["original_filename"],
            file_path=storage_info["storage_path"],
            source="upload",
            extracted_text=extracted_text,
            page_count=page_count,
            language=language,
            status=status,
        )

        logger.info(
            "paper_upload_complete",
            paper_id=str(paper.id),
            filename=file.filename,
            status=status,
            chars=len(extracted_text) if extracted_text else 0,
        )

        return PaperUploadResponse(
            paper_id=str(paper.id),
            filename=storage_info["original_filename"],
            status=status,
            extracted_text=extracted_text,
            page_count=page_count,
        )
