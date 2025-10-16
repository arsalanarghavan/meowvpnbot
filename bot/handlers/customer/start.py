from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.reply_keyboards import get_customer_main_menu, get_marketer_main_menu
from core.translator import _
from database.engine import SessionLocal
from database.models.user import UserRole
from database.queries import user_queries
from core.config import ADMIN_IDS  # <--- 'ADMIN_ID' به 'ADMIN_IDS' تغییر کرد

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command, referrals, and shows the correct menu."""
    user = update.effective_user
    db = SessionLocal()
    try:
        referrer_id = None
        # Check for referral payload in the start command
        if context.args and context.args[0].startswith('ref_'):
            try:
                # Extract referrer ID from the payload (e.g., 'ref_123456')
                ref_id_str = context.args[0].split('_')[1]
                referrer_id = int(ref_id_str)
                # Ensure a user cannot refer themselves
                if referrer_id == user.id:
                    referrer_id = None
            except (IndexError, ValueError):
                referrer_id = None

        db_user = user_queries.find_or_create_user(db, user_id=user.id, referrer_id=referrer_id)

        # Update user's role to admin if they are in the admin list
        # <--- شرط بررسی از برابری با یک آیدی به وجود داشتن در لیست تغییر کرد
        if user.id in ADMIN_IDS and db_user.role != UserRole.admin:
            db_user.role = UserRole.admin
            db.commit()
            db.refresh(db_user)

        # Determine the correct keyboard based on user role
        if db_user.role == UserRole.marketer:
            reply_markup = get_marketer_main_menu()
        else:
            reply_markup = get_customer_main_menu()

    finally:
        db.close()

    welcome_text = _('messages.welcome', first_name=user.first_name)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)