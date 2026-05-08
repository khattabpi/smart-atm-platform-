"""Cache-aside decorator with TTL + graceful fallback."""
import json
import functools
from typing import Callable, Any
from app.cache.redis_client import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)


def cached(key_builder: Callable[..., str], ttl: int = 60):
    """
    Cache-aside decorator. `key_builder` receives same args as wrapped fn.
    On Redis failure, function executes normally (graceful degradation).
    """
    def decorator(fn: Callable):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            r = get_redis()
            key = key_builder(*args, **kwargs) if r else None

            # Try cache
            if r and key:
                try:
                    cached_val = await r.get(key)
                    if cached_val:
                        return json.loads(cached_val)
                except Exception as e:
                    logger.warning("cache.read_failed", key=key, error=str(e))

            # Compute
            result = await fn(*args, **kwargs)

            # Populate
            if r and key and result is not None:
                try:
                    await r.set(key, json.dumps(result, default=str), ex=ttl)
                except Exception as e:
                    logger.warning("cache.write_failed", key=key, error=str(e))
            return result
        return wrapper
    return decorator


async def invalidate(*keys: str) -> None:
    r = get_redis()
    if not r:
        return
    try:
        await r.delete(*keys)
    except Exception as e:
        logger.warning("cache.invalidate_failed", error=str(e))


async def invalidate_pattern(pattern: str) -> None:
    r = get_redis()
    if not r:
        return
    try:
        async for key in r.scan_iter(match=pattern, count=200):
            await r.delete(key)
    except Exception as e:
        logger.warning("cache.invalidate_pattern_failed", pattern=pattern, error=str(e))