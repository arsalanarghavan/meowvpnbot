from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.models.transaction import TransactionStatus
from database.queries import transaction_queries, user_queries

async def handle_receipt_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a receipt."""
    query = update.callback_query
    await query.answer()

    action_parts = query.data.split('_')
    action = action_parts[0] + "_" + action_parts[1] # e.g., "confirm_receipt"
    tx_id = int(action_parts[2])
    
    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)
        if not tx or tx.status != TransactionStatus.PENDING:
            await query.edit_message_text(_('messages.admin_tx_already_processed'))
            return

        if action == "confirm_receipt":
            transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)
            user_queries.update_wallet_balance(db, tx.user_id, tx.amount)
            
            await query.edit_message_text(_('messages.admin_receipt_confirmed', tx_id=tx_id))
            await context.bot.send_message(
                chat_id=tx.user_id,
                text=_('messages.user_receipt_confirmed', amount=tx.amount)
            )
        
        elif action == "reject_receipt":
            transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.FAILED)
            
            await query.edit_message_text(_('messages.admin_receipt_rejected', tx_id=tx_id))
            await context.bot.send_message(
                chat_id=tx.user_id,
                text=_('messages.user_receipt_rejected')
            )
    finally:
        db.close()