from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from core.translator import _
from database.engine import SessionLocal
from database.queries import gift_card_queries, user_queries, transaction_queries
from database.models.transaction import TransactionType
from bot.states.conversation_states import AWAITING_GIFT_CODE, END_CONVERSATION

# Entry point for customer
async def gift_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the gift card redemption conversation."""
    await update.message.reply_text(_('messages.enter_gift_code'))
    return AWAITING_GIFT_CODE

async def redeem_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives and processes the gift code."""
    code = update.message.text.strip()
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        card = gift_card_queries.find_gift_card_by_code(db, code)
        
        if not card:
            await update.message.reply_text(_('messages.gift_code_not_found'))
            return AWAITING_GIFT_CODE # Ask again
            
        if card.is_used:
            await update.message.reply_text(_('messages.gift_code_already_used'))
            return END_CONVERSATION
            
        # Redeem the card
        amount = card.amount
        gift_card_queries.redeem_gift_card(db, card, user_id)
        
        # Update user's wallet and create transaction
        user_queries.update_wallet_balance(db, user_id, amount)
        transaction_queries.create_transaction(db, user_id, amount, TransactionType.GIFT_CARD)
        
        await update.message.reply_text(_('messages.gift_code_success', amount=amount))

    finally:
        db.close()
        
    return END_CONVERSATION

async def cancel_gift_redemption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the gift card redemption process."""
    await update.message.reply_text(_('messages.operation_cancelled'))
    return END_CONVERSATION

# Define the conversation handler
gift_card_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & filters.Regex(f"^{_('buttons.main_menu.gift_card')}$"), gift_card_start)],
    states={
        AWAITING_GIFT_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, redeem_gift_code)],
    },
    fallbacks=[CommandHandler('cancel', cancel_gift_redemption)]
)