from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.models.transaction import TransactionType
from database.queries import transaction_queries, user_queries
from bot.keyboards.inline_keyboards import get_payment_methods_keyboard, get_admin_receipt_confirmation_keyboard, get_wallet_menu_keyboard
from bot.states.conversation_states import AWAITING_AMOUNT, AWAITING_RECEIPT, END_CONVERSATION

async def ask_for_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks the user to choose a payment method for increasing balance."""
    query = update.callback_query
    await query.answer()

    context.user_data['purchase_flow'] = False
    context.user_data.pop('selected_plan', None) # Clear any selected plan

    await query.edit_message_text(_('messages.choose_payment_method_for_charge'))
    # A simplified state for asking amount for wallet charge
    # This leads to a text input from the user
    return AWAITING_AMOUNT


async def card_to_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the card-to-card payment process, either from purchase or wallet charge."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    db = SessionLocal()
    try:
        plan = context.user_data.get('selected_plan')
        if plan:
            # We are in a purchase flow
            amount = plan.price
            tx = transaction_queries.create_transaction(
                db, user_id=user.id, amount=amount, tx_type=TransactionType.SERVICE_PURCHASE, plan_id=plan.id
            )
        else:
            # This is a wallet charge flow, we should have the amount from the previous step
            amount = context.user_data.get('charge_amount')
            if not amount:
                await query.edit_message_text(_('messages.error_general'))
                return END_CONVERSATION
            tx = transaction_queries.create_transaction(
                db, user_id=user.id, amount=amount, tx_type=TransactionType.WALLET_CHARGE
            )

        context.user_data['active_tx_id'] = tx.id

        card_info_text = _('messages.card_to_card_instructions', amount=amount, tx_id=tx.id)
        await query.edit_message_text(text=card_info_text)

    finally:
        db.close()

    return AWAITING_RECEIPT

async def receive_charge_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the amount to charge the wallet and shows payment methods."""
    try:
        amount = int(update.message.text)
        if amount <= 0:
            raise ValueError
        context.user_data['charge_amount'] = amount
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_amount'))
        return AWAITING_AMOUNT

    text = _('messages.choose_payment_method')
    reply_markup = get_payment_methods_keyboard(purchase_flow=False)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    # The user will now click a button, which is handled by another handler.
    # We are ending this part of the conversation.
    return END_CONVERSATION


async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's sent receipt and forwards it to the admin."""
    user = update.effective_user
    tx_id = context.user_data.get('active_tx_id')

    if not tx_id:
        await update.message.reply_text(_('messages.error_general'))
        return END_CONVERSATION

    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)

        admin_message = _('messages.admin_receipt_notification',
                          user_id=user.id,
                          first_name=user.first_name,
                          amount=tx.amount,
                          tx_id=tx.id)

        reply_markup = get_admin_receipt_confirmation_keyboard(tx.id)

        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user.id, message_id=update.message.message_id)
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=reply_markup)

        await update.message.reply_text(_('messages.receipt_sent_for_review'))

    finally:
        db.close()

    context.user_data.clear()
    return END_CONVERSATION

async def back_to_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback query handler to go back to the wallet menu."""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        # We need to find the user from the database to get the latest balance
        db_user = user_queries.find_user_by_id(db, query.from_user.id)
        balance = db_user.wallet_balance if db_user else 0
        wallet_text = _('messages.wallet_info', balance=balance)
        reply_markup = get_wallet_menu_keyboard()
        await query.edit_message_text(wallet_text, reply_markup=reply_markup)
    finally:
        db.close()


async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the payment conversation."""
    await update.message.reply_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSATION