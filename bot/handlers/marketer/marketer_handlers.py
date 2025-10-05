from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.queries import user_queries
from bot.keyboards.reply_keyboards import get_marketer_panel_menu, get_marketer_main_menu

async def marketer_panel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the marketer panel menu."""
    await update.message.reply_text(
        _('messages.marketer_panel_welcome'),
        reply_markup=get_marketer_panel_menu()
    )

async def back_to_main_menu_from_marketer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the user to their main menu from the marketer panel."""
    await update.message.reply_text(
        _('messages.back_to_main_menu'),
        reply_markup=get_marketer_main_menu() # Assuming the user is a marketer
    )

async def get_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates and sends the marketer's unique referral link."""
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    await update.message.reply_text(
        _('messages.marketer_invite_link', link=invite_link)
    )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the marketer's referral statistics."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        referred_count = user_queries.get_referred_users_count(db, referrer_id=user_id)
        # Commission calculation logic would go here in a real scenario
        commission_balance = referred_count * 1000 # Example: 1000 Toman per referral

        await update.message.reply_text(
            _('messages.marketer_stats',
              count=referred_count,
              commission=commission_balance)
        )
    finally:
        db.close()

async def request_payout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a payout request to the admin."""
    user = update.effective_user
    # In a real application, you would check their actual commission balance first
    
    admin_message = _('messages.admin_payout_request',
                      user_id=user.id,
                      first_name=user.first_name)

    # You might want to add an inline keyboard for the admin to mark it as paid
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    
    await update.message.reply_text(_('messages.marketer_payout_request_sent'))