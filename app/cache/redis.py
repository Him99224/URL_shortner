import redis
import json

from datetime import datetime,timezone

from app.core.config import settings
from app.core.logging import logging

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

logger = logging.getLogger(__name__)

def cache_url(short_code: str, original_url:str, expires_at:str|None):
    data = {
        "original_url": original_url,
        "expires_at": expires_at.isoformat() if expires_at else None
        }
    try:
        if expires_at:
            ttl=int((expires_at - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                redis_client.set(
                    short_code,
                    json.dumps(data),
                    ex=ttl
                )
        else:
                redis_client.set(short_code,json.dumps(data)
                                )
    except redis.RedisError as e:
        logger.warning("Redis error while caching URL for short code '%s': %s", short_code, str(e))

def get_cached_url(short_code:str):
    try:
        cached=redis_client.get(short_code)
    except redis.RedisError as e:
        logger.warning("Redis error while getting cached URL for short code '%s': %s", short_code, str(e))
        return None
    
    if cached is None:
        return None

    data=json.loads(cached)
    if data["expires_at"] is not None:
        data["expires_at"]=datetime.fromisoformat(data["expires_at"])
    return data

def is_cached_url_expired(
        cached_url:dict
)->bool:
    current_time=datetime.now(timezone.utc)
    expires_at=cached_url.get("expires_at")
    if expires_at is None:
        return False
    else:
        return current_time>=expires_at