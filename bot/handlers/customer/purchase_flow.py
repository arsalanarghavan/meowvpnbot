from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.translator import _
from database.engine import SessionLocal
from database.models.plan import PlanCategory
from database.models.transaction import TransactionType
from database.queries import plan_queries, user_queries, service_queries, transaction_queries
from bot.keyboards.inline_keyboards import (get_plan_categories_keyboard, get_plans_keyboard,
                                            get_purchase_confirmation_keyboard)
from bot.states.conversation_states import SELECTING_CATEGORY, SELECTING_PLAN, CONFIRMING_PURCHASE, END_CONVERSATION
from services.marzban_api import MarzbanAPI

async def start_purchase_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the service purchase conversation by showing categories."""
    text = _('messages.purchase_select_category')
    reply_markup = get_plan_categories_keyboard()
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        
    return SELECTING_CATEGORY

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles category selection and shows corresponding plans."""
    query = update.callback_query
    await query.answer()
    
    category_name = query.data.split('_')[1]
    category_enum = PlanCategory[category_name]
    context.user_data['selected_category'] = category_enum
    
    db = SessionLocal()
    try:
        plans = plan_queries.get_plans_by_category(db, category=category_enum)
        if not plans:
            await query.edit_message_text(_('messages.no_plans_in_category'), reply_markup=get_plan_categories_keyboard())
            return SELECTING_CATEGORY
            
        text = _('messages.purchase_select_plan')
        reply_markup = get_plans_keyboard(plans)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()
        
    return SELECTING_PLAN

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles plan selection and asks for confirmation."""
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.split('_')[1])
    db = SessionLocal()
    try:
        plan = plan_queries.get_plan_by_id(db, plan_id)
        if not plan:
            await query.edit_message_text(_('messages.error_general'))
            return END_CONVERSATION

        context.user_data['selected_plan'] = plan
        
        confirmation_text = _('messages.purchase_confirmation',
                              name=plan.name,
                              duration=plan.duration_days,
                              traffic=plan.traffic_gb if plan.traffic_gb > 0 else "نامحدود",
                              devices=plan.device_limit,
                              price=plan.price)
        reply_markup = get_purchase_confirmation_keyboard(plan_id)
        await query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)
    finally:
        db.close()

    return CONFIRMING_PURCHASE

async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirms purchase, checks wallet, creates service."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    plan_id = int(query.data.split('_')[1])
    
    db = SessionLocal()
    try:
        plan = plan_queries.get_plan_by_id(db, plan_id)
        db_user = user_queries.find_or_create_user(db, user.id)

        if db_user.wallet_balance < plan.price:
            await query.edit_message_text(_('messages.insufficient_balance', balance=db_user.wallet_balance))
            return END_CONVERSATION

        await query.edit_message_text(_('messages.creating_service'))

        marzban_api = MarzbanAPI()
        marzban_user = await marzban_api.create_user(plan=plan, prefix=f"uid{user.id}")
        
        user_queries.update_wallet_balance(db, user.id, -plan.price)
        transaction_queries.create_transaction(db, user.id, plan.price, TransactionType.SERVICE_PURCHASE)
        service_queries.create_service_record(db, user.id, plan, marzban_user['username'])

        sub_link = marzban_user.get('subscription_url', 'Not found')
        await query.edit_message_text(_('messages.purchase_successful', sub_link=sub_link))

    except Exception as e:
        await query.edit_message_text(_('messages.error_general'))
        print(f"Error during purchase confirmation: {e}")
    finally:
        db.close()
        
    return END_CONVERSATION

async def back_to_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Goes back to the plan selection menu."""
    query = update.callback_query
    await query.answer()
    
    category_enum = context.user_data.get('selected_category')
    db = SessionLocal()
    try:
        plans = plan_queries.get_plans_by_category(db, category=category_enum)
        text = _('messages.purchase_select_plan')
        reply_markup = get_plans_keyboard(plans)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()
    
    return SELECTING_PLAN

async def cancel_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the purchase conversation."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    return END_CONVERSATION