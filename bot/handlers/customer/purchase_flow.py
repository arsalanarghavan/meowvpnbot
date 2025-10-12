import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.translator import _
from database.engine import SessionLocal
from database.models.plan import PlanCategory
from database.models.transaction import TransactionType, TransactionStatus
from database.queries import (plan_queries, user_queries, service_queries, 
                              transaction_queries, panel_queries)
from bot.keyboards.inline_keyboards import (get_plan_categories_keyboard, get_plans_keyboard,
                                            get_purchase_confirmation_keyboard, get_payment_methods_keyboard)
from bot.states.conversation_states import (SELECTING_CATEGORY, SELECTING_PLAN, 
                                            CONFIRMING_PURCHASE, SELECTING_PAYMENT_METHOD, END_CONVERSION)
from services.marzban_api import MarzbanAPI
from bot.logic.commission import award_commission_for_purchase
from core.telegram_logger import log_error

async def start_purchase_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the service purchase conversation by showing categories."""
    try:
        text = _('messages.purchase_select_category')
        reply_markup = get_plan_categories_keyboard()
        
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            
        return SELECTING_CATEGORY
    except Exception as e:
        await log_error(context, e, "start_purchase_flow")
        return ConversationHandler.END

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles category selection and shows corresponding plans."""
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    try:
        category_name = query.data.split('_')[1]
        category_enum = PlanCategory[category_name]
        context.user_data['selected_category'] = category_enum
        
        plans = plan_queries.get_plans_by_category(db, category=category_enum)
        if not plans:
            await query.edit_message_text(_('messages.no_plans_in_category'), reply_markup=get_plan_categories_keyboard())
            return SELECTING_CATEGORY
            
        text = _('messages.purchase_select_plan')
        reply_markup = get_plans_keyboard(plans)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return SELECTING_PLAN
    except Exception as e:
        await log_error(context, e, "select_category")
        await query.edit_message_text(_('messages.error_general'))
        return ConversationHandler.END
    finally:
        db.close()

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles plan selection and asks for confirmation."""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        plan_id = int(query.data.split('_')[1])
        plan = plan_queries.get_plan_by_id(db, plan_id)
        if not plan:
            await query.edit_message_text(_('messages.error_general'))
            return ConversationHandler.END

        context.user_data['selected_plan'] = plan
        
        traffic_text = _('words.unlimited') if plan.traffic_gb == 0 else f"{plan.traffic_gb} {_('words.gigabyte')}"
        confirmation_text = _('messages.purchase_confirmation',
                              name=plan.name,
                              duration=plan.duration_days,
                              traffic=traffic_text,
                              devices=plan.device_limit,
                              price=plan.price)
        reply_markup = get_purchase_confirmation_keyboard(plan_id)
        await query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)
        return CONFIRMING_PURCHASE
    except Exception as e:
        await log_error(context, e, "select_plan")
        await query.edit_message_text(_('messages.error_general'))
        return ConversationHandler.END
    finally:
        db.close()

async def show_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows payment method options to the user."""
    query = update.callback_query
    await query.answer()

    if 'selected_plan' not in context.user_data:
        await query.edit_message_text(_('messages.error_general'))
        return ConversationHandler.END

    text = _('messages.choose_payment_method')
    reply_markup = get_payment_methods_keyboard(purchase_flow=True)
    await query.edit_message_text(text=text, reply_markup=reply_markup)
    return SELECTING_PAYMENT_METHOD

async def process_wallet_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the purchase using the user's wallet, creating the user on ALL active panels."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    plan = context.user_data.get('selected_plan')
    
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user.id)

        if db_user.wallet_balance < plan.price:
            await query.edit_message_text(_('messages.insufficient_balance', balance=db_user.wallet_balance))
            return ConversationHandler.END

        await query.edit_message_text(_('messages.creating_service_multi_server'))

        panels = panel_queries.get_all_panels(db)
        if not panels:
            await query.edit_message_text(_('messages.no_panels_configured'))
            return ConversationHandler.END
            
        service_username = f"uid{user.id}-{uuid.uuid4().hex[:4]}"
        
        user_details_list = []
        failed_panels = []
        for panel in panels:
            if not panel.is_active:
                continue
            try:
                api = MarzbanAPI(panel)
                user_details = await api.create_user(plan=plan, username=service_username)
                user_details_list.append(user_details)
            except Exception as e:
                failed_panels.append(panel.name)
                await log_error(context, e, f"Failed to create user on panel {panel.name}")
                continue
        
        if not user_details_list:
            await query.edit_message_text(_('messages.error_all_panels_failed'))
            return ConversationHandler.END

        # --- If some panels failed, inform the admin but proceed for the user ---
        if failed_panels:
            failed_panel_names = ", ".join(failed_panels)
            error_message = f"User service creation partially failed for user {user.id} on panels: {failed_panel_names}"
            # This will be logged to the channel via the main error handler logic.
            # We can also send a direct, less detailed message.
            await context.bot.send_message(chat_id=context.bot_data['admin_id'], text=error_message)


        combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)

        user_queries.update_wallet_balance(db, user.id, -plan.price)
        tx = transaction_queries.create_transaction(db, user.id, plan.price, TransactionType.SERVICE_PURCHASE, plan.id)
        transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.COMPLETED)
        service_queries.create_service_record(db, user.id, plan, service_username)

        award_commission_for_purchase(db, tx)

        await query.edit_message_text(_('messages.purchase_successful', sub_link=combined_sub_link))

    except Exception as e:
        await query.edit_message_text(_('messages.error_general'))
        await log_error(context, e, "process_wallet_payment")
    finally:
        db.close()
        
    context.user_data.clear()
    return ConversationHandler.END

async def back_to_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Goes back to the plan selection menu."""
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    try:
        category_enum = context.user_data.get('selected_category')
        if not category_enum:
            return await start_purchase_flow(update, context) # Go back to start if category is lost

        plans = plan_queries.get_plans_by_category(db, category=category_enum)
        text = _('messages.purchase_select_plan')
        reply_markup = get_plans_keyboard(plans)
        await query.edit_message_text(text, reply_markup=reply_markup)
        return SELECTING_PLAN
    except Exception as e:
        await log_error(context, e, "back_to_plans")
        return ConversationHandler.END
    finally:
        db.close()

async def cancel_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the purchase conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return ConversationHandler.END