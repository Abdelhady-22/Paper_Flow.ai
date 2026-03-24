"""
Infrastructure — Redis Client

Provides async Redis client for caching and Pub/Sub event bus.
Used for: result caching, LLM response caching, TTS audio caching,
real-time progress events via Pub/Sub.
"""

import redis.asyncio as aioredis
from settings import settings
from shared.logger.logger import get_logger

logger = get_logger(__name__)


def get_redis_client() -> aioredis.Redis:
    """Create and return an async Redis client."""
    return aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )


def get_redis_binary_client() -> aioredis.Redis:
    """
    Create Redis client that returns raw bytes.
    Used for binary data like TTS audio caching.
    """
    return aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=False,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )


async def init_redis() -> aioredis.Redis:
    """Initialize and verify Redis connection."""
    client = get_redis_client()
    try:
        await client.ping()
        logger.info("redis_connected", url=settings.REDIS_URL)
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        raise
    return client


async def close_redis(client: aioredis.Redis) -> None:
    """Close Redis client connection."""
    await client.close()
