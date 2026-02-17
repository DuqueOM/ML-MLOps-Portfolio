"""Redis caching utilities for FastAPI applications."""

import hashlib
import json
import logging
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)

REDIS_AVAILABLE = False
redis_client = None

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available. Install with: pip install redis")


def get_redis_client(host: str = "localhost", port: int = 6379, db: int = 0):
    """Get or create Redis client."""
    global redis_client
    if not REDIS_AVAILABLE:
        return None
    if redis_client is None:
        try:
            redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            redis_client.ping()
            logger.info(f"Redis connected: {host}:{port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client


def cache_key(prefix: str, data: dict) -> str:
    """Generate cache key from data."""
    sorted_data = json.dumps(data, sort_keys=True)
    hash_val = hashlib.md5(sorted_data.encode()).hexdigest()
    return f"{prefix}:{hash_val}"


def cache_response(prefix: str = "api", ttl: int = 3600):
    """Decorator to cache API responses.

    Usage:
        @cache_response(prefix="predict", ttl=300)
        async def predict(data: dict):
            return model.predict(data)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return await func(*args, **kwargs)

            client = get_redis_client()
            if client is None:
                return await func(*args, **kwargs)

            # Extract data for cache key (Pydantic v2: model_dump, v1: dict)
            cache_data = {}
            if args and hasattr(args[0], "model_dump"):
                cache_data = args[0].model_dump()
            elif args and hasattr(args[0], "dict"):
                cache_data = args[0].dict()
            elif kwargs:
                cache_data = kwargs

            key = cache_key(prefix, cache_data)

            # Try cache
            try:
                cached = client.get(key)
                if cached:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                client.setex(key, ttl, json.dumps(result))
                logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"Cache write error: {e}")

            return result

        return wrapper

    return decorator
