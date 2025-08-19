"""
Redis client for Voice AI Demo
Caching and real-time data management
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        await init_redis()
    return redis_client

# Cache operations
async def set_cache(key: str, value: Any, expire: Optional[int] = None):
    """Set cache value with optional expiration"""
    try:
        client = await get_redis()
        serialized_value = json.dumps(value)
        if expire:
            await client.setex(key, expire, serialized_value)
        else:
            await client.set(key, serialized_value)
    except Exception as e:
        logger.error(f"Cache set failed for key {key}: {e}")

async def get_cache(key: str) -> Optional[Any]:
    """Get cache value"""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get failed for key {key}: {e}")
        return None

async def delete_cache(key: str):
    """Delete cache key"""
    try:
        client = await get_redis()
        await client.delete(key)
    except Exception as e:
        logger.error(f"Cache delete failed for key {key}: {e}")

async def clear_cache_pattern(pattern: str):
    """Clear cache keys matching pattern"""
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    except Exception as e:
        logger.error(f"Cache clear pattern failed for {pattern}: {e}")

# Real-time data operations
async def publish_event(channel: str, data: Dict[str, Any]):
    """Publish event to Redis channel"""
    try:
        client = await get_redis()
        await client.publish(channel, json.dumps(data))
    except Exception as e:
        logger.error(f"Event publish failed for channel {channel}: {e}")

async def subscribe_to_events(channel: str):
    """Subscribe to Redis channel for events"""
    try:
        client = await get_redis()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    except Exception as e:
        logger.error(f"Event subscription failed for channel {channel}: {e}")
        return None

# Call session management
async def set_call_session(call_sid: str, session_data: Dict[str, Any]):
    """Set call session data in Redis"""
    key = f"call_session:{call_sid}"
    await set_cache(key, session_data, expire=3600)  # 1 hour

async def get_call_session(call_sid: str) -> Optional[Dict[str, Any]]:
    """Get call session data from Redis"""
    key = f"call_session:{call_sid}"
    return await get_cache(key)

async def update_call_session(call_sid: str, updates: Dict[str, Any]):
    """Update call session data"""
    session_data = await get_call_session(call_sid)
    if session_data:
        session_data.update(updates)
        await set_call_session(call_sid, session_data)

async def delete_call_session(call_sid: str):
    """Delete call session data"""
    key = f"call_session:{call_sid}"
    await delete_cache(key)

# Conversation state management
async def set_conversation_state(call_sid: str, state: Dict[str, Any]):
    """Set conversation state for a call"""
    key = f"conversation_state:{call_sid}"
    await set_cache(key, state, expire=1800)  # 30 minutes

async def get_conversation_state(call_sid: str) -> Optional[Dict[str, Any]]:
    """Get conversation state for a call"""
    key = f"conversation_state:{call_sid}"
    return await get_cache(key)

async def update_conversation_state(call_sid: str, updates: Dict[str, Any]):
    """Update conversation state"""
    state = await get_conversation_state(call_sid)
    if state:
        state.update(updates)
        await set_conversation_state(call_sid, state)

# Rate limiting
async def check_rate_limit(key: str, limit: int, window: int) -> bool:
    """Check if rate limit is exceeded"""
    try:
        client = await get_redis()
        current = await client.get(key)
        if current and int(current) >= limit:
            return False
        
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
        return True
    except Exception as e:
        logger.error(f"Rate limit check failed for key {key}: {e}")
        return True  # Allow on error

# Health check
async def redis_health_check() -> bool:
    """Check Redis health"""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception:
        return False
