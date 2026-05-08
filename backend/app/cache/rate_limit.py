"""Token-bucket rate limiter using Redis INCR + EXPIRE."""
from fastapi import Request, HTTPException
from app.cache.redis_client import get_redis
from app.cache.keys import CacheKeys
from app.core.config import settings


async def rate_limit_dependency(request: Request, bucket: str = "global") -> None:
    r = get_redis()
    if not r:
        return  # Graceful: no Redis → no limit

    identifier = request.client.host if request.client else "anonymous"
    key = CacheKeys.rate_limit(identifier, bucket)

    try:
        current = await r.incr(key)
        if current == 1:
            await r.expire(key, 60)
        if current > settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=429, detail="Too many requests")
    except HTTPException:
        raise
    except Exception:
        return  # Don't block users on Redis failures