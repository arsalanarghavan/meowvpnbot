from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.queries import user_queries, setting_queries
from bot.keyboards.reply_keyboards import get_marketer_panel_menu, get_marketer_main_menu

async def marketer_panel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the marketer panel menu."""
    await update.message.reply_text(
        _('messages.marketer_panel_welcome'),
        reply_markup=get_marketer_panel_menu()
    )

async def back_to_main_menu_from_marketer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the user to their main menu from the marketer panel."""
    # This function needs to decide which main menu to show
    db = SessionLocal()
    try:
        user = user_queries.find_user_by_id(db, update.effective_user.id)
        # This is a safe check in case the role changes.
        reply_markup = get_marketer_main_menu() if user and user.role.value == 'marketer' else get_customer_main_menu()
    finally:
        db.close()

    await update.message.reply_text(
        _('messages.back_to_main_menu'),
        reply_markup=reply_markup
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
    """Shows the marketer's referral statistics and commission balance."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        db_user = user_queries.find_user_by_id(db, user_id)
        if not db_user:
            return

        referred_count = user_queries.get_referred_users_count(db, referrer_id=user_id)
        commission_balance = db_user.commission_balance

        await update.message.reply_text(
            _('messages.marketer_stats',
              count=referred_count,
              commission=commission_balance)
        )
    finally:
        db.close()

async def request_payout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles a payout request from a marketer."""
    user = update.effective_user
    db = SessionLocal()
    try:
        db_user = user_queries.find_user_by_id(db, user.id)
        min_payout_str = setting_queries.get_setting(db, 'minimum_payout_amount', '50000')
        min_payout = int(min_payout_str)

        if db_user.commission_balance < min_payout:
            await update.message.reply_text(
                _('messages.marketer_payout_min_error', min_amount=min_payout, balance=db_user.commission_balance)
            )
            return

        admin_message = _('messages.admin_payout_request',
                          user_id=user.id,
                          first_name=user.first_name,
                          amount=db_user.commission_balance)

        # Inline keyboard for the admin to approve or reject
        keyboard = [
            [
                InlineKeyboardButton(_('buttons.payout.confirm'), callback_data=f'payout_confirm_{user.id}'),
                InlineKeyboardButton(_('buttons.payout.reject'), callback_data=f'payout_reject_{user.id}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=reply_markup)
        
        await update.message.reply_text(_('messages.marketer_payout_request_sent'))

    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()