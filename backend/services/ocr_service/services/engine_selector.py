"""
OCR Service — Engine Selector (Strategy Pattern)

Selects the OCR engine at runtime based on configuration.
Uses lazy imports so the gateway can start even if a specific
engine's dependencies (e.g. PaddleOCR/OpenCV) are missing.
"""

from shared.error_handler.exceptions import OCREngineNotFoundException


class OCREngineSelector:
    """Factory that returns the correct OCR engine implementation."""

    def get_engine(self, engine: str):
        if engine == "paddle":
            from services.ocr_service.utils.paddle_wrapper import PaddleOCREngine
            return PaddleOCREngine()
        elif engine == "mistral":
            from services.ocr_service.utils.mistral_wrapper import MistralOCREngine
            return MistralOCREngine()
        elif engine == "lighton":
            from services.ocr_service.utils.lighton_wrapper import LightOnOCREngine
            return LightOnOCREngine()
        elif engine == "llm":
            from services.ocr_service.utils.llm_ocr_wrapper import LLMOCREngine
            return LLMOCREngine()
        else:
            raise OCREngineNotFoundException(
                f"Unknown OCR engine: '{engine}'. Available: paddle, mistral, lighton, llm"
            )

