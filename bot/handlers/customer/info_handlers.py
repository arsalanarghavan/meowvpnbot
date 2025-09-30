from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries

async def account_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's account information."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id=user_id)
        
        info_text = _('messages.account_info',
                      user_id=db_user.user_id,
                      wallet_balance=db_user.wallet_balance,
                      role=_(f'roles.{db_user.role.value}')) # ترجمه نقش کاربر
    finally:
        db.close()
        
    await update.message.reply_text(info_text)

async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays support information."""
    support_text = _('messages.support_info')
    await update.message.reply_text(support_text)

async def applications_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays application download links."""
    apps_text = _('messages.applications_info')
    await update.message.reply_text(apps_text)