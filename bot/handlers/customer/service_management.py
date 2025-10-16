from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import qrcode
from io import BytesIO

from core.translator import _
from database.engine import SessionLocal
from database.queries import (service_queries, user_queries, transaction_queries, panel_queries)
from database.models.transaction import TransactionType, TransactionStatus
from bot.keyboards.inline_keyboards import (get_user_services_keyboard, get_service_management_keyboard,
                                            get_service_access_section_keyboard, get_service_management_section_keyboard,
                                            get_service_info_section_keyboard)
from services.marzban_api import MarzbanAPI
from bot.states.conversation_states import (AWAITING_SERVICE_NOTE, AWAITING_RENEWAL_CONFIRMATION,
                                            AWAITING_CANCELLATION_CONFIRMATION, END_CONVERSION)
from bot.logic.commission import award_commission_for_purchase
from core.telegram_logger import log_error

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
    except Exception as e:
        await log_error(context, e, "list_services")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()

async def show_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, service_id_override: int = None) -> None:
    """Shows the detailed management menu for a selected service."""
    query = update.callback_query
    db = SessionLocal()
    try:
        user_id = None
        service_id = None

        if query:
            await query.answer()
            user_id = query.from_user.id
            service_id = service_id_override if service_id_override is not None else int(query.data.split('_')[2])
        elif service_id_override is not None:
            user_id = context.user_data.get('cancellation_user_id', update.effective_user.id)
            service_id = service_id_override
        else:
            return

        service = service_queries.get_service_by_id(db, service_id)
        if not service or service.user_id != user_id:
            if query: await query.edit_message_text(_('messages.error_service_not_found'))
            return

        context.user_data['current_service_id'] = service.id

        all_panels = panel_queries.get_all_panels(db)
        if not all_panels:
             if query: await query.edit_message_text(_('messages.no_panels_configured'))
             return

        # We only need to contact one active panel to get user status, assuming they are synced
        panel_user = None
        for panel in all_panels:
            if panel.is_active:
                try:
                    api = MarzbanAPI(panel)
                    panel_user = await api.get_user(service.username_in_panel)
                    if panel_user:
                        break # Found user on a panel, no need to check others
                except Exception:
                    continue # Try next panel

        if not panel_user:
            if query: await query.edit_message_text(_('messages.error_service_not_found_panel'))
            return

        used_traffic_gb = round(panel_user.get('used_traffic', 0) / (1024**3), 2)
        data_limit_gb = round(panel_user.get('data_limit', 0) / (1024**3), 2) if panel_user.get('data_limit', 0) > 0 else _('words.unlimited')
        expire_ts = panel_user.get('expire', 0)
        expire_date = datetime.fromtimestamp(expire_ts).strftime('%Y-%m-%d') if expire_ts else _('words.unknown')
        status_key = f"status.{panel_user.get('status', 'unknown')}"
        auto_renew_status = "✅ " + _('enums.status.enabled') if service.auto_renew else "❌ " + _('enums.status.disabled')
        alerts_status = "✅ " + _('enums.status.enabled') if service.connection_alerts else "❌ " + _('enums.status.disabled')

        text = _('messages.service_details_full',
                 note=service.note or f"{_('words.service')} #{service.id}",
                 status=_(status_key),
                 used_traffic=used_traffic_gb,
                 data_limit=data_limit_gb,
                 expire_date=expire_date,
                 auto_renew=auto_renew_status,
                 alerts_status=alerts_status)

        reply_markup = get_service_management_keyboard(service_id)

        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        elif 'cancellation_message_id' in context.user_data:
            await context.bot.edit_message_text(chat_id=user_id, message_id=context.user_data['cancellation_message_id'], text=text, reply_markup=reply_markup)

    except Exception as e:
        await log_error(context, e, "show_service_menu")
        if query: await query.edit_message_text(_('messages.error_general'))
    finally:
        db.close()

async def get_subscription_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides the combined subscription link from all active panels."""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        service_id = int(query.data.split('_')[2])
        service = service_queries.get_service_by_id(db, service_id)
        if not service:
            await query.message.reply_text(_('messages.error_service_not_found'))
            return

        panels = panel_queries.get_all_panels(db)
        user_details_list = []
        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                user_details = await api.get_user(service.username_in_panel)
                if user_details:
                    user_details_list.append(user_details)
            except Exception as e:
                await log_error(context, e, f"Could not fetch user {service.username_in_panel} from panel {panel.name} for sub link")

        if not user_details_list:
            await query.message.reply_text(_('messages.error_all_panels_failed_user'))
            return

        combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
        text = _('messages.subscription_link', sub_link=combined_sub_link)
        await query.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await log_error(context, e, "get_subscription_link")
        await query.message.reply_text(_('messages.error_general'))
    finally:
        db.close()

async def get_qr_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates and sends a QR code for the combined subscription link."""
    query = update.callback_query
    await query.answer(text=_('messages.generating_qr_code'))

    db = SessionLocal()
    try:
        service_id = int(query.data.split('_')[2])
        service = service_queries.get_service_by_id(db, service_id)
        if not service: return

        panels = panel_queries.get_all_panels(db)
        user_details_list = []
        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                user_details = await api.get_user(service.username_in_panel)
                if user_details:
                    user_details_list.append(user_details)
            except Exception as e:
                await log_error(context, e, f"Could not fetch user {service.username_in_panel} from panel {panel.name} for QR")

        sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)

        if "یافت نشد" in sub_link: # Fallback text from MarzbanAPI
            await context.bot.send_message(chat_id=query.from_user.id, text=_('messages.error_general'))
            return

        img = qrcode.make(sub_link)
        bio = BytesIO()
        bio.name = 'qrcode.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        await context.bot.send_photo(chat_id=query.from_user.id, photo=bio, caption=_('messages.qr_code_caption'))
    except Exception as e:
        await log_error(context, e, "get_qr_code")
    finally:
        db.close()

async def get_active_connections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows active IPs connected to a service from all active panels."""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        service_id = int(query.data.split('_')[2])
        service = service_queries.get_service_by_id(db, service_id)
        if not service: return

        panels = panel_queries.get_all_panels(db)
        all_ips = set()

        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                panel_user = await api.get_user(service.username_in_panel)
                if panel_user and panel_user.get('online_at'):
                    for conn in panel_user['online_at']:
                        all_ips.add(conn['ip'])
            except Exception as e:
                await log_error(context, e, f"Could not get connections from panel {panel.name}")

        if not all_ips:
            text = _('messages.no_active_connections')
        else:
            ip_list = "\n".join([f"`{ip}`" for ip in all_ips])
            text = _('messages.active_connections_list', count=len(all_ips), ip_list=ip_list)

        await query.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await log_error(context, e, "get_active_connections")
    finally:
        db.close()

async def regenerate_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resets the user's UUID on all active panels and provides a new subscription link."""
    query = update.callback_query
    await query.answer(text=_('messages.regenerating_uuid_wait'), show_alert=True)

    db = SessionLocal()
    try:
        service_id = int(query.data.split('_')[2])
        service = service_queries.get_service_by_id(db, service_id)
        if not service: return

        panels = panel_queries.get_all_panels(db)
        user_details_list = []
        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                new_panel_user = await api.reset_user_uuid(service.username_in_panel)
                if new_panel_user:
                    user_details_list.append(new_panel_user)
            except Exception as e:
                await log_error(context, e, f"Failed to reset UUID on panel {panel.name}")

        if not user_details_list:
            await context.bot.send_message(chat_id=query.from_user.id, text=_('messages.error_all_panels_failed_user'))
            return

        sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
        text = _('messages.regenerate_uuid_success', sub_link=sub_link)
        await query.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await log_error(context, e, "regenerate_uuid")
    finally:
        db.close()

async def back_to_main_menu_from_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.delete()

async def show_service_section(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows a specific section of service management."""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split('_')
    section = data_parts[1]  # access, manage, or info
    service_id = int(data_parts[2])
    
    if section == 'access':
        text = _('messages.service_access_section')
        reply_markup = get_service_access_section_keyboard(service_id)
    elif section == 'manage':
        text = _('messages.service_management_section')
        reply_markup = get_service_management_section_keyboard(service_id)
    elif section == 'info':
        text = _('messages.service_info_section')
        reply_markup = get_service_info_section_keyboard(service_id)
    else:
        return
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def toggle_auto_renew_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    service_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        service = service_queries.toggle_auto_renew(db, service_id)
        if service.auto_renew:
            await query.answer(_('messages.auto_renew_enabled'), show_alert=True)
        else:
            await query.answer(_('messages.auto_renew_disabled'), show_alert=True)
    except Exception as e:
        await log_error(context, e, "toggle_auto_renew")
    finally:
        db.close()
    await show_service_menu(update, context, service_id_override=service_id)

async def update_servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refreshes the subscription link by fetching from all servers again."""
    query = update.callback_query
    await query.answer(_('messages.updating_servers'), show_alert=False)
    await get_subscription_link(update, context)

# --- Handlers for Service Enhancement Buttons ---
async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the FAQ button click with comprehensive information."""
    query = update.callback_query
    await query.answer()
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # Create FAQ categories keyboard
    keyboard = [
        [InlineKeyboardButton(_('buttons.faq.connection_issues'), callback_data='faq_connection')],
        [InlineKeyboardButton(_('buttons.faq.speed_issues'), callback_data='faq_speed')],
        [InlineKeyboardButton(_('buttons.faq.setup_guide'), callback_data='faq_setup')],
        [InlineKeyboardButton(_('buttons.faq.subscription_link'), callback_data='faq_subscription')],
        [InlineKeyboardButton(_('buttons.faq.multi_device'), callback_data='faq_multidevice')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_faq_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(_('messages.faq_main'), reply_markup=reply_markup)

async def faq_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles FAQ category selections."""
    query = update.callback_query
    await query.answer()
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    category = query.data.split('_')[1]
    message_key = f'messages.faq_{category}_details'
    
    keyboard = [[InlineKeyboardButton(_('buttons.general.back'), callback_data='faq_generic')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(_(message_key), reply_markup=reply_markup)

async def toggle_alerts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggles connection alerts for a service."""
    query = update.callback_query
    service_id = int(query.data.split('_')[2])
    
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service:
            await query.answer(_('messages.error_service_not_found'), show_alert=True)
            return
        
        # Toggle alerts
        service.connection_alerts = not service.connection_alerts
        db.commit()
        db.refresh(service)
        
        if service.connection_alerts:
            await query.answer(_('messages.connection_alerts_enabled'), show_alert=True)
        else:
            await query.answer(_('messages.connection_alerts_disabled'), show_alert=True)
    except Exception as e:
        await log_error(context, e, "toggle_alerts")
        await query.answer(_('messages.error_general'), show_alert=True)
    finally:
        db.close()
    
    # Refresh the service menu
    await show_service_menu(update, context, service_id_override=service_id)


# --- Change Note Conversation ---
async def start_change_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service_id = int(query.data.split('_')[2])
    context.user_data['service_id_for_note'] = service_id
    await query.message.reply_text(_('messages.enter_new_note'))
    return AWAITING_SERVICE_NOTE

async def receive_new_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_note = update.message.text
    service_id = context.user_data.get('service_id_for_note')
    db = SessionLocal()
    try:
        service_queries.update_service_note(db, service_id, new_note)
        await update.message.reply_text(_('messages.note_changed_successfully'))
    except Exception as e:
        await log_error(context, e, "receive_new_note")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()
    context.user_data.pop('service_id_for_note', None)
    return END_CONVERSION

async def cancel_change_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop('service_id_for_note', None)
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSION

change_note_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_change_note, pattern='^edit_note_')],
    states={
        AWAITING_SERVICE_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_note)]
    },
    fallbacks=[CommandHandler('cancel', cancel_change_note)]
)

# --- Renew Service Conversation ---
async def start_renewal_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    try:
        service_id = int(query.data.split('_')[1])
        service = service_queries.get_service_by_id(db, service_id)
        if not service or service.user_id != query.from_user.id:
            await query.edit_message_text(_('messages.error_service_not_found'))
            return END_CONVERSION
        context.user_data['service_to_renew_id'] = service.id
        plan = service.plan
        confirmation_text = _('messages.renewal_confirmation', plan_name=plan.name, price=plan.price)
        keyboard = [
            [InlineKeyboardButton(_('buttons.renewal.confirm'), callback_data=f'confirm_renew_{service_id}')],
            [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_renew')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)
        return AWAITING_RENEWAL_CONFIRMATION
    except Exception as e:
        await log_error(context, e, "start_renewal_flow")
        await query.edit_message_text(_('messages.error_general'))
        return END_CONVERSION
    finally:
        db.close()

async def confirm_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            return END_CONVERSION

        await query.edit_message_text(_('messages.renewing_service'))

        panels = panel_queries.get_all_panels(db)
        success_count = 0
        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                await api.renew_user(service)
                success_count += 1
            except Exception as e:
                await log_error(context, e, f"Failed to renew user on panel {panel.name}")

        if success_count == 0:
            await query.edit_message_text(_('messages.error_all_panels_failed_user'))
            return END_CONVERSION

        user_queries.update_wallet_balance(db, user_id, -plan.price)
        tx = transaction_queries.create_transaction(db, user_id, plan.price, TransactionType.SERVICE_PURCHASE, plan.id)
        transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.COMPLETED)
        service_queries.renew_service_record(db, service)

        award_commission_for_purchase(db, tx)

        await query.edit_message_text(_('messages.renewal_successful'))
    except Exception as e:
        await query.edit_message_text(_('messages.error_general'))
        await log_error(context, e, "confirm_renewal")
    finally:
        db.close()
    context.user_data.clear()
    return END_CONVERSION

async def cancel_renewal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSION

renew_service_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_renewal_flow, pattern='^renew_')],
    states={
        AWAITING_RENEWAL_CONFIRMATION: [
            CallbackQueryHandler(confirm_renewal, pattern='^confirm_renew_'),
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_renewal, pattern='^cancel_renew$')]
)

# --- Cancel Service Conversation ---
async def start_cancellation_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service_id = int(query.data.split('_')[2])
    context.user_data['service_to_cancel_id'] = service_id
    context.user_data['cancellation_message_id'] = query.message.message_id
    context.user_data['cancellation_user_id'] = query.from_user.id

    keyboard = [
        [InlineKeyboardButton(_('buttons.cancellation.confirm'), callback_data=f'confirm_cancel_{service_id}')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_service_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(_('messages.cancellation_confirmation'), reply_markup=reply_markup)
    return AWAITING_CANCELLATION_CONFIRMATION

async def confirm_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service_id = context.user_data.get('service_to_cancel_id')
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service:
            await query.edit_message_text(_('messages.error_service_not_found'))
            return END_CONVERSION

        panels = panel_queries.get_all_panels(db)
        for panel in panels:
            if not panel.is_active: continue
            try:
                api = MarzbanAPI(panel)
                await api.deactivate_user(service.username_in_panel)
            except Exception as e:
                await log_error(context, e, f"Failed to deactivate user on panel {panel.name}")

        service_queries.cancel_service_record(db, service_id)

        await query.edit_message_text(_('messages.cancellation_successful'))
    except Exception as e:
        await query.edit_message_text(_('messages.error_general'))
        await log_error(context, e, "confirm_cancellation")
    finally:
        db.close()
    context.user_data.clear()
    return END_CONVERSION

async def back_to_service_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    service_id = context.user_data.get('service_to_cancel_id')
    await show_service_menu(update, context, service_id_override=service_id)
    return END_CONVERSION

cancel_service_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_cancellation_flow, pattern='^cancel_service_')],
    states={
        AWAITING_CANCELLATION_CONFIRMATION: [
            CallbackQueryHandler(confirm_cancellation, pattern='^confirm_cancel_'),
            CallbackQueryHandler(back_to_service_menu, pattern='^back_to_service_menu$')
        ]
    },
    fallbacks=[CallbackQueryHandler(back_to_service_menu, pattern='^back_to_service_menu$')]
)