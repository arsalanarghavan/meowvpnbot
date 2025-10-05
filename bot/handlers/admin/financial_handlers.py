from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.models.transaction import TransactionStatus, TransactionType
from database.queries import transaction_queries, user_queries, service_queries
from services.marzban_api import MarzbanAPI

async def handle_receipt_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a receipt and automates service creation or wallet charging."""
    query = update.callback_query
    await query.answer()

    action_parts = query.data.split('_')
    action = action_parts[0] + "_" + action_parts[1]
    tx_id = int(action_parts[2])

    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)
        if not tx or tx.status != TransactionStatus.PENDING:
            await query.edit_message_text(_('messages.admin_tx_already_processed'))
            return

        if action == "confirm_receipt":
            # --- Main Logic: Differentiate between wallet charge and service purchase ---
            if tx.type == TransactionType.SERVICE_PURCHASE and tx.plan_id:
                # This is a service purchase, create the service in Marzban
                await query.edit_message_text(_('messages.admin_creating_service_for_user', user_id=tx.user_id))
                try:
                    marzban_api = MarzbanAPI()
                    marzban_user = await marzban_api.create_user(plan=tx.plan, prefix=f"uid{tx.user_id}")
                    
                    # Create the service record in our database
                    service_queries.create_service_record(db, tx.user_id, tx.plan, marzban_user['username'])
                    
                    # Finalize transaction
                    transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)
                    
                    await query.edit_message_text(_('messages.admin_service_created_successfully', tx_id=tx_id))
                    
                    # Notify the user
                    sub_link = marzban_user.get('subscription_url', 'Not found')
                    await context.bot.send_message(
                        chat_id=tx.user_id,
                        text=_('messages.purchase_successful_after_confirm', sub_link=sub_link)
                    )
                except Exception as e:
                    await query.edit_message_text(_('messages.error_marzban_api', error=str(e)))
                    # Optionally, fail the transaction if API call fails
                    transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.FAILED)
                    return

            else: # This is a regular wallet charge
                user_queries.update_wallet_balance(db, tx.user_id, tx.amount)
                transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)
                
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