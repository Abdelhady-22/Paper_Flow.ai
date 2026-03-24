"""
OCR Service — File Parser Utility

Extracts text from PDF and DOCX files using their respective libraries.
Falls back to OCR for scanned/image-based pages.
"""

from io import BytesIO
from pathlib import Path
from typing import Optional
import PyPDF2
import pdfplumber
import docx
from shared.logger.logger import get_logger

logger = get_logger(__name__)


async def extract_text_from_pdf(content: bytes, filename: str) -> Optional[str]:
    """
    Extract text from a PDF file.
    Uses PyPDF2 first, falls back to pdfplumber for complex layouts.

    Returns None if the PDF contains no extractable text (scanned/image).
    """
    try:
        # Try PyPDF2 first (faster)
        reader = PyPDF2.PdfReader(BytesIO(content))
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())

        text = "\n\n".join(text_parts)

        # If PyPDF2 returned very little text, try pdfplumber
        if len(text.strip()) < 100:
            logger.info("pdf_fallback_pdfplumber", filename=filename)
            with pdfplumber.open(BytesIO(content)) as pdf:
                plumber_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        plumber_parts.append(page_text.strip())
                plumber_text = "\n\n".join(plumber_parts)

                if len(plumber_text) > len(text):
                    text = plumber_text

        if not text.strip():
            logger.info("pdf_no_text", filename=filename, reason="scanned_or_image")
            return None

        page_count = len(reader.pages)
        logger.info(
            "pdf_text_extracted",
            filename=filename,
            chars=len(text),
            pages=page_count,
        )
        return text

    except Exception as e:
        logger.error("pdf_extraction_error", filename=filename, error=str(e))
        return None


async def extract_text_from_docx(content: bytes, filename: str) -> Optional[str]:
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)

        if not text.strip():
            logger.info("docx_no_text", filename=filename)
            return None

        logger.info(
            "docx_text_extracted",
            filename=filename,
            chars=len(text),
            paragraphs=len(paragraphs),
        )
        return text

    except Exception as e:
        logger.error("docx_extraction_error", filename=filename, error=str(e))
        return None


async def extract_text(content: bytes, filename: str) -> Optional[str]:
    """
    Extract text from a file based on its extension.
    Returns None if no text could be extracted (requires OCR).
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return await extract_text_from_pdf(content, filename)
    elif ext == ".docx":
        return await extract_text_from_docx(content, filename)
    else:
        # Image files — need OCR
        return None
