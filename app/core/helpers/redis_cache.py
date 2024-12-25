import aioredis
import json
from typing import Any
from app.core.config import settings
from app.core.helpers.logging import logger

USERS_CACHE_KEY = "employers"

REDIS_URL = f"redis://{settings.REDIS_SERVER}:6379"

logger.info(f"Connecting to Redis at {REDIS_URL}")

redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_cache(key: str) -> Any:
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value: Any, expire: int = 60) -> None:
    await redis.set(key, json.dumps(value), ex=expire)

async def invalidate_cache(key: str) -> None:
    await redis.delete(key)