from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.queries import gift_card_queries
from bot.states.conversation_states import AWAITING_GIFT_AMOUNT, AWAITING_GIFT_COUNT, END_CONVERSATION

# Entry point for admin
async def new_gift_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the gift card creation conversation."""
    await update.message.reply_text(_('messages.admin_enter_gift_amount'))
    return AWAITING_GIFT_AMOUNT

async def receive_gift_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the amount for the gift cards."""
    try:
        amount = int(update.message.text)
        if amount <= 0:
            raise ValueError
        context.user_data['gift_amount'] = amount
        await update.message.reply_text(_('messages.admin_enter_gift_count'))
        return AWAITING_GIFT_COUNT
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_amount'))
        return AWAITING_GIFT_AMOUNT

async def receive_gift_count_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the count and creates the gift cards."""
    try:
        count = int(update.message.text)
        if not 1 <= count <= 100: # Limit to 100 cards at a time
             raise ValueError
        amount = context.user_data['gift_amount']
        
        db = SessionLocal()
        try:
            codes = gift_card_queries.create_gift_cards(db, amount=amount, count=count)
            
            codes_text = "\n".join([f"`{code}`" for code in codes])
            await update.message.reply_text(
                _('messages.admin_gift_codes_created', count=count, amount=amount, codes=codes_text),
                parse_mode='Markdown'
            )
        finally:
            db.close()
            
        context.user_data.clear()
        return END_CONVERSATION
        
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_count'))
        return AWAITING_GIFT_COUNT

async def cancel_gift_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the gift card creation process."""
    context.user_data.clear()
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSATION

# Define the conversation handler
new_gift_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('newgift', new_gift_start, filters=filters.User(user_id=ADMIN_ID))],
    states={
        AWAITING_GIFT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gift_amount)],
        AWAITING_GIFT_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_gift_count_and_create)],
    },
    fallbacks=[CommandHandler('cancel', cancel_gift_creation)]
)