"""
OCR Service — Mistral OCR API Wrapper

Cloud API engine — requires MISTRAL_API_KEY.
High accuracy for complex document layouts.
"""

import httpx
from settings import settings
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import (
    OCRExtractionException,
    OCRTimeoutException,
    OCRProviderException,
    MissingAPIKeyException,
)
from services.ocr_service.models.schemas import OCRResult
from services.ocr_service.utils.engine_interface import OCREngine

logger = get_logger(__name__)


class MistralOCREngine(OCREngine):
    """Mistral OCR cloud API engine."""

    BASE_URL = "https://api.mistral.ai/v1/ocr"

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        if not self.api_key:
            raise MissingAPIKeyException("MISTRAL_API_KEY is not configured.")

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("mistral_ocr_start", filename=filename)

            async with httpx.AsyncClient(timeout=settings.OCR_API_TIMEOUT) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files={"file": (filename, file, "application/octet-stream")},
                    data={"model": "mistral-ocr-latest"},
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("text", "")

                logger.info(
                    "mistral_ocr_complete",
                    filename=filename,
                    chars=len(text),
                )

                return OCRResult(text=text, engine="mistral")

        except httpx.TimeoutException:
            logger.error("mistral_ocr_timeout", filename=filename)
            raise OCRTimeoutException(
                "Mistral OCR timed out. Try a smaller file or use local OCR."
            )
        except httpx.HTTPStatusError as e:
            logger.error("mistral_ocr_http_error", status=e.response.status_code)
            raise OCRProviderException(
                "Mistral OCR API returned an error. Please try again."
            )
        except (OCRTimeoutException, OCRProviderException):
            raise
        except Exception as e:
            logger.error("mistral_ocr_error", error=str(e))
            raise OCRExtractionException(
                "Text extraction via Mistral failed."
            )
