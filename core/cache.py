"""
Simple in-memory cache for frequently accessed data.
For production, consider using Redis or Memcached.
"""
from typing import Any, Optional
from datetime import datetime, timedelta
from functools import wraps
from core.logger import get_logger

logger = get_logger(__name__)

# Simple in-memory cache
_cache: dict[str, tuple[Any, datetime]] = {}


def get_cache(key: str, default: Any = None) -> Optional[Any]:
    """
    Get a value from cache.
    
    Args:
        key: Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    if key not in _cache:
        return default
    
    value, expiry = _cache[key]
    
    # Check if expired
    if datetime.now() > expiry:
        del _cache[key]
        return default
    
    return value


def set_cache(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """
    Set a value in cache with TTL.
    
    Args:
        key: Cache key
        value: Value to cache
        ttl_seconds: Time to live in seconds (default 5 minutes)
    """
    expiry = datetime.now() + timedelta(seconds=ttl_seconds)
    _cache[key] = (value, expiry)


def delete_cache(key: str) -> None:
    """Delete a key from cache."""
    _cache.pop(key, None)


def clear_cache(pattern: str = None) -> None:
    """
    Clear cache entries.
    
    Args:
        pattern: If provided, only clear keys matching pattern (simple substring match)
    """
    if pattern:
        keys_to_delete = [key for key in _cache.keys() if pattern in key]
        for key in keys_to_delete:
            del _cache[key]
    else:
        _cache.clear()


def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = get_cache(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            set_cache(cache_key, result, ttl_seconds)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = get_cache(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            set_cache(cache_key, result, ttl_seconds)
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

