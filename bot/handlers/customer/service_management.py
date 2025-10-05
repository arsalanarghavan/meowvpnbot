from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import qrcode
from io import BytesIO

from core.translator import _
from database.engine import SessionLocal
from database.queries import service_queries, user_queries, transaction_queries
from database.models.transaction import TransactionType, TransactionStatus
from bot.keyboards.inline_keyboards import get_user_services_keyboard, get_service_management_keyboard
from services.marzban_api import MarzbanAPI
from bot.states.conversation_states import AWAITING_SERVICE_NOTE, AWAITING_RENEWAL_CONFIRMATION, END_CONVERSATION

async def list_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the 'Manage Service' button, listing all active services."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        services = service_queries.get_user_active_services(db, user_id=user_id)
        
        if not services:
            await update.message.reply_text(_('messages.no_active_services'))
            return
            
        text = _('messages.select_service_to_manage')
        reply_markup = get_user_services_keyboard(services)
        await update.message.reply_text(text, reply_markup=reply_markup)
    finally:
        db.close()

async def show_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the detailed management menu for a selected service."""
    query = update.callback_query
    await query.answer()

    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service or service.user_id != query.from_user.id:
            await query.edit_message_text(_('messages.error_service_not_found'))
            return
        
        context.user_data['current_service_id'] = service.id
        
        api = MarzbanAPI()
        panel_user = await api.get_user(service.username_in_panel)
        if not panel_user:
            await query.edit_message_text(_('messages.error_service_not_found_panel'))
            return
            
        used_traffic_gb = round(panel_user.get('used_traffic', 0) / (1024**3), 2)
        data_limit_gb = round(panel_user.get('data_limit', 0) / (1024**3), 2) if panel_user.get('data_limit', 0) > 0 else "نامحدود"
        expire_ts = panel_user.get('expire', 0)
        expire_date = datetime.fromtimestamp(expire_ts).strftime('%Y-%m-%d') if expire_ts else "نامشخص"
        status_key = f"status.{panel_user.get('status', 'unknown')}"
        
        text = _('messages.service_details',
                 note=service.note or f"سرویس #{service.id}",
                 status=_(status_key),
                 used_traffic=used_traffic_gb,
                 data_limit=data_limit_gb,
                 expire_date=expire_date)
                 
        reply_markup = get_service_management_keyboard(service_id)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()

async def get_subscription_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides the subscription link for a service."""
    query = update.callback_query
    await query.answer()
    
    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        api = MarzbanAPI()
        panel_user = await api.get_user(service.username_in_panel)
        
        sub_link = panel_user.get('subscription_url', 'یافت نشد')
        text = _('messages.subscription_link', sub_link=sub_link)
        await context.bot.send_message(chat_id=query.from_user.id, text=text, parse_mode='Markdown')
    finally:
        db.close()

async def get_qr_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates and sends a QR code for the subscription link."""
    query = update.callback_query
    await query.answer(text=_('messages.generating_qr_code'))

    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        api = MarzbanAPI()
        panel_user = await api.get_user(service.username_in_panel)
        sub_link = panel_user.get('subscription_url')

        if not sub_link:
            await context.bot.send_message(chat_id=query.from_user.id, text=_('messages.error_general'))
            return

        img = qrcode.make(sub_link)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        await context.bot.send_photo(chat_id=query.from_user.id, photo=bio, caption=_('messages.qr_code_caption'))

    finally:
        db.close()
        
async def get_active_connections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows active IPs connected to a service."""
    query = update.callback_query
    await query.answer()

    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        api = MarzbanAPI()
        panel_user = await api.get_user(service.username_in_panel)
        
        connections = panel_user.get('online_at', [])
        
        if not connections:
            text = _('messages.no_active_connections')
        else:
            ip_list = "\n".join([f"`{conn['ip']}`" for conn in connections])
            text = _('messages.active_connections_list', count=len(connections), ip_list=ip_list)
            
        await context.bot.send_message(chat_id=query.from_user.id, text=text, parse_mode='Markdown')
    finally:
        db.close()
        
async def regenerate_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resets the user's UUID and provides a new subscription link."""
    query = update.callback_query
    await query.answer(text=_('messages.regenerating_uuid_wait'), show_alert=True)

    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        api = MarzbanAPI()
        new_panel_user = await api.reset_user_uuid(service.username_in_panel)

        if not new_panel_user:
            await context.bot.send_message(chat_id=query.from_user.id, text=_('messages.error_general'))
            return
            
        sub_link = new_panel_user.get('subscription_url', 'یافت نشد')
        text = _('messages.regenerate_uuid_success', sub_link=sub_link)
        await context.bot.send_message(chat_id=query.from_user.id, text=text, parse_mode='Markdown')

    finally:
        db.close()

async def back_to_main_menu_from_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deletes the service management menu and shows a confirmation."""
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    await context.bot.send_message(chat_id=query.from_user.id, text=_('messages.back_to_main_menu'))

# --- Change Note Conversation ---
async def start_change_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to change the service note."""
    query = update.callback_query
    await query.answer()
    service_id = int(query.data.split('_')[2])
    context.user_data['service_id_for_note'] = service_id
    await query.message.reply_text(_('messages.enter_new_note'))
    return AWAITING_SERVICE_NOTE

async def receive_new_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives and updates the service note."""
    new_note = update.message.text
    service_id = context.user_data.get('service_id_for_note')
    db = SessionLocal()
    try:
        service_queries.update_service_note(db, service_id, new_note)
        await update.message.reply_text(_('messages.note_changed_successfully'))
    finally:
        db.close()
    context.user_data.pop('service_id_for_note', None)
    await update.message.reply_text(_('messages.back_to_main_menu'))
    return END_CONVERSATION

async def cancel_change_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the change note conversation."""
    context.user_data.pop('service_id_for_note', None)
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSATION

change_note_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_change_note, pattern='^edit_note_')],
    states={
        AWAITING_SERVICE_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_note)]
    },
    fallbacks=[CommandHandler('cancel', cancel_change_note)]
)

# --- Renew Service Conversation ---
async def start_renewal_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the service renewal conversation."""
    query = update.callback_query
    await query.answer()
    
    service_id = int(query.data.split('_')[1]) # Pattern is renew_{service_id}
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service or service.user_id != query.from_user.id:
            await query.edit_message_text(_('messages.error_service_not_found'))
            return END_CONVERSATION
        
        context.user_data['service_to_renew_id'] = service.id
        plan = service.plan
        
        confirmation_text = _('messages.renewal_confirmation',
                              plan_name=plan.name,
                              price=plan.price)
        
        keyboard = [
            [InlineKeyboardButton(_('buttons.renewal.confirm'), callback_data=f'confirm_renew_{service_id}')],
            [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_renew')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)
        
    finally:
        db.close()
        
    return AWAITING_RENEWAL_CONFIRMATION

async def confirm_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirms and processes the service renewal."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    service_id = context.user_data.get('service_to_renew_id')
    
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        plan = service.plan
        db_user = user_queries.find_user_by_id(db, user_id)

        if db_user.wallet_balance < plan.price:
            await query.edit_message_text(_('messages.insufficient_balance', balance=db_user.wallet_balance))
            return END_CONVERSATION

        await query.edit_message_text(_('messages.renewing_service'))

        marzban_api = MarzbanAPI()
        await marzban_api.renew_user(service)
        
        user_queries.update_wallet_balance(db, user_id, -plan.price)
        tx = transaction_queries.create_transaction(db, user_id, plan.price, TransactionType.SERVICE_PURCHASE)
        transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.COMPLETED)
        service_queries.renew_service_record(db, service)

        await query.edit_message_text(_('messages.renewal_successful'))

    except Exception as e:
        await query.edit_message_text(_('messages.error_general'))
        print(f"Error during service renewal: {e}")
    finally:
        db.close()
    
    context.user_data.clear()
    return END_CONVERSATION

async def cancel_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the renewal process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSATION

renew_service_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_renewal_flow, pattern='^renew_')],
    states={
        AWAITING_RENEWAL_CONFIRMATION: [
            CallbackQueryHandler(confirm_renewal, pattern='^confirm_renew_'),
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_renewal, pattern='^cancel_renew$')]
)