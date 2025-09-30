from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from core.translator import _
from database.engine import SessionLocal
from database.queries import service_queries
from bot.keyboards.inline_keyboards import get_user_services_keyboard, get_service_management_keyboard
from services.marzban_api import MarzbanAPI

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

    # Pattern is 'manage_service_{service_id}'
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
        
        text = _('messages.service_details',
                 note=service.note or f"سرویس #{service.id}",
                 status=_(f"status.{panel_user.get('status', 'unknown')}"),
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