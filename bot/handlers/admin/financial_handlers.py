import uuid
from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.models.transaction import TransactionStatus, TransactionType
from database.queries import (transaction_queries, user_queries, service_queries, panel_queries)
from services.marzban_api import MarzbanAPI

async def handle_receipt_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a receipt and automates service creation on all panels or wallet charging."""
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
            if tx.type == TransactionType.SERVICE_PURCHASE and tx.plan_id:
                # --- Multi-Panel Service Creation Logic ---
                await query.edit_message_text(_('messages.admin_creating_service_for_user', user_id=tx.user_id))
                
                panels = panel_queries.get_all_panels(db)
                if not panels:
                    await query.edit_message_text(_('messages.no_panels_configured'))
                    return

                service_username = f"uid{tx.user_id}-{uuid.uuid4().hex[:8]}"
                user_details_list = []

                for panel in panels:
                    try:
                        api = MarzbanAPI(panel)
                        user_details = await api.create_user(plan=tx.plan, username=service_username)
                        user_details_list.append(user_details)
                    except Exception as e:
                        print(f"Failed to create user on panel {panel.name} during receipt confirmation: {e}")
                        continue
                
                if not user_details_list:
                    await query.edit_message_text(_('messages.error_all_panels_failed'))
                    transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.FAILED)
                    return

                combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
                
                service_queries.create_service_record(db, tx.user_id, tx.plan, service_username)
                transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)
                
                await query.edit_message_text(_('messages.admin_service_created_successfully', tx_id=tx_id))
                
                await context.bot.send_message(
                    chat_id=tx.user_id,
                    text=_('messages.purchase_successful_after_confirm', sub_link=combined_sub_link)
                )

            else: # Regular wallet charge
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