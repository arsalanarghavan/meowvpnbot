from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import translator, _
from bot.keyboards.reply_keyboards import get_admin_settings_menu
from bot.states.conversation_states import (
    ADMIN_SETTINGS_MENU, EDIT_TEXTS_NAVIGATE, AWAITING_NEW_TEXT_VALUE
)

# --- Main Settings Menu ---
async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the admin settings menu."""
    text = _('messages.admin_settings_welcome')
    reply_markup = get_admin_settings_menu()
    await update.message.reply_text(text, reply_markup=reply_markup)
    return ADMIN_SETTINGS_MENU


# --- Edit Texts Conversation ---
async def start_text_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the text editing conversation. Shows top-level keys."""
    text = _('messages.edit_texts_select_category')
    
    # Get top-level keys from the translator (e.g., messages, buttons)
    all_texts = translator.get_all_texts()
    keyboard = []
    for key in all_texts.keys():
        keyboard.append([InlineKeyboardButton(key, callback_data=f'navigate_{key}')])
    
    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # This handler is triggered by a ReplyKeyboard button, so we send a new message.
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
        # We are still navigating through dictionaries
        for key, value in data.items():
            new_path_str = f'{path_str}.{key}'
            # Show a snippet of the value if it's a string
            display_text = key if isinstance(value, dict) else f"{key}: \"{str(value)[:20]}...\""
            keyboard.append([InlineKeyboardButton(display_text, callback_data=f'navigate_{new_path_str}')])
        
        # Add a back button
        parent_path = ".".join(path[:-1])
        back_callback = 'back_to_top_level' if not parent_path else f'navigate_{parent_path}'
        keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data=back_callback)])
        
        await query.edit_message_text(_('messages.edit_texts_select_key'), reply_markup=InlineKeyboardMarkup(keyboard))
        return EDIT_TEXTS_NAVIGATE
        
    elif isinstance(data, str):
        # We've reached a string value that can be edited
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
    
    await query.edit_message_text(_('messages.edit_texts_send_new_value', key=key_to_edit))
    return AWAITING_NEW_TEXT_VALUE


async def receive_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new text and updates the fa.json file."""
    new_value = update.message.text
    key_to_edit = context.user_data.get('key_to_edit')
    
    if not key_to_edit:
        await update.message.reply_text(_('messages.error_general'))
        return EDIT_TEXTS_NAVIGATE

    success = translator.update_text(key_to_edit, new_value)
    
    if success:
        await update.message.reply_text(_('messages.edit_texts_updated_successfully'))
    else:
        await update.message.reply_text(_('messages.error_general'))

    # Go back to the parent key menu
    parent_path = ".".join(key_to_edit.split('.')[:-1])
    
    # Simulate a callback query to navigate back
    query_data = 'navigate_' + parent_path if parent_path else 'back_to_top_level'
    # To avoid sending a new message, we can't directly call the handler.
    # Instead, we just inform the user and they can continue from the menu.
    # For a better UX, one might refactor to pass the message object around to edit it.
    
    context.user_data.pop('key_to_edit', None)
    
    # Since we can't easily go back to the inline menu after a text message,
    # we restart the flow from the top level for simplicity.
    await start_text_edit(update, context)
    return EDIT_TEXTS_NAVIGATE


async def back_to_top_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles going back to the top-level key selection."""
    query = update.callback_query
    # Re-using the logic from start_text_edit but editing the message
    text = _('messages.edit_texts_select_category')
    all_texts = translator.get_all_texts()
    keyboard = []
    for key in all_texts.keys():
        keyboard.append([InlineKeyboardButton(key, callback_data=f'navigate_{key}')])
    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)
    return EDIT_TEXTS_NAVIGATE


async def back_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exits the text editing conversation and shows the main settings menu."""
    query = update.callback_query
    await query.answer()
    
    # We need to send a new message with the ReplyKeyboard
    await query.message.delete()
    await show_settings_menu(query.message, context)
    
    return ConversationHandler.END