"""
Shared — Secure File Storage (Local + GCS)

Supports two backends:
- "local": Files stored on local disk (default, for development)
- "gcs": Files stored in Google Cloud Storage (for production on GCP)

Files are stored with UUID-based paths — never using the original filename
in the storage path to prevent directory traversal attacks.
Original filename is sanitized and stored in the database only.

Backend is selected via STORAGE_BACKEND env var.
"""

import uuid
from pathlib import Path
from settings import settings
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

    Dispatches to local or GCS backend based on STORAGE_BACKEND setting.

    Args:
        content: File bytes
        original_filename: Original upload filename
        user_id: ID of the uploading user
        base_dir: Base storage directory (used for local backend only)

    Returns:
        Dict with paper_id, storage_path, original_filename, size_bytes
    """
    if settings.STORAGE_BACKEND == "gcs":
        return await _store_gcs(content, original_filename, user_id)
    return await _store_local(content, original_filename, user_id, base_dir)


async def _store_local(
    content: bytes,
    original_filename: str,
    user_id: str,
    base_dir: str,
) -> dict:
    """Store file on local filesystem."""
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
        backend="local",
    )

    return {
        "paper_id": paper_id,
        "storage_path": str(storage_path),
        "original_filename": safe_name,
        "size_bytes": len(content),
    }


async def _store_gcs(
    content: bytes,
    original_filename: str,
    user_id: str,
) -> dict:
    """
    Store file in Google Cloud Storage.
    Auto-authenticates on GCE via the VM's service account.
    """
    from google.cloud import storage as gcs_storage

    bucket_name = settings.GCS_BUCKET_NAME
    if not bucket_name:
        logger.error("gcs_bucket_not_configured")
        raise ValueError(
            "GCS_BUCKET_NAME is not configured. "
            "Set it in .env or switch STORAGE_BACKEND to 'local'."
        )

    paper_id = str(uuid.uuid4())
    safe_name = sanitize_filename(original_filename)
    ext = Path(safe_name).suffix

    # GCS object path: {user_id}/{paper_id}/file.ext
    blob_path = f"{user_id}/{paper_id}/file{ext}"

    client = gcs_storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    # Upload bytes to GCS
    blob.upload_from_string(content, content_type="application/octet-stream")

    storage_path = f"gs://{bucket_name}/{blob_path}"

    logger.info(
        "file_stored",
        paper_id=paper_id,
        user_id=user_id,
        original_filename=safe_name,
        size_bytes=len(content),
        backend="gcs",
        gcs_path=storage_path,
    )

    return {
        "paper_id": paper_id,
        "storage_path": storage_path,
        "original_filename": safe_name,
        "size_bytes": len(content),
    }
