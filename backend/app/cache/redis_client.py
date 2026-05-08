"""Redis singleton with graceful degradation."""
from typing import Optional
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    _healthy: bool = False

    @classmethod
    async def init(cls) -> None:
        if not settings.REDIS_ENABLED:
            logger.info("redis.disabled")
            return
        try:
            cls._pool = ConnectionPool.from_url(
                settings.REDIS_URL, max_connections=50, decode_responses=True
            )
            cls._client = redis.Redis(connection_pool=cls._pool)
            await cls._client.ping()
            cls._healthy = True
            logger.info("redis.connected", url=settings.REDIS_URL)
        except Exception as e:
            cls._healthy = False
            logger.warning("redis.connection_failed", error=str(e))

    @classmethod
    async def close(cls) -> None:
        if cls._client:
            await cls._client.close()
        if cls._pool:
            await cls._pool.disconnect()

    @classmethod
    def get(cls) -> Optional[redis.Redis]:
        return cls._client if cls._healthy else None

    @classmethod
    def is_healthy(cls) -> bool:
        return cls._healthy


def get_redis() -> Optional[redis.Redis]:
    return RedisClient.get()