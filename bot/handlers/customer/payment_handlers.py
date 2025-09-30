from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.models.transaction import TransactionType
from database.queries import transaction_queries
from bot.keyboards.inline_keyboards import get_payment_methods_keyboard, get_admin_receipt_confirmation_keyboard
from bot.states.conversation_states import AWAITING_RECEIPT, END_CONVERSATION

async def ask_for_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks the user to choose a payment method."""
    query = update.callback_query
    await query.answer()
    
    text = _('messages.choose_payment_method')
    reply_markup = get_payment_methods_keyboard()
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def card_to_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the card-to-card payment process."""
    query = update.callback_query
    await query.answer()
    
    card_info_text = _('messages.card_to_card_instructions')
    await query.edit_message_text(text=card_info_text)
    
    return AWAITING_RECEIPT

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's sent receipt and forwards it to the admin."""
    user = update.effective_user
    
    # This is a placeholder. In a real scenario, you'd ask the user for the amount first.
    amount = 50000 
    
    db = SessionLocal()
    try:
        tx = transaction_queries.create_transaction(
            db, user_id=user.id, amount=amount, tx_type=TransactionType.WALLET_CHARGE
        )
        
        admin_message = _('messages.admin_receipt_notification',
                          user_id=user.id,
                          first_name=user.first_name,
                          amount=amount,
                          tx_id=tx.id)
                          
        reply_markup = get_admin_receipt_confirmation_keyboard(tx.id)
        
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user.id, message_id=update.message.message_id)
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=reply_markup)
        
        await update.message.reply_text(_('messages.receipt_sent_for_review'))

    finally:
        db.close()
        
    return END_CONVERSATION

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the payment conversation."""
    await update.message.reply_text(_('messages.operation_cancelled'))
    # You might want to remove the message with the card info here
    # await update.callback_query.message.delete()
    return END_CONVERSATION