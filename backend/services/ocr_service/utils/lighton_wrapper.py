"""
OCR Service — LightOn OCR API Wrapper

Cloud API engine — requires LIGHTON_API_KEY.
Specialized for scientific and academic documents.
"""

import httpx
from settings import settings
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import (
    OCRExtractionException,
    OCRTimeoutException,
    MissingAPIKeyException,
)
from services.ocr_service.models.schemas import OCRResult
from services.ocr_service.utils.engine_interface import OCREngine

logger = get_logger(__name__)


class LightOnOCREngine(OCREngine):
    """LightOn OCR cloud API engine — academic paper focus."""

    BASE_URL = "https://api.lighton.ai/v1/ocr"

    def __init__(self):
        self.api_key = settings.LIGHTON_API_KEY
        if not self.api_key:
            raise MissingAPIKeyException("LIGHTON_API_KEY is not configured.")

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("lighton_ocr_start", filename=filename)

            async with httpx.AsyncClient(timeout=settings.OCR_API_TIMEOUT) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/octet-stream",
                    },
                    content=file,
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("result", {}).get("text", "")

                logger.info(
                    "lighton_ocr_complete",
                    filename=filename,
                    chars=len(text),
                )

                return OCRResult(text=text, engine="lighton")

        except httpx.TimeoutException:
            logger.error("lighton_ocr_timeout", filename=filename)
            raise OCRTimeoutException("LightOn OCR timed out.")
        except (OCRTimeoutException,):
            raise
        except Exception as e:
            logger.error("lighton_ocr_error", error=str(e))
            raise OCRExtractionException(
                "Text extraction via LightOn failed."
            )
