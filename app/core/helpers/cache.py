import aioredis
import json
import functools
from typing import Callable
from fastapi import HTTPException
from app.core.config import settings
from app.core.helpers.logging import logger

CACHE_KEY_USERS_GET_ALL = "users:get_all"

REDIS_URL = f"redis://{settings.REDIS_SERVER}:6379"

logger.info(f"Connecting to Redis at {REDIS_URL}")

redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

def cache_data(key: str, expire: int = None):
    """
    Cache the response with an optional expiration time.
    Logs cache hits, misses, and writes.
    :param key: The cache key.
    :param expire: Expiration time in seconds (None or 0 for infinite caching).
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            # Log checking cache
            logger.info(f"#### Checking cache for key: {key}")

            # Check cache first
            cached_data = await redis.get(key)

            if cached_data:
                logger.info(f"#### Cache HIT for key: {key} | Returning Data")
                return json.loads(cached_data)

            # Log cache miss
            logger.info(f"#### Cache MISS for key: {key}")

            # If not cached, call the function
            result = await func(*args, **kwargs)

            # Cache the result
            if expire is None or expire == 0:
                logger.info(f"##### Caching data for key: {key} with NO expiration")
                await redis.set(key, json.dumps(result))  # Infinite cache
            else:
                logger.info(f"##### Caching data for key: {key} with expiration {expire} seconds")
                await redis.set(key, json.dumps(result), ex=expire)

            return result
        return wrapper
    return decorator

def cache_invalidate(key: str):
    """
    Invalidate the cache for a specific key.
    :param key: The cache key to invalidate.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            result = await func(*args, **kwargs)

            # Remove cache entry
            await redis.delete(key)
            return result
        return wrapper
    return decorator

async def cache_invalidate_by_key(key: str):
    """
    Directly invalidate cache by key without a decorator.
    :param key: The cache key to invalidate.
    """
    try:
        logger.info(f"##### Attempting to invalidating cache for key: {key}")
        deleted = await redis.delete(key)
        if deleted:
            logger.info(f"##### Cache invalidated for key: {key}")
        else:
            logger.info(f"##### No cache found for key: {key}")
    except Exception as e:
        logger.error(f"##### Cache invalidation failed for key: {key}. Error: {str(e)}")