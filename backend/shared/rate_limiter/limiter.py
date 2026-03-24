"""
Shared — LLM Rate Limiter

Controls concurrent LLM requests to avoid hitting provider rate limits.
Uses asyncio Semaphore to limit max concurrent LLM calls.
Configurable via LLM_MAX_CONCURRENT env var (default: 5).
"""

import os
from asyncio import Semaphore


class LLMRateLimiter:
    """
    Controls concurrent LLM requests to avoid hitting provider rate limits.
    Max concurrent LLM calls configurable via LLM_MAX_CONCURRENT env var.
    """

    def __init__(self, max_concurrent: int = 5):
        self._semaphore = Semaphore(max_concurrent)

    async def acquire(self):
        """Acquire a slot for an LLM request."""
        await self._semaphore.acquire()

    def release(self):
        """Release a slot after an LLM request completes."""
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()


# Global singleton used across all services
llm_rate_limiter = LLMRateLimiter(
    max_concurrent=int(os.getenv("LLM_MAX_CONCURRENT", "5"))
)
