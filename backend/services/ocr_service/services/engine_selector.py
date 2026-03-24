"""
OCR Service — Engine Selector (Strategy Pattern)

Selects the OCR engine at runtime based on configuration.
Implements the Factory + Strategy pattern from Section 11.1.
"""

from shared.error_handler.exceptions import OCREngineNotFoundException
from services.ocr_service.utils.engine_interface import OCREngine
from services.ocr_service.utils.paddle_wrapper import PaddleOCREngine
from services.ocr_service.utils.mistral_wrapper import MistralOCREngine
from services.ocr_service.utils.lighton_wrapper import LightOnOCREngine


class OCREngineSelector:
    """Factory that returns the correct OCR engine implementation."""

    def get_engine(self, engine: str) -> OCREngine:
        engines = {
            "paddle": PaddleOCREngine,
            "mistral": MistralOCREngine,
            "lighton": LightOnOCREngine,
        }
        engine_cls = engines.get(engine)
        if not engine_cls:
            raise OCREngineNotFoundException(
                f"Unknown OCR engine: '{engine}'. Available: {', '.join(engines.keys())}"
            )
        return engine_cls()
