"""
Middleware to check if a user is blocked/inactive before processing their requests.
"""
from telegram import Update
from telegram.ext import ContextTypes, BaseHandler
from typing import Optional, Callable, Any

from database.engine import SessionLocal
from database.queries import user_queries
from core.translator import _
from core.config import ADMIN_IDS

async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE, handler: Callable) -> Optional[Any]:
    """
    Middleware that checks if a user is blocked before processing their update.
    Admins are always allowed regardless of is_active status.
    """
    user = update.effective_user
    
    if not user:
        return await handler(update, context)
    
    # Always allow admins
    if user.id in ADMIN_IDS:
        return await handler(update, context)
    
    # Check if user is blocked
    db = SessionLocal()
    try:
        db_user = user_queries.find_user_by_id(db, user.id)
        
        if db_user and not db_user.is_active:
            # User is blocked, don't process the update
            if update.message:
                await update.message.reply_text(_('messages.user_account_blocked'))
            elif update.callback_query:
                await update.callback_query.answer(_('messages.user_account_blocked'), show_alert=True)
            return None  # Stop processing
    finally:
        db.close()
    
    # User is active or doesn't exist yet, proceed
    return await handler(update, context)

