from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.reply_keyboards import get_customer_main_menu
from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command and ensures the user is in the database."""
    user = update.effective_user
    db = SessionLocal()
    try:
        # پیدا کردن یا ساختن کاربر در دیتابیس
        user_queries.find_or_create_user(db, user_id=user.id)
    finally:
        db.close()

    welcome_text = _('messages.welcome', first_name=user.first_name)
    reply_markup = get_customer_main_menu()
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)