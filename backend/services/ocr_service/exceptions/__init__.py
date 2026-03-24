"""
OCR Service — Custom Exceptions
"""

from shared.error_handler.exceptions import (
    AppBaseException,
    OCRExtractionException,
    OCRTimeoutException,
    OCRProviderException,
    OCREngineNotFoundException,
)

__all__ = [
    "OCRExtractionException",
    "OCRTimeoutException",
    "OCRProviderException",
    "OCREngineNotFoundException",
]
