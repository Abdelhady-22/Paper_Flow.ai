"""
OCR Service — LLM Vision OCR Engine Wrapper

Uses vision-capable LLMs (Gemini, GPT-4o, Claude, etc.) via LiteLLM
to extract text from images and scanned documents.

Supports any LiteLLM provider with vision/multimodal capabilities.
Default: gemini/gemini-1.5-flash (fast, accurate, free tier available).
"""

import base64
import mimetypes
from pathlib import Path
from litellm import acompletion
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

# ── Default model for vision OCR ────────────────────────────────────────
# Can be overridden via LLM_OCR_MODEL env var.
DEFAULT_OCR_MODEL = "gemini/gemini-1.5-flash"

# ── OCR system prompt ──────────────────────────────────────────────────
OCR_SYSTEM_PROMPT = """You are a precise OCR engine. Your task is to extract ALL text 
from the provided image exactly as it appears.

Rules:
- Extract every word, number, symbol, and punctuation mark visible in the image.
- Preserve the original layout, line breaks, and paragraph structure as closely as possible.
- For tables, use plain text formatting with aligned columns.
- For multi-column layouts, read left to right, top to bottom.
- Do NOT add any commentary, headers, footers, or explanations.
- Do NOT summarize or paraphrase — extract the text verbatim.
- If the image contains handwritten text, do your best to transcribe it accurately.
- If a word is unclear, provide your best guess with [?] after it.
- Output ONLY the extracted text, nothing else."""


class LLMOCREngine(OCREngine):
    """LLM Vision-based OCR engine — uses multimodal LLMs to extract text."""

    def __init__(self, model: str | None = None):
        self.model = model or getattr(settings, "LLM_OCR_MODEL", None) or DEFAULT_OCR_MODEL

        # Validate that the provider has an API key configured
        provider = self.model.split("/")[0] if "/" in self.model else self.model
        key_map = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        env_var = key_map.get(provider)
        if env_var and not getattr(settings, env_var, None):
            raise MissingAPIKeyException(
                f"{env_var} is not configured. Required for LLM OCR with {provider}."
            )

    async def extract(self, file: bytes, filename: str) -> OCRResult:
        try:
            logger.info("llm_ocr_start", filename=filename, model=self.model)

            # Determine MIME type from filename
            ext = Path(filename).suffix.lower()
            mime_type = mimetypes.guess_type(filename)[0] or "image/png"

            # For PDFs, we can't send directly as image — inform the user
            if ext == ".pdf":
                logger.info("llm_ocr_pdf_passthrough", filename=filename)
                # LiteLLM / Gemini can handle PDFs as documents
                mime_type = "application/pdf"

            # Encode file to base64 data URL
            b64_data = base64.b64encode(file).decode("utf-8")
            data_url = f"data:{mime_type};base64,{b64_data}"

            # Build multimodal message with image
            messages = [
                {"role": "system", "content": OCR_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Output only the extracted text.",
                        },
                    ],
                },
            ]

            response = await acompletion(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for accurate extraction
                max_tokens=4096,
                timeout=60,
                num_retries=2,
            )

            text = response.choices[0].message.content or ""

            # Clean up common LLM artifacts
            text = text.strip()
            if text.startswith("```"):
                # Remove markdown code fences if LLM wraps output
                lines = text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = "\n".join(lines)

            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(
                "llm_ocr_complete",
                filename=filename,
                model=self.model,
                chars=len(text),
                tokens=tokens_used,
            )

            return OCRResult(
                text=text,
                engine=f"llm ({self.model})",
                page_count=1,
            )

        except Exception as e:
            error_str = str(e).lower()

            if "timeout" in error_str:
                logger.error("llm_ocr_timeout", filename=filename, model=self.model)
                raise OCRTimeoutException(
                    "LLM OCR timed out. Try a smaller image or use local PaddleOCR."
                )

            if "rate" in error_str and "limit" in error_str:
                logger.warning("llm_ocr_rate_limit", filename=filename, model=self.model)
                raise OCRExtractionException(
                    "LLM rate limit reached. Please wait a moment and try again, "
                    "or switch to the local PaddleOCR engine."
                )

            logger.error(
                "llm_ocr_error",
                filename=filename,
                model=self.model,
                error=str(e),
            )
            raise OCRExtractionException(
                "Text extraction via LLM failed. "
                "Please try a different engine (e.g. paddle)."
            )
