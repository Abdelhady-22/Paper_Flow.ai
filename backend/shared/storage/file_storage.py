"""
Shared — Secure File Storage

Files are stored with UUID-based paths — never using the original filename
in the storage path to prevent directory traversal attacks.
Original filename is sanitized and stored in the database only.
"""

import uuid
from pathlib import Path
from shared.security.filename_sanitizer import sanitize_filename
from shared.logger.logger import get_logger

logger = get_logger(__name__)


async def store_file(
    content: bytes,
    original_filename: str,
    user_id: str,
    base_dir: str,
) -> dict:
    """
    Store file safely using UUID path.
    Returns storage metadata — original name stored in DB only, not in path.

    Args:
        content: File bytes
        original_filename: Original upload filename
        user_id: ID of the uploading user
        base_dir: Base storage directory

    Returns:
        Dict with paper_id, storage_path, original_filename, size_bytes
    """
    paper_id = str(uuid.uuid4())
    safe_name = sanitize_filename(original_filename)
    ext = Path(safe_name).suffix

    # Path uses UUIDs — original name never appears in filesystem path
    storage_path = Path(base_dir) / user_id / paper_id / f"file{ext}"
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    storage_path.write_bytes(content)

    logger.info(
        "file_stored",
        paper_id=paper_id,
        user_id=user_id,
        original_filename=safe_name,
        size_bytes=len(content),
    )

    return {
        "paper_id": paper_id,
        "storage_path": str(storage_path),
        "original_filename": safe_name,
        "size_bytes": len(content),
    }
