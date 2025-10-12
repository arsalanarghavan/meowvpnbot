import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)
from unittest.mock import MagicMock

from core.translator import translator, _
from bot.keyboards.reply_keyboards import get_admin_settings_menu
from bot.states.conversation_states import (
    ADMIN_SETTINGS_MENU, EDIT_TEXTS_NAVIGATE, AWAITING_NEW_TEXT_VALUE,
    PAYMENT_SETTINGS_MENU, GENERAL_SETTINGS_MENU, AWAITING_NEW_SETTING_VALUE,
    COMMISSION_SETTINGS_MENU, AWAITING_COMMISSION_THRESHOLD, AWAITING_COMMISSION_RATE,
    END_CONVERSION
)
from database.engine import SessionLocal
from database.queries import setting_queries
from core.config import ZARINPAL_MERCHANT_ID # Fallback
from core.telegram_logger import log_error

# --- Main Settings Menu ---
async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the admin settings menu."""
    text = _('messages.admin_settings_welcome')
    reply_markup = get_admin_settings_menu()

    try:
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif hasattr(update, 'callback_query') and update.callback_query:
            # Delete the previous inline keyboard message and send a new one with the reply keyboard
            await update.callback_query.message.delete()
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

    except Exception as e:
        await log_error(context, e, "show_settings_menu")

    return ADMIN_SETTINGS_MENU


# --- Payment Settings ---
async def start_payment_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays current payment settings and options to edit them."""
    db = SessionLocal()
    try:
        card_number = setting_queries.get_setting(db, 'card_number', _('messages.setting_not_set'))
        card_holder = setting_queries.get_setting(db, 'card_holder', _('messages.setting_not_set'))
        merchant_id = setting_queries.get_setting(db, 'zarinpal_merchant_id', ZARINPAL_MERCHANT_ID or _('messages.setting_not_set'))
        min_payout = setting_queries.get_setting(db, 'minimum_payout_amount', '50000') # Default 50,000
    except Exception as e:
        await log_error(context, e, "loading payment settings")
        card_number = card_holder = merchant_id = min_payout = _('messages.error_general')
    finally:
        db.close()

    text = _('messages.payment_settings_menu',
             card_number=card_number,
             card_holder=card_holder,
             merchant_id=merchant_id,
             min_payout=min_payout)

    keyboard = [
        [InlineKeyboardButton(_('buttons.payment_settings.edit_card_number'), callback_data='edit_setting_card_number')],
        [InlineKeyboardButton(_('buttons.payment_settings.edit_card_holder'), callback_data='edit_setting_card_holder')],
        [InlineKeyboardButton(_('buttons.payment_settings.edit_merchant_id'), callback_data='edit_setting_zarinpal_merchant_id')],
        [InlineKeyboardButton(_('buttons.payment_settings.edit_min_payout'), callback_data='edit_setting_minimum_payout_amount')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        await log_error(context, e, "start_payment_settings")


    return PAYMENT_SETTINGS_MENU

# --- General Settings ---
async def start_general_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays general settings like test account status."""
    db = SessionLocal()
    try:
        test_account_status = setting_queries.get_setting(db, 'test_account_enabled', 'True') == 'True'
    except Exception as e:
        await log_error(context, e, "loading general settings")
        test_account_status = False # Default to a safe value on error
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

    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        await log_error(context, e, "start_general_settings")

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
    except Exception as e:
        await log_error(context, e, "toggle_test_account")
    finally:
        db.close()

    await start_general_settings(query, context)
    return GENERAL_SETTINGS_MENU


# --- Commission Tiers Settings ---
async def start_commission_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the current commission tiers and options to manage them."""
    db = SessionLocal()
    try:
        tiers_json = setting_queries.get_setting(db, 'commission_tiers', '[]')
        tiers = sorted(json.loads(tiers_json), key=lambda x: x['threshold'])
    except (json.JSONDecodeError, TypeError, Exception) as e:
        await log_error(context, e, "loading commission settings")
        tiers = []
    finally:
        db.close()

    tiers_text = ""
    if not tiers:
        tiers_text = _('messages.commission_no_tiers_set')
    else:
        for i, tier in enumerate(tiers):
            tiers_text += _('messages.commission_tier_item',
                           threshold=tier['threshold'],
                           rate=tier['rate'],
                           index=i) + "\n"

    text = _('messages.commission_settings_menu', tiers=tiers_text)
    keyboard = [[InlineKeyboardButton(_('buttons.commission_settings.add_tier'), callback_data='add_tier')]]

    for i, tier in enumerate(tiers):
        keyboard.append([
            InlineKeyboardButton(
                _('buttons.commission_settings.delete_tier', threshold=tier['threshold']),
                callback_data=f'delete_tier_{i}'
            )
        ])

    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        await log_error(context, e, "start_commission_settings")

    return COMMISSION_SETTINGS_MENU

async def prompt_for_new_commission_tier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for the threshold (number of users) for the new tier."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.commission_enter_threshold'))
    return AWAITING_COMMISSION_THRESHOLD

async def receive_commission_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the threshold and asks for the commission rate."""
    try:
        threshold = int(update.message.text)
        if threshold < 0: raise ValueError
        context.user_data['new_tier_threshold'] = threshold
        await update.message.reply_text(_('messages.commission_enter_rate'))
        return AWAITING_COMMISSION_RATE
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
        return AWAITING_COMMISSION_THRESHOLD

async def receive_commission_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the rate, saves the new tier, and refreshes the menu."""
    try:
        rate = int(update.message.text)
        if not 0 <= rate <= 100: raise ValueError
        threshold = context.user_data['new_tier_threshold']
        
        db = SessionLocal()
        try:
            tiers_json = setting_queries.get_setting(db, 'commission_tiers', '[]')
            tiers = json.loads(tiers_json)
            
            if any(t['threshold'] == threshold for t in tiers):
                await update.message.reply_text(_('messages.commission_error_duplicate_threshold'))
                return COMMISSION_SETTINGS_MENU

            tiers.append({"threshold": threshold, "rate": rate})
            setting_queries.update_setting(db, 'commission_tiers', json.dumps(tiers))
        finally:
            db.close()

    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.commission_error_invalid_rate'))
        return AWAITING_COMMISSION_RATE
    except Exception as e:
        await log_error(context, e, "receive_commission_rate")
    finally:
        context.user_data.pop('new_tier_threshold', None)
        
    await start_commission_settings(update, context)
    return COMMISSION_SETTINGS_MENU

async def delete_commission_tier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes a specific commission tier."""
    query = update.callback_query
    await query.answer()
    tier_index = int(query.data.split('_')[2])

    db = SessionLocal()
    try:
        tiers_json = setting_queries.get_setting(db, 'commission_tiers', '[]')
        tiers = json.loads(tiers_json)
        if 0 <= tier_index < len(tiers):
            tiers.pop(tier_index)
            setting_queries.update_setting(db, 'commission_tiers', json.dumps(tiers))
    except (json.JSONDecodeError, IndexError, Exception) as e:
        await log_error(context, e, "deleting commission tier")
    finally:
        db.close()
        
    await start_commission_settings(query, context)
    return COMMISSION_SETTINGS_MENU


# --- Shared logic for editing a setting ---
async def prompt_for_new_setting_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the admin for the new value of a setting."""
    query = update.callback_query
    await query.answer()
    
    key_to_edit = query.data.split('edit_setting_')[1]
    context.user_data['setting_key_to_edit'] = key_to_edit
    context.user_data['message_to_edit_id'] = query.message.message_id
    
    try:
        await query.edit_message_text(_('messages.edit_setting_send_new_value', key_name=_(f'settings_keys.{key_to_edit}')))
    except Exception as e:
        await log_error(context, e, "prompt_for_new_setting_value")
        
    return AWAITING_NEW_SETTING_VALUE

async def receive_new_setting_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives and saves the new setting value."""
    new_value = update.message.text
    key = context.user_data.get('setting_key_to_edit')
    message_id = context.user_data.get('message_to_edit_id')

    await update.message.delete()

    if not key:
        return ConversationHandler.END 

    db = SessionLocal()
    try:
        setting_queries.update_setting(db, key, new_value)
    except Exception as e:
        await log_error(context, e, "receive_new_setting_value")
    finally:
        db.close()
        
    context.user_data.pop('setting_key_to_edit', None)
    context.user_data.pop('message_to_edit_id', None)
    
    # Mock an update object to refresh the menu correctly
    mock_query = MagicMock()
    mock_query.message = MagicMock()
    mock_query.message.message_id = message_id
    mock_query.message.edit_text = lambda text, reply_markup: context.bot.edit_message_text(
        chat_id=update.effective_chat.id, message_id=message_id, text=text, reply_markup=reply_markup)

    if key in ['card_number', 'card_holder', 'zarinpal_merchant_id', 'minimum_payout_amount']:
        await start_payment_settings(mock_query, context)
        return PAYMENT_SETTINGS_MENU
    else:
        await start_general_settings(mock_query, context)
        return GENERAL_SETTINGS_MENU

async def back_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exits a settings sub-menu and shows the main settings menu."""
    query = update.callback_query
    await query.answer()
    
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

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        
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

    translator.update_text(key_to_edit, new_value)
    
    context.user_data.pop('key_to_edit', None)
    context.user_data.pop('message_to_edit_id', None)
    
    parent_path = ".".join(key_to_edit.split('.')[:-1])
    
    # Mock a query object to navigate back
    mock_query = MagicMock()
    mock_query.data = f'navigate_{parent_path}'
    mock_query.answer = lambda: None
    mock_query.message = MagicMock()
    mock_query.message.edit_text = lambda text, reply_markup: context.bot.edit_message_text(
        chat_id=update.effective_chat.id, message_id=message_id, text=text, reply_markup=reply_markup
    )

    if parent_path:
        await navigate_text_keys(mock_query, context)
    else:
        await back_to_top_level(mock_query, context)
        
    return EDIT_TEXTS_NAVIGATE


async def back_to_top_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles going back to the top-level key selection."""
    query = update.callback_query
    await query.answer()
    await start_text_edit(query, context) # Simply restart the text edit flow
    return EDIT_TEXTS_NAVIGATE

# --- Conversation Handlers ---
edit_texts_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.edit_texts')}$"), start_text_edit)],
    states={
        EDIT_TEXTS_NAVIGATE: [
            CallbackQueryHandler(navigate_text_keys, pattern='^navigate_'),
            CallbackQueryHandler(prompt_for_new_value, pattern='^edit_value_'),
            CallbackQueryHandler(back_to_top_level, pattern='^back_to_top_level$')
        ],
        AWAITING_NEW_TEXT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_value)]
    },
    fallbacks=[CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$')],
    map_to_parent={END_CONVERSION: ADMIN_SETTINGS_MENU}
)

payment_settings_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.payment_settings')}$"), start_payment_settings)],
    states={
        PAYMENT_SETTINGS_MENU: [CallbackQueryHandler(prompt_for_new_setting_value, pattern='^edit_setting_')],
        AWAITING_NEW_SETTING_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_setting_value)]
    },
    fallbacks=[CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$')],
    map_to_parent={END_CONVERSION: ADMIN_SETTINGS_MENU}
)

general_settings_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.general_settings')}$"), start_general_settings)],
    states={
        GENERAL_SETTINGS_MENU: [CallbackQueryHandler(toggle_test_account, pattern='^toggle_test_account$')]
    },
    fallbacks=[CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$')],
    map_to_parent={END_CONVERSION: ADMIN_SETTINGS_MENU}
)

commission_settings_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.commission_settings')}$"), start_commission_settings)],
    states={
        COMMISSION_SETTINGS_MENU: [
            CallbackQueryHandler(prompt_for_new_commission_tier, pattern='^add_tier$'),
            CallbackQueryHandler(delete_commission_tier, pattern='^delete_tier_')
        ],
        AWAITING_COMMISSION_THRESHOLD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_commission_threshold)],
        AWAITING_COMMISSION_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_commission_rate)]
    },
    fallbacks=[CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$')],
    map_to_parent={END_CONVERSION: ADMIN_SETTINGS_MENU}
)