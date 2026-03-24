"""
OCR Service — OCR Engine Abstract Interface and Implementations

Strategy pattern: each OCR engine implements the same abstract interface.
Engine selection happens at runtime via OCREngineSelector.

Engines:
- PaddleOCR (local, free, offline)
- Mistral OCR API (cloud, paid, high accuracy)
- LightOnOCR (cloud, paid, academic focus)
"""

from abc import ABC, abstractmethod
from services.ocr_service.models.schemas import OCRResult


class OCREngine(ABC):
    """Abstract interface for OCR engines — Strategy pattern."""

    @abstractmethod
    async def extract(self, file: bytes, filename: str) -> OCRResult:
        """Extract text from a file using this OCR engine."""
        ...
