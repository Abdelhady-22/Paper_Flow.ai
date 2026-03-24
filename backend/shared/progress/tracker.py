"""
Shared — WebSocket Progress Tracking

Real-time progress updates via Redis Pub/Sub + WebSocket.
Implements the Observer pattern from Section 27 & 28.

Services publish progress events → Redis Pub/Sub → WebSocket → Frontend
"""

import json
from typing import Optional
from fastapi import WebSocket
from shared.logger.logger import get_logger
from infrastructure.redis.client import get_redis_client

logger = get_logger(__name__)


class ProgressTracker:
    """
    Publishes progress events to Redis Pub/Sub.
    Services use this to report task progress in real-time.
    """

    CHANNEL = "task_progress"

    async def publish(
        self,
        task_id: str,
        status: str,
        progress: float,
        message: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """Publish a progress update to Redis Pub/Sub."""
        event = {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message,
            "metadata": metadata or {},
        }
        redis = get_redis_client()
        try:
            await redis.publish(self.CHANNEL, json.dumps(event))
            logger.debug("progress_published", task_id=task_id, progress=progress)
        except Exception as e:
            logger.warning("progress_publish_failed", error=str(e))
        finally:
            await redis.close()


async def websocket_progress_handler(websocket: WebSocket) -> None:
    """
    WebSocket endpoint that streams progress events to the client.
    Subscribes to Redis Pub/Sub and forwards events.
    """
    await websocket.accept()
    redis = get_redis_client()

    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe(ProgressTracker.CHANNEL)

        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except Exception as e:
        logger.error("websocket_error", error=str(e))
    finally:
        await pubsub.unsubscribe(ProgressTracker.CHANNEL)
        await redis.close()
        try:
            await websocket.close()
        except Exception:
            pass


# Global singleton
progress_tracker = ProgressTracker()
