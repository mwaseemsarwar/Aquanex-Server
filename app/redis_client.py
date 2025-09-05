import hashlib
from typing import Optional
from redis.asyncio import Redis
from .config import settings

redis: Optional[Redis] = None

async def get_redis() -> Optional[Redis]:
    global redis
    if settings.REDIS_URL is None:
        return None
    if redis is None:
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis

def cache_key_from_prompt(last_user_message: str, model: str) -> str:
    h = hashlib.sha256(last_user_message.encode("utf-8")).hexdigest()
    return f"chat:resp:{model}:{h}"
