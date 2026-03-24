"""
Shared — Filename Sanitization

Removes dangerous characters from uploaded filenames to prevent:
- Path traversal attacks (../../etc/passwd)
- Injection attacks
- Hidden files
"""

import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from filenames.
    Prevents path traversal and injection attacks.

    Args:
        filename: Original filename from upload

    Returns:
        Sanitized safe filename
    """
    # Get only the base name — strip any directory components
    name = Path(filename).name

    # Keep only safe characters: letters, digits, dots, hyphens, underscores
    name = re.sub(r"[^\w.\-]", "_", name)

    # Remove leading dots (hidden files on Unix)
    name = name.lstrip(".")

    # Limit filename length
    if len(name) > 255:
        stem = Path(name).stem[:200]
        suffix = Path(name).suffix
        name = stem + suffix

    # Fallback if name becomes empty after sanitization
    if not name or name == Path(name).suffix:
        name = f"uploaded_file{Path(filename).suffix}"

    return name
