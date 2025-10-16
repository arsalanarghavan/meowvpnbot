from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.queries import panel_queries
from bot.states.conversation_states import (
    SELECTING_PANEL_TO_MANAGE, AWAITING_PANEL_NAME, AWAITING_PANEL_URL,
    AWAITING_PANEL_USERNAME, AWAITING_PANEL_PASSWORD, CONFIRMING_PANEL_CREATION,
    MANAGING_SPECIFIC_PANEL, SELECTING_FIELD_TO_EDIT_PANEL, AWAITING_NEW_PANEL_VALUE,
    CONFIRMING_PANEL_DELETION, ADMIN_SETTINGS_MENU
)
from bot.handlers.admin.settings_handlers import back_to_settings

# --- Helper Functions ---
def get_panels_management_keyboard(db: SessionLocal) -> InlineKeyboardMarkup:
    """Generates an inline keyboard with all panels for management."""
    panels = panel_queries.get_all_panels(db)
    keyboard = []
    if panels:
        for panel in panels:
            status_icon = "✅" if panel.is_active else "❌"
            button_text = f"{status_icon} {panel.name} ({panel.api_base_url})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'manage_panel_{panel.id}')])
    return InlineKeyboardMarkup(keyboard)

# --- Main Menu ---
async def start_panel_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the main menu for Marzban panel management."""
    db = SessionLocal()
    try:
        panels = panel_queries.get_all_panels(db)
        if not panels:
            text = _('messages.panel_management_no_panels')
        else:
            text = _('messages.panel_management_select_to_manage')

        panel_keyboard = get_panels_management_keyboard(db).inline_keyboard

        control_buttons = [
            [InlineKeyboardButton(_('buttons.panel_management.add'), callback_data='add_panel')],
            [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')]
        ]
        full_keyboard = panel_keyboard + control_buttons
        reply_markup = InlineKeyboardMarkup(full_keyboard)

        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    finally:
        db.close()

    return SELECTING_PANEL_TO_MANAGE

async def show_panel_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the management menu for a specific panel (Edit/Delete)."""
    query = update.callback_query
    await query.answer()

    panel_id_str = query.data.split('_')[-1]
    panel_id = int(panel_id_str)
    context.user_data['selected_panel_id'] = panel_id
    
    db = SessionLocal()
    try:
        panel = panel_queries.get_panel_by_id(db, panel_id)
        if not panel:
            await query.edit_message_text(_('messages.error_general'))
            return ConversationHandler.END

        text = _('messages.panel_management_menu_for_panel', name=panel.name)
        keyboard = [
            [
                InlineKeyboardButton(_('buttons.panel_management.edit'), callback_data='edit_panel'),
                InlineKeyboardButton(_('buttons.panel_management.delete'), callback_data='delete_panel')
            ],
            [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_panel_list')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()

    return MANAGING_SPECIFIC_PANEL

# --- Delete Panel Flow ---
async def start_delete_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for confirmation before deleting a panel."""
    query = update.callback_query
    await query.answer()
    panel_id = context.user_data['selected_panel_id']

    db = SessionLocal()
    try:
        panel = panel_queries.get_panel_by_id(db, panel_id)
        text = _('messages.panel_delete_confirmation', name=panel.name)
        keyboard = [
            [
                InlineKeyboardButton(_('buttons.general.confirm_delete'), callback_data=f'confirm_delete_panel'),
                InlineKeyboardButton(_('buttons.general.cancel'), callback_data=f'manage_panel_{panel_id}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()

    return CONFIRMING_PANEL_DELETION

async def confirm_delete_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes the panel from the database."""
    query = update.callback_query
    await query.answer()
    panel_id = context.user_data['selected_panel_id']

    db = SessionLocal()
    try:
        panel_queries.delete_panel_by_id(db, panel_id)
        await query.edit_message_text(_('messages.panel_deleted_successfully'))
    finally:
        db.close()
    
    context.user_data.clear()
    await start_panel_management(update, context)
    return SELECTING_PANEL_TO_MANAGE

# --- Add Panel Conversation ---
async def start_add_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add a new panel."""
    query = update.callback_query
    await query.answer()
    context.user_data['new_panel'] = {}
    await query.edit_message_text(_('messages.panel_enter_name'))
    return AWAITING_PANEL_NAME

async def receive_panel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['name'] = update.message.text
    await update.message.reply_text(_('messages.panel_enter_url'))
    return AWAITING_PANEL_URL

async def receive_panel_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['url'] = update.message.text.rstrip('/')
    await update.message.reply_text(_('messages.panel_enter_username'))
    return AWAITING_PANEL_USERNAME

async def receive_panel_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['username'] = update.message.text
    await update.message.reply_text(_('messages.panel_enter_password'))
    return AWAITING_PANEL_PASSWORD

async def receive_panel_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_panel']['password'] = update.message.text
    
    panel = context.user_data['new_panel']
    text = _('messages.panel_confirm_creation',
             name=panel['name'], url=panel['url'],
             username=panel['username'])
             
    keyboard = [
        [InlineKeyboardButton(_('buttons.general.confirm'), callback_data='confirm_create_panel')],
        [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_panel_creation')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
    return CONFIRMING_PANEL_CREATION

async def confirm_create_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    await start_panel_management(update, context)
    return SELECTING_PANEL_TO_MANAGE

async def cancel_panel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
        
    context.user_data.clear()
    await start_panel_management(update, context)
    return SELECTING_PANEL_TO_MANAGE

# --- Edit Panel Conversation ---
async def start_edit_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows options for which field of the panel to edit."""
    query = update.callback_query
    await query.answer()
    panel_id = context.user_data['selected_panel_id']
    db = SessionLocal()
    try:
        panel = panel_queries.get_panel_by_id(db, panel_id)
        
        text = _('messages.panel_edit_select_field', name=panel.name)
        keyboard = [
            [InlineKeyboardButton(_('buttons.panel_edit.name'), callback_data='edit_panel_field_name')],
            [InlineKeyboardButton(_('buttons.panel_edit.url'), callback_data='edit_panel_field_api_base_url')],
            [InlineKeyboardButton(_('buttons.panel_edit.username'), callback_data='edit_panel_field_username')],
            [InlineKeyboardButton(_('buttons.panel_edit.password'), callback_data='edit_panel_field_password')],
            [InlineKeyboardButton(_('buttons.general.back'), callback_data=f'manage_panel_{panel_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()
    return SELECTING_FIELD_TO_EDIT_PANEL

async def select_field_to_edit_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the field to edit and asks for the new value."""
    query = update.callback_query
    await query.answer()

    field = query.data.split('_')[3]
    context.user_data['field_to_edit'] = field

    await query.edit_message_text(_(f'messages.panel_enter_new_{field}'))
    return AWAITING_NEW_PANEL_VALUE

async def receive_new_panel_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new value and updates the panel in the database."""
    new_value = update.message.text
    field = context.user_data['field_to_edit']
    panel_id = context.user_data['selected_panel_id']
    
    if field == 'api_base_url':
        new_value = new_value.rstrip('/')

    update_data = {field: new_value}

    db = SessionLocal()
    try:
        panel_queries.update_panel(db, panel_id, update_data)
        await update.message.reply_text(_('messages.panel_updated_successfully'))
    finally:
        db.close()

    context.user_data.pop('field_to_edit', None)
    
    # Go back to the specific panel management menu by faking a callback query
    # We need to send a new message because we can't edit the user's text message
    await update.message.delete()
    query_data = f'manage_panel_{panel_id}'
    query = type('obj', (object,), {'data' : query_data, 'answer': lambda:None})
    update.callback_query = query
    await show_panel_management_menu(update, context)

    return MANAGING_SPECIFIC_PANEL


# --- Main Conversation Handler for Panel Management ---
panel_management_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.panel_management')}$"), start_panel_management)
    ],
    states={
        SELECTING_PANEL_TO_MANAGE: [
            CallbackQueryHandler(show_panel_management_menu, pattern='^manage_panel_'),
            CallbackQueryHandler(start_add_panel, pattern='^add_panel$'),
        ],
        MANAGING_SPECIFIC_PANEL: [
            CallbackQueryHandler(start_edit_panel, pattern='^edit_panel$'),
            CallbackQueryHandler(start_delete_panel, pattern='^delete_panel$'),
            CallbackQueryHandler(start_panel_management, pattern='^back_to_panel_list$')
        ],
        CONFIRMING_PANEL_DELETION: [
            CallbackQueryHandler(confirm_delete_panel, pattern='^confirm_delete_panel$'),
            CallbackQueryHandler(show_panel_management_menu, pattern='^manage_panel_')
        ],
        AWAITING_PANEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_name)],
        AWAITING_PANEL_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_url)],
        AWAITING_PANEL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_username)],
        AWAITING_PANEL_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_panel_password)],
        CONFIRMING_PANEL_CREATION: [
            CallbackQueryHandler(confirm_create_panel, pattern='^confirm_create_panel$'),
            CallbackQueryHandler(cancel_panel_creation, pattern='^cancel_panel_creation$')
        ],
        SELECTING_FIELD_TO_EDIT_PANEL: [
            CallbackQueryHandler(select_field_to_edit_panel, pattern='^edit_panel_field_'),
            CallbackQueryHandler(show_panel_management_menu, pattern='^manage_panel_')
        ],
        AWAITING_NEW_PANEL_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_panel_value)],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$'),
        CommandHandler('cancel', cancel_panel_creation) # A generic cancel
    ],
    map_to_parent={
        ConversationHandler.END: ADMIN_SETTINGS_MENU
    }
)