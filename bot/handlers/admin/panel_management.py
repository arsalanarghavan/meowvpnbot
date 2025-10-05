from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.queries import panel_queries
from bot.states.conversation_states import (PANEL_MANAGEMENT_MENU, AWAITING_PANEL_NAME,
                                            AWAITING_PANEL_URL, AWAITING_PANEL_USERNAME,
                                            AWAITING_PANEL_PASSWORD, CONFIRMING_PANEL_CREATION,
                                            END_CONVERSION)

# --- Main Menu ---
async def start_panel_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the main menu for Marzban panel management."""
    db = SessionLocal()
    try:
        panels = panel_queries.get_all_panels(db)
        if not panels:
            text = _('messages.panel_management_no_panels')
        else:
            panel_list = "\n".join([f"- {p.name} ({p.api_base_url})"] for p in panels])
            text = _('messages.panel_management_menu', panels=panel_list)
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton(_('buttons.panel_management.add'), callback_data='add_panel')],
        [InlineKeyboardButton(_('buttons.general.back_to_admin_menu'), callback_data='back_to_admin_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if called from a button or a query
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        
    return PANEL_MANAGEMENT_MENU

# --- Add Panel Conversation ---
async def start_add_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add a new panel."""
    query = update.callback_query
    await query.answer()
    context.user_data['new_panel'] = {}
    await query.edit_message_text(_('messages.panel_enter_name'))
    return AWAITING_PANEL_NAME

async def receive_panel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the panel's friendly name."""
    context.user_data['new_panel']['name'] = update.message.text
    await update.message.reply_text(_('messages.panel_enter_url'))
    return AWAITING_PANEL_URL

async def receive_panel_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the panel's API base URL."""
    context.user_data['new_panel']['url'] = update.message.text.rstrip('/')
    await update.message.reply_text(_('messages.panel_enter_username'))
    return AWAITING_PANEL_USERNAME

async def receive_panel_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the panel's admin username."""
    context.user_data['new_panel']['username'] = update.message.text
    await update.message.reply_text(_('messages.panel_enter_password'))
    return AWAITING_PANEL_PASSWORD

async def receive_panel_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the panel's admin password and asks for confirmation."""
    context.user_data['new_panel']['password'] = update.message.text
    
    panel = context.user_data['new_panel']
    text = _('messages.panel_confirm_creation',
             name=panel['name'], url=panel['url'],
             username=panel['username'])
             
    keyboard = [
        [InlineKeyboardButton(_('buttons.general.confirm'), callback_data='confirm_create_panel')],
        [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_create_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
    return CONFIRMING_PANEL_CREATION

async def confirm_create_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the new panel to the database."""
    query = update.callback_query
    await query.answer()
    
    panel_data = context.user_data['new_panel']
    db = SessionLocal()
    try:
        panel_queries.create_panel(db, panel_data)
        await query.edit_message_text(_('messages.panel_created_successfully'))
    finally:
        db.close()
        
    context.user_data.clear()
    return END_CONVERSION

async def cancel_panel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the panel creation process."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(_('messages.operation_cancelled'))
    else:
        await update.message.reply_text(_('messages.operation_cancelled'))
        
    context.user_data.clear()
    return END_CONVERSION

# --- Conversation Handler ---
add_panel_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_panel, pattern='^add_panel$')],
    states={
        AWAITING_PANEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_name)],
        AWAITING_PANEL_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_url)],
        AWAITING_PANEL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_username)],
        AWAITING_PANEL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_password)],
        CONFIRMING_PANEL_CREATION: [
            CallbackQueryHandler(confirm_create_panel, pattern='^confirm_create_panel$'),
            CallbackQueryHandler(cancel_panel_creation, pattern='^cancel_create_panel$')
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_panel_creation)]
)