"""
Admin handlers for managing multiple card accounts.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler, 
                          CallbackQueryHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.models.queries import card_queries
from bot.states.conversation_states import (
    AWAITING_CARD_NUMBER, AWAITING_CARD_HOLDER, AWAITING_CARD_LIMIT,
    AWAITING_CARD_PRIORITY, AWAITING_CARD_NOTE, CONFIRMING_CARD_CREATION,
    SELECTING_CARD_TO_MANAGE, AWAITING_NEW_CARD_VALUE, END_CONVERSION
)
from core.telegram_logger import log_error

# ===== List and Display Cards =====

async def list_card_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all card accounts with their status and statistics."""
    db = SessionLocal()
    try:
        cards = card_queries.get_all_cards(db)
        
        if not cards:
            await update.message.reply_text(_('messages.admin_no_cards'))
            
            # Offer to add first card
            keyboard = [[InlineKeyboardButton(_('buttons.card_management.add_card'), callback_data='add_card_start')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(_('messages.admin_add_first_card'), reply_markup=reply_markup)
            return
        
        text = _('messages.admin_cards_list_header') + "\n\n"
        
        keyboard = []
        for card in cards:
            # Format card number (6037-****-****-1234)
            masked_card = f"{card.card_number[:4]}-****-****-{card.card_number[-4:]}"
            
            status_emoji = "✅" if card.is_active else "❌"
            limit_text = _('words.unlimited') if card.daily_limit == 0 else f"{card.daily_limit:,}"
            remaining = card.remaining_capacity()
            remaining_text = _('words.unlimited') if remaining == float('inf') else f"{remaining:,}"
            
            text += _('messages.admin_card_item',
                     priority=card.priority,
                     status=status_emoji,
                     card_number=masked_card,
                     holder=card.card_holder,
                     daily_limit=limit_text,
                     current_amount=f"{card.current_amount:,}",
                     remaining=remaining_text)
            text += "\n━━━━━━━━━━\n"
            
            # Add button for managing this card
            button_text = f"#{card.priority} - {masked_card}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'manage_card_{card.id}')])
        
        # Add button to add new card
        keyboard.append([InlineKeyboardButton(_('buttons.card_management.add_card'), callback_data='add_card_start')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await log_error(context, e, "list_card_accounts")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()

async def show_card_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows management options for a specific card."""
    query = update.callback_query
    await query.answer()
    
    card_id = int(query.data.split('_')[2])
    
    db = SessionLocal()
    try:
        card = card_queries.get_card_by_id(db, card_id)
        if not card:
            await query.edit_message_text(_('messages.error_general'))
            return
        
        masked_card = f"{card.card_number[:4]}-****-****-{card.card_number[-4:]}"
        stats = card_queries.get_card_statistics(db, card_id)
        
        text = _('messages.admin_card_details',
                card_number=masked_card,
                holder=card.card_holder,
                priority=card.priority,
                daily_limit=stats['daily_limit'] if stats['daily_limit'] > 0 else _('words.unlimited'),
                current_amount=f"{stats['current_amount']:,}",
                remaining=f"{stats['remaining_capacity']:,}" if stats['remaining_capacity'] != float('inf') else _('words.unlimited'),
                usage_percent=f"{stats['usage_percentage']:.1f}",
                status=_('enums.status.enabled') if stats['is_active'] else _('enums.status.disabled'),
                note=card.note or _('words.none'))
        
        keyboard = [
            [InlineKeyboardButton(_('buttons.card_management.edit_limit'), callback_data=f'edit_card_limit_{card_id}')],
            [InlineKeyboardButton(_('buttons.card_management.edit_priority'), callback_data=f'edit_card_priority_{card_id}')],
            [InlineKeyboardButton(_('buttons.card_management.edit_note'), callback_data=f'edit_card_note_{card_id}')],
            [InlineKeyboardButton(
                _('buttons.card_management.deactivate') if card.is_active else _('buttons.card_management.activate'),
                callback_data=f'toggle_card_{card_id}'
            )],
            [InlineKeyboardButton(_('buttons.card_management.delete'), callback_data=f'delete_card_confirm_{card_id}')],
            [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_cards_list')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        await log_error(context, e, "show_card_management_menu")
        await query.edit_message_text(_('messages.error_general'))
    finally:
        db.close()

# ===== Add Card Conversation =====

async def start_add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add a new card."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(_('messages.admin_enter_card_number'))
    return AWAITING_CARD_NUMBER

async def receive_card_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the card number."""
    card_number = update.message.text.replace('-', '').replace(' ', '')
    
    # Validate card number (should be 16 digits)
    if not card_number.isdigit() or len(card_number) != 16:
        await update.message.reply_text(_('messages.error_invalid_card_number'))
        return AWAITING_CARD_NUMBER
    
    context.user_data['new_card_number'] = card_number
    await update.message.reply_text(_('messages.admin_enter_card_holder'))
    return AWAITING_CARD_HOLDER

async def receive_card_holder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the card holder name."""
    card_holder = update.message.text.strip()
    
    if len(card_holder) < 3:
        await update.message.reply_text(_('messages.error_invalid_card_holder'))
        return AWAITING_CARD_HOLDER
    
    context.user_data['new_card_holder'] = card_holder
    await update.message.reply_text(_('messages.admin_enter_card_limit'))
    return AWAITING_CARD_LIMIT

async def receive_card_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the daily limit."""
    try:
        daily_limit = int(update.message.text)
        if daily_limit < 0:
            raise ValueError
        
        context.user_data['new_card_limit'] = daily_limit
        await update.message.reply_text(_('messages.admin_enter_card_priority'))
        return AWAITING_CARD_PRIORITY
        
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
        return AWAITING_CARD_LIMIT

async def receive_card_priority(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the priority."""
    try:
        priority = int(update.message.text)
        if priority < 0:
            raise ValueError
        
        context.user_data['new_card_priority'] = priority
        await update.message.reply_text(_('messages.admin_enter_card_note_optional'))
        return AWAITING_CARD_NOTE
        
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
        return AWAITING_CARD_PRIORITY

async def receive_card_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives optional note or skips it."""
    note = update.message.text.strip()
    
    if note.lower() == _('words.skip'):
        note = None
    else:
        context.user_data['new_card_note'] = note
    
    # Show confirmation
    card_number = context.user_data['new_card_number']
    masked = f"{card_number[:4]}-****-****-{card_number[-4:]}"
    
    limit_text = _('words.unlimited') if context.user_data['new_card_limit'] == 0 else f"{context.user_data['new_card_limit']:,}"
    
    confirmation_text = _('messages.admin_confirm_card_creation',
                         card_number=masked,
                         holder=context.user_data['new_card_holder'],
                         daily_limit=limit_text,
                         priority=context.user_data['new_card_priority'],
                         note=note or _('words.none'))
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.general.confirm'), callback_data='confirm_add_card')],
        [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_add_card')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(confirmation_text, reply_markup=reply_markup, parse_mode='Markdown')
    return CONFIRMING_CARD_CREATION

async def confirm_add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirms and creates the card account."""
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    try:
        card = card_queries.create_card_account(
            db,
            card_number=context.user_data['new_card_number'],
            card_holder=context.user_data['new_card_holder'],
            daily_limit=context.user_data['new_card_limit'],
            priority=context.user_data['new_card_priority'],
            note=context.user_data.get('new_card_note')
        )
        
        await query.edit_message_text(_('messages.admin_card_created_successfully'))
        
    except Exception as e:
        await log_error(context, e, "confirm_add_card")
        await query.edit_message_text(_('messages.error_general'))
    finally:
        db.close()
    
    context.user_data.clear()
    return END_CONVERSION

async def cancel_add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the add card process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSION

# ===== Card Actions =====

async def toggle_card_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggles the active status of a card."""
    query = update.callback_query
    await query.answer()
    
    card_id = int(query.data.split('_')[2])
    
    db = SessionLocal()
    try:
        card = card_queries.toggle_card_status(db, card_id)
        
        if card.is_active:
            await query.answer(_('messages.admin_card_activated'), show_alert=True)
        else:
            await query.answer(_('messages.admin_card_deactivated'), show_alert=True)
        
        # Refresh the management menu
        await show_card_management_menu(update, context)
        
    except Exception as e:
        await log_error(context, e, "toggle_card_status")
    finally:
        db.close()

async def delete_card_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for confirmation before deleting a card."""
    query = update.callback_query
    await query.answer()
    
    card_id = int(query.data.split('_')[3])
    context.user_data['card_to_delete'] = card_id
    
    keyboard = [
        [InlineKeyboardButton(_('buttons.general.confirm_delete'), callback_data=f'delete_card_confirmed_{card_id}')],
        [InlineKeyboardButton(_('buttons.general.cancel'), callback_data=f'manage_card_{card_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(_('messages.admin_confirm_card_deletion'), reply_markup=reply_markup)
    return END_CONVERSION

async def delete_card_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes the card after confirmation."""
    query = update.callback_query
    await query.answer()
    
    card_id = int(query.data.split('_')[3])
    
    db = SessionLocal()
    try:
        success = card_queries.delete_card(db, card_id)
        
        if success:
            await query.edit_message_text(_('messages.admin_card_deleted'))
        else:
            await query.edit_message_text(_('messages.error_general'))
            
    except Exception as e:
        await log_error(context, e, "delete_card_confirmed")
        await query.edit_message_text(_('messages.error_general'))
    finally:
        db.close()

async def back_to_cards_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Goes back to the cards list."""
    query = update.callback_query
    await query.answer()
    
    # Send a new message with the list (can't edit because we need reply keyboard)
    await query.message.delete()
    await list_card_accounts(update, context)

# ===== Edit Card Fields =====

async def start_edit_card_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts editing a specific field of a card."""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    field = parts[2]  # limit, priority, or note
    card_id = int(parts[3])
    
    context.user_data['editing_card_id'] = card_id
    context.user_data['editing_field'] = field
    
    if field == 'limit':
        await query.edit_message_text(_('messages.admin_enter_new_card_limit'))
    elif field == 'priority':
        await query.edit_message_text(_('messages.admin_enter_new_card_priority'))
    elif field == 'note':
        await query.edit_message_text(_('messages.admin_enter_new_card_note'))
    
    return AWAITING_NEW_CARD_VALUE

async def receive_new_card_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new value for the edited field."""
    field = context.user_data.get('editing_field')
    card_id = context.user_data.get('editing_card_id')
    
    db = SessionLocal()
    try:
        if field == 'limit':
            try:
                new_value = int(update.message.text)
                if new_value < 0:
                    raise ValueError
                card_queries.update_card(db, card_id, daily_limit=new_value)
            except (ValueError, TypeError):
                await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
                return AWAITING_NEW_CARD_VALUE
                
        elif field == 'priority':
            try:
                new_value = int(update.message.text)
                if new_value < 0:
                    raise ValueError
                card_queries.update_card(db, card_id, priority=new_value)
            except (ValueError, TypeError):
                await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
                return AWAITING_NEW_CARD_VALUE
                
        elif field == 'note':
            new_value = update.message.text.strip()
            card_queries.update_card(db, card_id, note=new_value if new_value else None)
        
        await update.message.reply_text(_('messages.admin_card_updated'))
        
    except Exception as e:
        await log_error(context, e, "receive_new_card_value")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()
    
    context.user_data.clear()
    return END_CONVERSION

# ===== Conversation Handler =====

add_card_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_card, pattern='^add_card_start$')],
    states={
        AWAITING_CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_card_number)],
        AWAITING_CARD_HOLDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_card_holder)],
        AWAITING_CARD_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_card_limit)],
        AWAITING_CARD_PRIORITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_card_priority)],
        AWAITING_CARD_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_card_note)],
        CONFIRMING_CARD_CREATION: [
            CallbackQueryHandler(confirm_add_card, pattern='^confirm_add_card$'),
            CallbackQueryHandler(cancel_add_card, pattern='^cancel_add_card$')
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_add_card, pattern='^cancel_add_card$')]
)

edit_card_field_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_edit_card_field, pattern='^edit_card_(limit|priority|note)_')],
    states={
        AWAITING_NEW_CARD_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_card_value)]
    },
    fallbacks=[]
)

