from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries
from database.models.user import UserRole
from bot.keyboards.reply_keyboards import get_marketer_main_menu

async def earn_money_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the 'Earn Money' button - promotes users to marketers."""
    user = update.effective_user
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id=user.id)
        
        # Check if user is already a marketer
        if db_user.role == UserRole.marketer:
            # Show them the marketing panel
            bot_username = (await context.bot.get_me()).username
            invite_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
            
            referred_count = user_queries.get_referred_users_count(db, referrer_id=user.id)
            commission_balance = db_user.commission_balance
            
            message_text = _('messages.earn_money_already_marketer',
                           invite_link=invite_link,
                           referred_count=referred_count,
                           commission_balance=commission_balance)
            
            keyboard = [
                [InlineKeyboardButton(_('buttons.earn_money.open_marketer_panel'), 
                                     callback_data='open_marketer_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message_text, reply_markup=reply_markup)
        else:
            # Show them information about becoming a marketer
            message_text = _('messages.earn_money_intro')
            
            keyboard = [
                [InlineKeyboardButton(_('buttons.earn_money.become_marketer'), 
                                     callback_data='become_marketer')],
                [InlineKeyboardButton(_('buttons.earn_money.learn_more'), 
                                     callback_data='earn_money_learn_more')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message_text, reply_markup=reply_markup)
            
    finally:
        db.close()

async def become_marketer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback handler to promote a user to marketer."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id=user.id)
        
        if db_user.role != UserRole.marketer:
            # Promote to marketer
            user_queries.update_user_role(db, user.id, UserRole.marketer)
            
            # Generate their referral link
            bot_username = (await context.bot.get_me()).username
            invite_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
            
            success_message = _('messages.become_marketer_success', invite_link=invite_link)
            
            await query.edit_message_text(success_message)
            
            # Update their keyboard to marketer menu
            await context.bot.send_message(
                chat_id=user.id,
                text=_('messages.marketer_menu_updated'),
                reply_markup=get_marketer_main_menu()
            )
        else:
            await query.edit_message_text(_('messages.already_marketer'))
            
    finally:
        db.close()

async def learn_more_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows detailed information about the marketer program."""
    query = update.callback_query
    await query.answer()
    
    learn_more_text = _('messages.earn_money_learn_more_details')
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.earn_money.become_marketer'), 
                             callback_data='become_marketer')],
        [InlineKeyboardButton(_('buttons.general.back'), 
                             callback_data='back_to_earn_money')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(learn_more_text, reply_markup=reply_markup)

async def back_to_earn_money_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Goes back to the earn money main message."""
    query = update.callback_query
    await query.answer()
    
    message_text = _('messages.earn_money_intro')
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.earn_money.become_marketer'), 
                             callback_data='become_marketer')],
        [InlineKeyboardButton(_('buttons.earn_money.learn_more'), 
                             callback_data='earn_money_learn_more')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def open_marketer_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Opens the marketer panel for existing marketers."""
    query = update.callback_query
    await query.answer()
    
    from bot.keyboards.reply_keyboards import get_marketer_panel_menu
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=_('messages.marketer_panel_welcome'),
        reply_markup=get_marketer_panel_menu()
    )

