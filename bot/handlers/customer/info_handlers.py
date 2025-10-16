from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries

async def account_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's account information with comprehensive details."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        from database.queries import service_queries
        db_user = user_queries.find_or_create_user(db, user_id=user_id)
        
        # Get additional stats
        active_services = service_queries.get_user_active_services(db, user_id)
        referred_count = user_queries.get_referred_users_count(db, user_id) if db_user.role.value == 'marketer' else 0
        
        info_text = _('messages.account_info_enhanced',
                      user_id=db_user.user_id,
                      wallet_balance=db_user.wallet_balance,
                      commission_balance=db_user.commission_balance,
                      role=_(f'roles.{db_user.role.value}'),
                      active_services_count=len(active_services),
                      referred_count=referred_count,
                      member_since=db_user.created_at.strftime('%Y-%m-%d'))
    finally:
        db.close()
        
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays support information with multiple contact options."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    support_text = _('messages.support_info_enhanced')
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.support.contact_admin'), url=f"https://t.me/{_('config.support_id')}")],
        [InlineKeyboardButton(_('buttons.support.faq'), callback_data='faq_generic')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(support_text, reply_markup=reply_markup, parse_mode='Markdown')

async def applications_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays application download links with organized categories."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    apps_text = _('messages.applications_info_enhanced')
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.apps.android'), url='https://play.google.com/store/apps/details?id=com.v2ray.ang')],
        [InlineKeyboardButton(_('buttons.apps.ios'), url='https://apps.apple.com/app/shadowrocket/id932747118')],
        [InlineKeyboardButton(_('buttons.apps.windows'), url='https://github.com/2dust/v2rayN/releases')],
        [InlineKeyboardButton(_('buttons.apps.macos'), url='https://github.com/yanue/V2rayU/releases')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(apps_text, reply_markup=reply_markup, parse_mode='Markdown')