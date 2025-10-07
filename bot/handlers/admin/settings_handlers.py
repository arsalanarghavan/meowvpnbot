from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)
from unittest.mock import MagicMock


from core.translator import translator, _
from bot.keyboards.reply_keyboards import get_admin_settings_menu
from bot.states.conversation_states import (
    ADMIN_SETTINGS_MENU, EDIT_TEXTS_NAVIGATE, AWAITING_NEW_TEXT_VALUE,
    PAYMENT_SETTINGS_MENU, GENERAL_SETTINGS_MENU, AWAITING_NEW_SETTING_VALUE, END_CONVERSION
)
from database.engine import SessionLocal
from database.queries import setting_queries
from core.config import ZARINPAL_MERCHANT_ID # Fallback

# --- Main Settings Menu ---
async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the admin settings menu."""
    text = _('messages.admin_settings_welcome')
    reply_markup = get_admin_settings_menu()
    
    # This function might be called from a message or a callback query (after exiting a sub-menu)
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif hasattr(update, 'callback_query') and update.callback_query:
        # If coming from a callback, we often need to send a new message to show the reply keyboard
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        
    return ADMIN_SETTINGS_MENU


# --- Payment Settings ---
async def start_payment_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays current payment settings and options to edit them."""
    db = SessionLocal()
    try:
        card_number = setting_queries.get_setting(db, 'card_number', _('messages.setting_not_set'))
        card_holder = setting_queries.get_setting(db, 'card_holder', _('messages.setting_not_set'))
        merchant_id = setting_queries.get_setting(db, 'zarinpal_merchant_id', ZARINPAL_MERCHANT_ID or _('messages.setting_not_set'))
    finally:
        db.close()

    text = _('messages.payment_settings_menu',
             card_number=card_number,
             card_holder=card_holder,
             merchant_id=merchant_id)

    keyboard = [
        [InlineKeyboardButton(_('buttons.payment_settings.edit_card_number'), callback_data='edit_setting_card_number')],
        [InlineKeyboardButton(_('buttons.payment_settings.edit_card_holder'), callback_data='edit_setting_card_holder')],
        [InlineKeyboardButton(_('buttons.payment_settings.edit_merchant_id'), callback_data='edit_setting_zarinpal_merchant_id')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Can be triggered by message (ReplyKeyboard) or callback (from another inline)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    return PAYMENT_SETTINGS_MENU

# --- General Settings ---
async def start_general_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays general settings like test account status."""
    db = SessionLocal()
    try:
        test_account_status = setting_queries.get_setting(db, 'test_account_enabled', 'True') == 'True'
    finally:
        db.close()
        
    status_text = "✅ " + _('enums.status.enabled') if test_account_status else "❌ " + _('enums.status.disabled')
    button_text = _('buttons.general_settings.disable_test_account') if test_account_status else _('buttons.general_settings.enable_test_account')

    text = _('messages.general_settings_menu', test_account_status=status_text)
    keyboard = [
        [InlineKeyboardButton(button_text, callback_data='toggle_test_account')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    return GENERAL_SETTINGS_MENU

async def toggle_test_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggles the test account feature on or off."""
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    try:
        is_enabled = setting_queries.get_setting(db, 'test_account_enabled', 'True') == 'True'
        new_status = 'False' if is_enabled else 'True'
        setting_queries.update_setting(db, 'test_account_enabled', new_status)
    finally:
        db.close()
        
    # Refresh the menu to show the new status
    await start_general_settings(query, context)
    return GENERAL_SETTINGS_MENU


# --- Shared logic for editing a setting ---
async def prompt_for_new_setting_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the admin for the new value of a setting."""
    query = update.callback_query
    await query.answer()
    
    key_to_edit = query.data.split('edit_setting_')[1]
    context.user_data['setting_key_to_edit'] = key_to_edit
    
    # Store the original message to edit it later, providing better UX
    context.user_data['message_to_edit_id'] = query.message.message_id
    
    await query.edit_message_text(_('messages.edit_setting_send_new_value', key_name=_(f'settings_keys.{key_to_edit}')))
    return AWAITING_NEW_SETTING_VALUE

async def receive_new_setting_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives and saves the new setting value."""
    new_value = update.message.text
    key = context.user_data.get('setting_key_to_edit')
    message_id = context.user_data.get('message_to_edit_id')

    # Delete the user's message containing the new value
    await update.message.delete()

    if not key:
        return ConversationHandler.END 

    db = SessionLocal()
    try:
        setting_queries.update_setting(db, key, new_value)
        # Inform the user of success briefly, maybe not needed if menu refreshes
        # await update.message.reply_text(_('messages.setting_updated_successfully'), quote=False)
    finally:
        db.close()
        
    context.user_data.pop('setting_key_to_edit', None)
    context.user_data.pop('message_to_edit_id', None)
    
    # Create a mock update object to refresh the correct menu by editing the original message
    mock_update = MagicMock()
    mock_update.callback_query = None
    mock_update.message = MagicMock()
    # We need edit_text method on the message object
    mock_update.message.edit_text = lambda text, reply_markup: context.bot.edit_message_text(
        chat_id=update.effective_chat.id, message_id=message_id, text=text, reply_markup=reply_markup)


    if key in ['card_number', 'card_holder', 'zarinpal_merchant_id']:
        await start_payment_settings(mock_update.message, context)
        return PAYMENT_SETTINGS_MENU
    else: # Fallback for other settings if added in the future
        await start_general_settings(mock_update.message, context)
        return GENERAL_SETTINGS_MENU

async def back_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exits a settings sub-menu and shows the main settings menu."""
    query = update.callback_query
    await query.answer()
    
    # Delete the inline menu and send a new message with the ReplyKeyboard
    await query.message.delete()
    await show_settings_menu(query, context)
    
    return END_CONVERSION


# --- Edit Texts Conversation ---
async def start_text_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the text editing conversation. Shows top-level keys."""
    text = _('messages.edit_texts_select_category')
    
    all_texts = translator.get_all_texts()
    keyboard = []
    for key in all_texts.keys():
        keyboard.append([InlineKeyboardButton(key, callback_data=f'navigate_{key}')])
    
    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)
    return EDIT_TEXTS_NAVIGATE


async def navigate_text_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Navigates through the JSON keys to find the text to edit."""
    query = update.callback_query
    await query.answer()

    path = query.data.split('_')[1:]
    path_str = ".".join(path)
    
    data = translator.get_all_texts()
    for key in path:
        data = data[key]
        
    keyboard = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path_str = f'{path_str}.{key}'
            display_text = key if isinstance(value, dict) else f"{key}: \"{str(value)[:20]}...\""
            keyboard.append([InlineKeyboardButton(display_text, callback_data=f'navigate_{new_path_str}')])
        
        parent_path = ".".join(path[:-1])
        back_callback = 'back_to_top_level' if not parent_path else f'navigate_{parent_path}'
        keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data=back_callback)])
        
        await query.edit_message_text(_('messages.edit_texts_select_key'), reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_TEXTS_NAVIGATE
        
    elif isinstance(data, str):
        context.user_data['key_to_edit'] = path_str
        text = _('messages.edit_texts_current_value', key=path_str, value=data)
        
        parent_path = ".".join(path[:-1])
        keyboard.append([InlineKeyboardButton(_('buttons.edit_texts.edit_this'), callback_data=f'edit_value_{path_str}')])
        keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data=f'navigate_{parent_path}')])

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_TEXTS_NAVIGATE


async def prompt_for_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user to send the new text value."""
    query = update.callback_query
    await query.answer()
    
    key_to_edit = query.data.split('edit_value_')[1]
    context.user_data['key_to_edit'] = key_to_edit
    context.user_data['message_to_edit_id'] = query.message.message_id
    
    await query.edit_message_text(_('messages.edit_texts_send_new_value', key=key_to_edit))
    return AWAITING_NEW_TEXT_VALUE


async def receive_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new text and updates the fa.json file."""
    new_value = update.message.text
    key_to_edit = context.user_data.get('key_to_edit')
    message_id = context.user_data.get('message_to_edit_id')

    await update.message.delete()
    
    if not key_to_edit:
        return EDIT_TEXTS_NAVIGATE

    success = translator.update_text(key_to_edit, new_value)
    
    # We don't send a success message, we just refresh the previous menu
    # This provides a much better user experience.

    context.user_data.pop('key_to_edit', None)
    context.user_data.pop('message_to_edit_id', None)
    
    # Simulate a callback query to navigate back to the parent key
    parent_path = ".".join(key_to_edit.split('.')[:-1])
    query.data = f'navigate_{parent_path}'
    
    # We need to mock the query message to be able to edit it
    query.message = MagicMock()
    query.message.edit_text = lambda text, reply_markup: context.bot.edit_message_text(
        chat_id=update.effective_chat.id, message_id=message_id, text=text, reply_markup=reply_markup
    )

    if parent_path:
        await navigate_text_keys(query, context)
    else: # If we were editing a top-level key
        await back_to_top_level(query, context)
        
    return EDIT_TEXTS_NAVIGATE


async def back_to_top_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles going back to the top-level key selection."""
    query = update.callback_query
    await query.answer()
    text = _('messages.edit_texts_select_category')
    all_texts = translator.get_all_texts()
    keyboard = []
    for key in all_texts.keys():
        keyboard.append([InlineKeyboardButton(key, callback_data=f'navigate_{key}')])
    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
    return EDIT_TEXTS_NAVIGATE