"""
Shared — Rate Limiter Instances

Provides the slowapi limiter instance used across all routes.
Separated from gateway to avoid circular imports.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance — shared across all service routes
limiter = Limiter(key_func=get_remote_address)
