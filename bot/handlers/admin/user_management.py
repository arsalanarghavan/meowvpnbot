from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, service_queries
from database.models.user import UserRole
from bot.keyboards.inline_keyboards import get_user_management_keyboard
from bot.states.conversation_states import (AWAITING_USER_ID_FOR_SEARCH,
                                            AWAITING_AMOUNT_TO_ADD, AWAITING_ROLE_SELECTION, END_CONVERSATION)
from core.telegram_logger import log_error

# --- User Search Conversation ---
async def start_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the user search conversation."""
    await update.message.reply_text(_('messages.admin_enter_user_id'))
    return AWAITING_USER_ID_FOR_SEARCH

async def receive_user_id_and_show_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a user ID, searches for the user, and displays their info."""
    try:
        user_id = int(update.message.text)
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_user_id'))
        return AWAITING_USER_ID_FOR_SEARCH

    db = SessionLocal()
    try:
        db_user = user_queries.find_user_by_id(db, user_id=user_id)
        if not db_user:
            await update.message.reply_text(_('messages.admin_user_not_found'))
            return AWAITING_USER_ID_FOR_SEARCH

        user_info_text = _('messages.admin_user_details',
                           user_id=db_user.user_id,
                           role=_(f'roles.{db_user.role.value}'),
                           wallet_balance=db_user.wallet_balance,
                           created_at=db_user.created_at.strftime('%Y-%m-%d %H:%M'),
                           is_active="فعال" if db_user.is_active else "مسدود")
        reply_markup = get_user_management_keyboard(user_id)
        await update.message.reply_text(user_info_text, reply_markup=reply_markup)
        return END_CONVERSATION
    except Exception as e:
        await log_error(context, e, "receive_user_id_and_show_info")
        await update.message.reply_text(_('messages.error_general'))
        return END_CONVERSATION
    finally:
        db.close()

async def cancel_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the user search process."""
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSATION

user_search_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.admin_panel.user_management')}$"), start_user_search)],
    states={AWAITING_USER_ID_FOR_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_id_and_show_info)]},
    fallbacks=[CommandHandler('cancel', cancel_user_search)]
)

# --- Standalone Callback Handlers (Actions on a user) ---
async def view_user_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback handler for admin to view a user's services."""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[3])
    db = SessionLocal()
    try:
        services = service_queries.get_user_active_services(db, user_id=user_id)
        if not services:
            await query.edit_message_text(query.message.text + "\n\n" + _('messages.admin_user_has_no_services'))
            return

        services_list_text = "\n\n" + _('messages.admin_user_services_header') + "\n"
        for service in services:
            services_list_text += _('messages.admin_user_service_item',
                                    id=service.id,
                                    plan_name=service.plan.name,
                                    expire_date=service.expire_date.strftime('%Y-%m-%d'))

        await query.edit_message_text(query.message.text + services_list_text, reply_markup=get_user_management_keyboard(user_id))
    except Exception as e:
        await log_error(context, e, "view_user_services")
    finally:
        db.close()

# --- Add Balance Conversation ---
async def start_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add balance to a user's wallet."""
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split('_')[3])
    context.user_data['target_user_id'] = user_id

    await query.edit_message_text(query.message.text + "\n\n" + _('messages.admin_enter_amount_to_add'))
    return AWAITING_AMOUNT_TO_ADD

async def receive_amount_and_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the amount and updates the user's wallet balance."""
    try:
        amount = int(update.message.text)
        user_id = context.user_data['target_user_id']
    except (ValueError, TypeError, KeyError):
        await update.message.reply_text(_('messages.error_invalid_amount_or_user'))
        context.user_data.clear()
        return END_CONVERSATION

    db = SessionLocal()
    try:
        user_queries.update_wallet_balance(db, user_id, amount)

        await update.message.reply_text(_('messages.admin_balance_added_successfully', amount=amount, user_id=user_id))

        await context.bot.send_message(
            chat_id=user_id,
            text=_('messages.user_balance_added_by_admin', amount=amount)
        )
    except Exception as e:
        await log_error(context, e, "receive_amount_and_update")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()

    context.user_data.clear()
    return END_CONVERSATION

async def cancel_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the add balance process."""
    context.user_data.clear()
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSATION

add_balance_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_balance, pattern='^admin_add_balance_')],
    states={
        AWAITING_AMOUNT_TO_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount_and_update)]
    },
    fallbacks=[CommandHandler('cancel', cancel_add_balance)]
)

# --- Change Role Conversation ---
async def start_change_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the admin to select a new role for the user."""
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[3])
    context.user_data['target_user_id'] = user_id

    keyboard = [
        [InlineKeyboardButton(_(f'roles.{role.value}'), callback_data=f'set_role_{role.name}')]
        for role in UserRole if role != UserRole.admin # Admin role cannot be set manually
    ]
    keyboard.append([InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_role_change')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(query.message.text + "\n\n" + _('messages.admin_select_user_role'), reply_markup=reply_markup)
    return AWAITING_ROLE_SELECTION

async def set_user_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sets the new role for the user and ends the conversation."""
    query = update.callback_query
    await query.answer()

    user_id = context.user_data.get('target_user_id')
    
    try:
        new_role_name = query.data.split('set_role_')[1]
        new_role = UserRole[new_role_name]
    except (IndexError, KeyError):
        await query.edit_message_text(_('messages.error_general'))
        context.user_data.clear()
        return END_CONVERSATION

    db = SessionLocal()
    try:
        user_queries.update_user_role(db, user_id, new_role)
        await query.edit_message_text(_('messages.admin_user_role_updated', role=_(f'roles.{new_role.value}')))
    except Exception as e:
        await log_error(context, e, "set_user_role")
        await query.edit_message_text(_('messages.error_general'))
    finally:
        db.close()
    
    context.user_data.clear()
    return END_CONVERSATION

async def cancel_change_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the role change process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSATION

change_role_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_change_role, pattern='^admin_change_role_')],
    states={
        AWAITING_ROLE_SELECTION: [CallbackQueryHandler(set_user_role, pattern='^set_role_')]
    },
    fallbacks=[CallbackQueryHandler(cancel_change_role, pattern='^cancel_role_change$')]
)