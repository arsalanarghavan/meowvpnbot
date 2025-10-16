import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from telegram.error import Forbidden, BadRequest

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries
from bot.states.conversation_states import AWAITING_BROADCAST_MESSAGE, CONFIRMING_BROADCAST, END_CONVERSION

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the broadcast conversation."""
    await update.message.reply_text(_('messages.broadcast_send_message'))
    return AWAITING_BROADCAST_MESSAGE

async def receive_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the message to be broadcasted and asks for confirmation."""
    context.user_data['broadcast_message'] = update.message
    
    keyboard = [
        [
            InlineKeyboardButton(_('buttons.broadcast.send'), callback_data='send_broadcast'),
            InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_broadcast')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(_('messages.broadcast_confirm_send'), reply_markup=reply_markup)
    return CONFIRMING_BROADCAST

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends the stored message to all users."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_('messages.broadcast_sending_started'))

    message_to_send = context.user_data['broadcast_message']
    db = SessionLocal()
    try:
        user_ids = user_queries.get_all_user_ids(db)
    finally:
        db.close()

    successful_sends = 0
    failed_sends = 0

    for user_id in user_ids:
        try:
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message_to_send.chat_id,
                message_id=message_to_send.message_id
            )
            successful_sends += 1
        except Forbidden:
            # User has blocked the bot
            failed_sends += 1
        except BadRequest:
            # User not found or other issues
            failed_sends += 1
        
        # A small delay to avoid hitting Telegram's rate limits
        await asyncio.sleep(0.1)

    result_message = _('messages.broadcast_finished',
                       success=successful_sends,
                       fail=failed_sends)
    await context.bot.send_message(chat_id=query.from_user.id, text=result_message)
    
    context.user_data.clear()
    return END_CONVERSION

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the broadcast conversation."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(_('messages.operation_cancelled'))
    else:
        await update.message.reply_text(_('messages.operation_cancelled'))
        
    context.user_data.clear()
    return END_CONVERSION

# Define the conversation handler
broadcast_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.admin_panel.broadcast')}$"), start_broadcast)],
    states={
        AWAITING_BROADCAST_MESSAGE: [MessageHandler(filters.ALL & ~filters.COMMAND, receive_broadcast_message)],
        CONFIRMING_BROADCAST: [CallbackQueryHandler(send_broadcast, pattern='^send_broadcast$')]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_broadcast, pattern='^cancel_broadcast$'),
        CommandHandler('cancel', cancel_broadcast)
    ]
)