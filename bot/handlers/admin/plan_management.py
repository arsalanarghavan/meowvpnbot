from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler, MessageHandler,
                          CallbackQueryHandler, CommandHandler, filters)

from core.translator import _
from database.engine import SessionLocal
from database.queries import plan_queries
from database.models.plan import Plan, PlanCategory
from bot.states.conversation_states import (
    PLAN_MANAGEMENT_MENU, AWAITING_PLAN_NAME, AWAITING_PLAN_CATEGORY,
    AWAITING_PLAN_DURATION, AWAITING_PLAN_TRAFFIC, AWAITING_PLAN_PRICE,
    AWAITING_PLAN_DEVICE_LIMIT, CONFIRMING_PLAN_CREATION, ADMIN_SETTINGS_MENU,
    CONFIRMING_PLAN_DELETION, SELECTING_FIELD_TO_EDIT_PLAN, AWAITING_NEW_PLAN_VALUE
)
from bot.handlers.admin.settings_handlers import back_to_settings
from core.telegram_logger import log_error


# --- Main Menu ---
async def start_plan_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the main menu for plan management with edit/delete buttons."""
    query = update.callback_query
    if query:
        await query.answer()

    db = SessionLocal()
    try:
        plans = plan_queries.get_all_plans(db)
        keyboard = []
        if not plans:
            text = _('messages.plan_management_no_plans_list')
        else:
            text = _('messages.plan_management_menu_list')
            for p in plans:
                # Add an edit button (pencil emoji) and a delete button (trash emoji) for each plan
                keyboard.append([
                    InlineKeyboardButton(f"✏️ {p.name}", callback_data=f'edit_plan_start_{p.id}'),
                    InlineKeyboardButton(f"🗑️", callback_data=f'delete_plan_{p.id}'),
                ])

        # Add control buttons
        keyboard.append([InlineKeyboardButton(_('buttons.plan_management.add'), callback_data='add_plan')])
        keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_settings')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send message logic
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception as e:
        await log_error(context, e, "start_plan_management")
    finally:
        db.close()

    return PLAN_MANAGEMENT_MENU


# --- Delete Plan Conversation ---
async def delete_plan_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for confirmation before deleting a plan."""
    query = update.callback_query
    await query.answer()
    plan_id = int(query.data.split('_')[2])
    context.user_data['plan_to_manage_id'] = plan_id

    db = SessionLocal()
    try:
        plan = plan_queries.get_plan_by_id(db, plan_id)
        if not plan:
            await query.edit_message_text(_('messages.error_general'))
            return ConversationHandler.END

        text = _('messages.plan_delete_confirmation', name=plan.name)
        keyboard = [
            [
                InlineKeyboardButton(_('buttons.general.confirm_delete'), callback_data='confirm_delete_plan'),
                InlineKeyboardButton(_('buttons.general.cancel'), callback_data='back_to_plan_list')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()

    return CONFIRMING_PLAN_DELETION


async def confirm_delete_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes the plan from the database."""
    query = update.callback_query
    await query.answer()
    plan_id = context.user_data.pop('plan_to_manage_id', None)

    if not plan_id:
        return ConversationHandler.END

    db = SessionLocal()
    try:
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if plan:
            db.delete(plan)
            db.commit()
        await query.edit_message_text(_('messages.plan_deleted_successfully'))
    except Exception as e:
        await log_error(context, e, "confirm_delete_plan")
    finally:
        db.close()

    # Go back to the plan management menu
    await start_plan_management(update, context)
    return PLAN_MANAGEMENT_MENU

# --- Edit Plan Conversation ---
async def start_edit_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows options for which field of the plan to edit."""
    query = update.callback_query
    await query.answer()
    plan_id = int(query.data.split('_')[3])
    context.user_data['plan_to_manage_id'] = plan_id
    db = SessionLocal()
    try:
        plan = plan_queries.get_plan_by_id(db, plan_id)

        text = _('messages.plan_edit_select_field', name=plan.name)
        # Define fields that can be edited
        keyboard = [
            [InlineKeyboardButton(_('buttons.plan_edit.name'), callback_data='edit_plan_field_name')],
            [InlineKeyboardButton(_('buttons.plan_edit.price'), callback_data='edit_plan_field_price')],
            [InlineKeyboardButton(_('buttons.plan_edit.duration'), callback_data='edit_plan_field_duration_days')],
            [InlineKeyboardButton(_('buttons.plan_edit.traffic'), callback_data='edit_plan_field_traffic_gb')],
            [InlineKeyboardButton(_('buttons.plan_edit.device_limit'), callback_data='edit_plan_field_device_limit')],
            [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_plan_list')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        db.close()
    return SELECTING_FIELD_TO_EDIT_PLAN

async def select_field_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the field to edit and asks for the new value."""
    query = update.callback_query
    await query.answer()

    field = query.data.split('edit_plan_field_')[1]
    context.user_data['field_to_edit'] = field

    await query.edit_message_text(_(f'messages.plan_enter_new_{field}'))
    return AWAITING_NEW_PLAN_VALUE

async def receive_new_plan_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new value and updates the plan in the database."""
    from bot.utils.validators import validate_positive_integer, validate_text_length, sanitize_text
    
    field = context.user_data.get('field_to_edit')
    plan_id = context.user_data.get('plan_to_manage_id')

    if not field or not plan_id:
        await update.message.reply_text(_('messages.error_general'))
        return ConversationHandler.END
    
    # Validate based on field type
    if field in ['duration_days', 'traffic_gb', 'price', 'device_limit']:
        text_input = sanitize_text(update.message.text, max_length=20)
        new_value = validate_positive_integer(text_input, min_value=1 if field != 'traffic_gb' else 0)
        if new_value is None:
            await update.message.reply_text(_('messages.error_invalid_number'))
            return AWAITING_NEW_PLAN_VALUE
    elif field == 'name':
        new_value = validate_text_length(update.message.text, min_length=1, max_length=100)
        if new_value is None:
            await update.message.reply_text(_('messages.error_invalid_text'))
            return AWAITING_NEW_PLAN_VALUE
    else:
        new_value = sanitize_text(update.message.text, max_length=200)
        
    update_data = {field: new_value}

    db = SessionLocal()
    try:
        plan_queries.update_plan(db, plan_id, update_data)
        await update.message.reply_text(_('messages.plan_updated_successfully'))
    except Exception as e:
        await log_error(context, e, "receive_new_plan_value")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()
        context.user_data.pop('field_to_edit', None)
    
    # Go back to the main plan management menu
    await start_plan_management(update, context)
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
    context.user_data['new_plan']['name'] = update.message.text
    keyboard = [
        [InlineKeyboardButton(_(f'plan_categories.{cat.name}'), callback_data=f'plan_cat_{cat.name}')]
        for cat in PlanCategory
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(_('messages.plan_select_category'), reply_markup=reply_markup)
    return AWAITING_PLAN_CATEGORY

async def receive_plan_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category = PlanCategory[query.data.split('_')[2]]
    context.user_data['new_plan']['category'] = category
    await query.edit_message_text(_('messages.plan_enter_duration'))
    return AWAITING_PLAN_DURATION

async def receive_plan_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    try:
        limit = int(update.message.text)
        if limit <= 0: raise ValueError
        context.user_data['new_plan']['device_limit'] = limit
        plan = context.user_data['new_plan']
        text = _('messages.plan_confirm_creation',
                 name=plan['name'], category=plan['category'].value,
                 duration=plan['duration'], traffic=plan['traffic'],
                 price=plan['price'], devices=plan['device_limit'])
        keyboard = [
            [InlineKeyboardButton(_('buttons.general.confirm'), callback_data='confirm_create_plan')],
            [InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_creation')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        return CONFIRMING_PLAN_CREATION
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_number_positive'))
        return AWAITING_PLAN_DEVICE_LIMIT

async def confirm_create_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    plan_data = context.user_data.pop('new_plan', None)
    if not plan_data:
        return ConversationHandler.END

    db = SessionLocal()
    try:
        plan_queries.create_plan(db, plan_data)
        await query.edit_message_text(_('messages.plan_created_successfully'))
    finally:
        db.close()

    await start_plan_management(update, context)
    return PLAN_MANAGEMENT_MENU

async def cancel_plan_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    await start_plan_management(update, context)
    return PLAN_MANAGEMENT_MENU

# --- Conversation Handler ---
add_plan_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(f"^{_('buttons.admin_settings.plan_management')}$"), start_plan_management),
        CallbackQueryHandler(start_plan_management, pattern='^back_to_plan_list$')
    ],
    states={
        PLAN_MANAGEMENT_MENU: [
            CallbackQueryHandler(start_add_plan, pattern='^add_plan$'),
            CallbackQueryHandler(delete_plan_confirmation, pattern='^delete_plan_'),
            CallbackQueryHandler(start_edit_plan, pattern='^edit_plan_start_'),
        ],
        CONFIRMING_PLAN_DELETION: [
            CallbackQueryHandler(confirm_delete_plan, pattern='^confirm_delete_plan$'),
            CallbackQueryHandler(start_plan_management, pattern='^cancel_delete$'),
        ],
        SELECTING_FIELD_TO_EDIT_PLAN: [
            CallbackQueryHandler(select_field_to_edit, pattern='^edit_plan_field_')
        ],
        AWAITING_NEW_PLAN_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_plan_value)
        ],
        AWAITING_PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_name)],
        AWAITING_PLAN_CATEGORY: [CallbackQueryHandler(receive_plan_category, pattern='^plan_cat_')],
        AWAITING_PLAN_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_duration)],
        AWAITING_PLAN_TRAFFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_traffic)],
        AWAITING_PLAN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_price)],
        AWAITING_PLAN_DEVICE_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan_device_limit)],
        CONFIRMING_PLAN_CREATION: [
            CallbackQueryHandler(confirm_create_plan, pattern='^confirm_create_plan$'),
            CallbackQueryHandler(cancel_plan_creation, pattern='^cancel_creation$')
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_settings, pattern='^back_to_settings$'),
        CommandHandler('cancel', cancel_plan_creation)
    ],
    map_to_parent={
        ConversationHandler.END: ADMIN_SETTINGS_MENU
    }
)