from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.queries import plan_queries
from database.models.plan import PlanCategory
from bot.states.conversation_states import (PLAN_MANAGEMENT_MENU, AWAITING_PLAN_NAME,
                                            AWAITING_PLAN_CATEGORY, AWAITING_PLAN_DURATION,
                                            AWAITING_PLAN_TRAFFIC, AWAITING_PLAN_PRICE,
                                            AWAITING_PLAN_DEVICE_LIMIT, CONFIRMING_PLAN_CREATION,
                                            END_CONVERSION)

# --- Main Menu ---
async def start_plan_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the main menu for plan management."""
    db = SessionLocal()
    try:
        plans = plan_queries.get_all_plans(db)
        if not plans:
            text = _('messages.plan_management_no_plans')
        else:
            plan_list = "\n".join([f"- {p.name} ({p.price} تومان)" for p in plans])
            text = _('messages.plan_management_menu', plans=plan_list)
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton(_('buttons.plan_management.add'), callback_data='add_plan')],
        # Future buttons for edit/delete can be added here
        [InlineKeyboardButton(_('buttons.general.back_to_admin_menu'), callback_data='back_to_admin_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)
    return PLAN_MANAGEMENT_MENU

# --- Add Plan Conversation ---
async def start_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation to add a new plan."""
    query = update.callback_query
    await query.answer()
    context.user_data['new_plan'] = {}
    await query.edit_message_text(_('messages.plan_enter_name'))
    return AWAITING_PLAN_NAME

async def receive_plan_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the plan name."""
    context.user_data['new_plan']['name'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton(_(f'plan_categories.{cat.name}'), callback_data=f'plan_cat_{cat.name}')]
        for cat in PlanCategory
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(_('messages.plan_select_category'), reply_markup=reply_markup)
    return AWAITING_PLAN_CATEGORY

async def receive_plan_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the plan category."""
    query = update.callback_query
    await query.answer()
    category = PlanCategory[query.data.split('_')[2]]
    context.user_data['new_plan']['category'] = category
    await query.edit_message_text(_('messages.plan_enter_duration'))
    return AWAITING_PLAN_DURATION

async def receive_plan_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the plan duration in days."""
    try:
        duration = int(update.message.text)
        if duration <= 0: raise ValueError
        context.user_data['new_plan']['duration'] = duration
        await update.message.reply_text(_('messages.plan_enter_traffic'))
        return AWAITING_PLAN_TRAFFIC
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_positive'))
        return AWAITING_PLAN_DURATION

async def receive_plan_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the plan traffic in GB (0 for unlimited)."""
    try:
        traffic = int(update.message.text)
        if traffic < 0: raise ValueError
        context.user_data['new_plan']['traffic'] = traffic
        await update.message.reply_text(_('messages.plan_enter_price'))
        return AWAITING_PLAN_PRICE
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_zero_ok'))
        return AWAITING_PLAN_TRAFFIC

async def receive_plan_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the plan price."""
    try:
        price = int(update.message.text)
        if price <= 0: raise ValueError
        context.user_data['new_plan']['price'] = price
        await update.message.reply_text(_('messages.plan_enter_device_limit'))
        return AWAITING_PLAN_DEVICE_LIMIT
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_positive'))
        return AWAITING_PLAN_PRICE

async def receive_plan_device_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the device limit and asks for confirmation."""
    try:
        limit = int(update.message.text)
        if limit <= 0: raise ValueError
        context.user_data['new_plan']['device_limit'] = limit
        
        # Show confirmation
        plan = context.user_data['new_plan']
        text = _('messages.plan_confirm_creation',
                 name=plan['name'], category=plan['category'].value,
                 duration=plan['duration'], traffic=plan['traffic'],
                 price=plan['price'], devices=plan['device_limit'])
        
        keyboard = [
            [InlineKeyboardButton(_('buttons.general.confirm'), callback_data='confirm_create_plan')],
            [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_create_plan')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        return CONFIRMING_PLAN_CREATION
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_positive'))
        return AWAITING_PLAN_DEVICE_LIMIT

async def confirm_create_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the new plan to the database."""
    query = update.callback_query
    await query.answer()
    
    plan_data = context.user_data['new_plan']
    db = SessionLocal()
    try:
        plan_queries.create_plan(db, plan_data)
        await query.edit_message_text(_('messages.plan_created_successfully'))
    finally:
        db.close()
        
    context.user_data.clear()
    return END_CONVERSION

async def cancel_plan_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the plan creation process."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(_('messages.operation_cancelled'))
    else:
        await update.message.reply_text(_('messages.operation_cancelled'))
        
    context.user_data.clear()
    return END_CONVERSION

# --- Conversation Handler ---
add_plan_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_plan, pattern='^add_plan$')],
    states={
        AWAITING_PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_name)],
        AWAITING_PLAN_CATEGORY: [CallbackQueryHandler(receive_plan_category, pattern='^plan_cat_')],
        AWAITING_PLAN_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_duration)],
        AWAITING_PLAN_TRAFFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_traffic)],
        AWAITING_PLAN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_price)],
        AWAITING_PLAN_DEVICE_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_device_limit)],
        CONFIRMING_PLAN_CREATION: [
            CallbackQueryHandler(confirm_create_plan, pattern='^confirm_create_plan$'),
            CallbackQueryHandler(cancel_plan_creation, pattern='^cancel_create_plan$')
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_plan_creation)]
)