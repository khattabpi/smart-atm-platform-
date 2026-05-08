"""Bridges Redis Pub/Sub → ConnectionManager. Enables horizontal scaling."""
import asyncio
from app.cache.redis_client import get_redis
from app.ws.manager import manager
from app.core.logging import get_logger

logger = get_logger(__name__)

GLOBAL_CHANNELS = ["ws:atm:status"]


class PubSubBridge:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        r = get_redis()
        if not r:
            logger.warning("pubsub.bridge.no_redis")
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()

    async def _run(self) -> None:
        r = get_redis()
        if not r:
            return
        pubsub = r.pubsub()
        # Subscribe to global + per-user pattern
        await pubsub.subscribe(*GLOBAL_CHANNELS)
        await pubsub.psubscribe("ws:user:*:notifications")

        async for msg in pubsub.listen():
            if not self._running:
                break
            if msg["type"] not in ("message", "pmessage"):
                continue

            channel = msg["channel"]
            data = msg["data"]

            if channel == "ws:atm:status":
                await manager.broadcast("atm:status", data)
            elif channel.startswith("ws:user:"):
                # ws:user:{id}:notifications
                parts = channel.split(":")
                if len(parts) >= 3:
                    user_id = parts[2]
                    await manager.broadcast(f"user:{user_id}", data)


bridge = PubSubBridge()