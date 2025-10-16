"""
Admin handlers for managing marketers.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries
from database.models.user import UserRole, User
from core.telegram_logger import log_error

async def list_all_marketers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all marketers with their statistics."""
    db = SessionLocal()
    try:
        marketers = db.query(User).filter(User.role == UserRole.marketer).all()
        
        if not marketers:
            await update.message.reply_text(_('messages.admin_no_marketers'))
            return
        
        text = _('messages.admin_marketers_list_header') + "\n\n"
        
        for marketer in marketers:
            referred_count = user_queries.get_referred_users_count(db, marketer.user_id)
            active_referrals = user_queries.get_active_referrals_count(db, marketer.user_id)
            
            text += _('messages.admin_marketer_item',
                     user_id=marketer.user_id,
                     referred_count=referred_count,
                     active_referrals=active_referrals,
                     commission_balance=marketer.commission_balance)
            text += "\n━━━━━━━━━━\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        await log_error(context, e, "list_all_marketers")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()

