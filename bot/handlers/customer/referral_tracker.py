"""
Referral tracking and rewards system.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries
from database.models.user import UserRole

async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows referral information for any user (not just marketers)."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id)
        bot_username = (await context.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        referred_count = user_queries.get_referred_users_count(db, user_id)
        
        if db_user.role == UserRole.marketer:
            # Show full marketer stats
            active_referrals = user_queries.get_active_referrals_count(db, user_id)
            total_earned = user_queries.get_total_earned_commission(db, user_id)
            
            text = _('messages.referral_info_marketer',
                    invite_link=invite_link,
                    referred_count=referred_count,
                    active_referrals=active_referrals,
                    commission_balance=db_user.commission_balance,
                    total_earned=total_earned)
        else:
            # Show basic referral info
            text = _('messages.referral_info_customer',
                    invite_link=invite_link,
                    referred_count=referred_count)
            
        keyboard = []
        if db_user.role != UserRole.marketer:
            keyboard.append([InlineKeyboardButton(_('buttons.earn_money.become_marketer'), 
                                                  callback_data='become_marketer')])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    finally:
        db.close()

