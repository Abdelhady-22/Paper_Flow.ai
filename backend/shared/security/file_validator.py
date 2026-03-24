"""
Shared — Multi-Layer File Validator

Validates uploaded files through 6 security layers:
1. Extension whitelist
2. File size limit
3. MIME type verification (python-magic)
4. Magic bytes (file signature)
5. Content integrity (try to open/parse)
6. Empty file check

Never exposes internal error details to the user.
"""

import magic
from pathlib import Path
from fastapi import UploadFile
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import (
    FileTooLargeException,
    UnsupportedFileTypeException,
    CorruptedFileException,
    SuspiciousFileException,
)

logger = get_logger(__name__)

# ── Allowed types configuration ────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
AUDIO_EXTENSIONS = {".wav", ".webm", ".mp3", ".ogg"}

ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
}

MAGIC_BYTES = {
    ".pdf": b"%PDF",
    ".png": b"\x89PNG",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".bmp": b"BM",
    ".wav": b"RIFF",
}

MAX_FILE_SIZES: dict[str, int] = {
    ".pdf": 50 * 1024 * 1024,
    ".docx": 30 * 1024 * 1024,
    ".png": 20 * 1024 * 1024,
    ".jpg": 20 * 1024 * 1024,
    ".jpeg": 20 * 1024 * 1024,
    ".tiff": 30 * 1024 * 1024,
    ".bmp": 20 * 1024 * 1024,
    ".wav": 25 * 1024 * 1024,
    ".webm": 25 * 1024 * 1024,
}


class FileValidator:
    """
    Multi-layer file validator.
    Validates extension, size, MIME type, magic bytes, and content integrity.
    Never exposes internal error details to the user.
    """

    async def validate(self, file: UploadFile, context: str = "document") -> bytes:
        """
        Validate file and return its bytes if all checks pass.

        Args:
            file: The uploaded file
            context: "document" | "audio"

        Returns:
            File content as bytes

        Raises:
            UnsupportedFileTypeException, FileTooLargeException,
            CorruptedFileException, SuspiciousFileException
        """
        allowed = AUDIO_EXTENSIONS if context == "audio" else ALLOWED_EXTENSIONS

        # ── Layer 1: Extension whitelist ───────────────────────────────
        ext = Path(file.filename or "").suffix.lower()
        if ext not in allowed:
            logger.warning(
                "file_rejected_extension",
                filename=file.filename,
                extension=ext,
                context=context,
            )
            raise UnsupportedFileTypeException(
                f"File type '{ext}' is not supported. "
                f"Allowed types: {', '.join(sorted(allowed))}"
            )

        # ── Layer 2: Read file content ─────────────────────────────────
        content = await file.read()
        await file.seek(0)

        # ── Layer 3: File size limit ───────────────────────────────────
        max_size = MAX_FILE_SIZES.get(ext, 20 * 1024 * 1024)
        size_mb = round(len(content) / 1024 / 1024, 2)
        max_mb = round(max_size / 1024 / 1024)

        if len(content) > max_size:
            logger.warning(
                "file_rejected_size",
                filename=file.filename,
                size_mb=size_mb,
                max_mb=max_mb,
            )
            raise FileTooLargeException(
                f"File is too large ({size_mb} MB). "
                f"Maximum allowed size for {ext} files is {max_mb} MB."
            )

        if len(content) == 0:
            raise CorruptedFileException("The uploaded file is empty.")

        # ── Layer 4: Magic bytes verification ─────────────────────────
        expected_magic = MAGIC_BYTES.get(ext)
        if expected_magic and not content.startswith(expected_magic):
            logger.warning(
                "file_rejected_magic_bytes",
                filename=file.filename,
                extension=ext,
            )
            raise SuspiciousFileException(
                "The file content does not match its extension. "
                "Please upload a valid file."
            )

        # ── Layer 5: MIME type check (python-magic) ────────────────────
        detected_mime = magic.from_buffer(content, mime=True)
        expected_mime = ALLOWED_MIME_TYPES.get(ext, "")

        docx_mimes = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip",
        }
        mime_valid = detected_mime == expected_mime or (
            ext == ".docx" and detected_mime in docx_mimes
        )

        if not mime_valid:
            logger.warning(
                "file_rejected_mime",
                filename=file.filename,
                detected_mime=detected_mime,
                expected_mime=expected_mime,
            )
            raise SuspiciousFileException(
                "The file appears to be invalid or corrupted. "
                "Please upload a valid file."
            )

        # ── Layer 6: Content integrity ─────────────────────────────────
        await self._verify_content_integrity(content, ext, file.filename)

        logger.info(
            "file_accepted",
            filename=file.filename,
            extension=ext,
            size_mb=size_mb,
        )
        return content

    async def _verify_content_integrity(
        self, content: bytes, ext: str, filename: str
    ) -> None:
        """Try to open the file with the appropriate library to confirm it's valid."""
        try:
            if ext == ".pdf":
                import pypdf
                from io import BytesIO

                pypdf.PdfReader(BytesIO(content))

            elif ext == ".docx":
                import docx
                from io import BytesIO

                docx.Document(BytesIO(content))

            elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
                from PIL import Image
                from io import BytesIO

                img = Image.open(BytesIO(content))
                img.verify()

        except Exception as e:
            logger.warning(
                "file_integrity_failed",
                filename=filename,
                extension=ext,
                error=str(e),
            )
            raise CorruptedFileException(
                "The file appears to be corrupted or unreadable. "
                "Please try uploading the file again."
            )
