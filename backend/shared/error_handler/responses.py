"""
Shared — Standard API Response Format

All API responses follow a consistent format:
- Success: {"success": true, "data": {...}}
- Error:   {"success": false, "error": "User-friendly message"}
"""

from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


def success_response(data: Any = None) -> dict:
    """Create a standardized success response."""
    return {"success": True, "data": data}


def error_response(message: str) -> dict:
    """Create a standardized error response."""
    return {"success": False, "error": message}
