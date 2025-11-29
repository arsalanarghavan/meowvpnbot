"""
Rate limiting middleware for bot handlers.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Any
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from core.logger import get_logger

logger = get_logger(__name__)

# In-memory storage for rate limiting
# In production, consider using Redis or database
_rate_limit_store: dict[int, list[datetime]] = defaultdict(list)


def rate_limit(max_calls: int = 5, period_seconds: int = 60, per_user: bool = True):
    """
    Decorator to rate limit bot handlers.
    
    Args:
        max_calls: Maximum number of calls allowed
        period_seconds: Time period in seconds
        per_user: If True, rate limit per user; if False, global rate limit
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
            # Get identifier (user ID or global)
            if per_user and update.effective_user:
                identifier = update.effective_user.id
            else:
                identifier = 0  # Global
            
            now = datetime.now()
            cutoff = now - timedelta(seconds=period_seconds)
            
            # Clean old entries
            _rate_limit_store[identifier] = [
                timestamp for timestamp in _rate_limit_store[identifier]
                if timestamp > cutoff
            ]
            
            # Check if limit exceeded
            if len(_rate_limit_store[identifier]) >= max_calls:
                logger.warning(
                    f"Rate limit exceeded for {'user' if per_user else 'global'} "
                    f"{identifier}: {len(_rate_limit_store[identifier])} calls in {period_seconds}s"
                )
                
                if update.message:
                    await update.message.reply_text(
                        f"⚠️ تعداد درخواست‌های شما بیش از حد مجاز است. "
                        f"لطفاً {period_seconds} ثانیه دیگر تلاش کنید."
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        f"⚠️ تعداد درخواست‌ها بیش از حد مجاز است. لطفاً صبر کنید.",
                        show_alert=True
                    )
                
                return None
            
            # Record this call
            _rate_limit_store[identifier].append(now)
            
            # Call the original function
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    return decorator


def clear_rate_limit(user_id: int = None):
    """
    Clear rate limit for a specific user or all users.
    
    Args:
        user_id: User ID to clear, or None to clear all
    """
    if user_id is not None:
        _rate_limit_store.pop(user_id, None)
    else:
        _rate_limit_store.clear()

