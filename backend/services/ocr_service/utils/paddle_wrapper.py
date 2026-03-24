"""
OCR Service — PaddleOCR Engine Wrapper

Local OCR engine — no API key required, runs fully offline.
Supported formats: PNG, JPG, JPEG, TIFF, BMP, scanned PDF pages.
"""

import tempfile
import os
from paddleocr import PaddleOCR
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import OCRExtractionException
from services.ocr_service.models.schemas import OCRResult
from services.ocr_service.utils.engine_interface import OCREngine

logger = get_logger(__name__)

# Lazy-loaded PaddleOCR instance
_paddle_instance = None


def _get_paddle():
    global _paddle_instance
    if _paddle_instance is None:
        logger.info("paddle_ocr_loading")
        _paddle_instance = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        logger.info("paddle_ocr_loaded")
    return _paddle_instance


class PaddleOCREngine(OCREngine):
    """PaddleOCR local engine — free, offline."""

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("paddle_ocr_start", filename=filename)

            # Write to temp file for PaddleOCR
            suffix = os.path.splitext(filename)[1] or ".png"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(file)
                tmp_path = tmp.name

            try:
                ocr = _get_paddle()
                result = ocr.ocr(tmp_path, cls=True)

                if result is None:
                    text = ""
                    page_count = 0
                else:
                    lines = []
                    for block in result:
                        if block:
                            for line in block:
                                if line and len(line) > 1:
                                    lines.append(line[1][0])
                    text = "\n".join(lines)
                    page_count = len(result)

                logger.info(
                    "paddle_ocr_complete",
                    filename=filename,
                    chars=len(text),
                    pages=page_count,
                )

                return OCRResult(
                    text=text,
                    engine="paddle",
                    page_count=page_count,
                )

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            logger.error("paddle_ocr_error", filename=filename, error=str(e))
            raise OCRExtractionException(
                "Text extraction failed. Please try a different file or OCR engine."
            )
