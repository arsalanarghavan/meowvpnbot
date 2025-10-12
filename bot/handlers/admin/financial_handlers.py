import uuid
from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.models.transaction import TransactionStatus, TransactionType
from database.queries import (transaction_queries, user_queries, service_queries, panel_queries)
from services.marzban_api import MarzbanAPI
from bot.logic.commission import award_commission_for_purchase
from core.telegram_logger import log_error
from bot.keyboards.inline_keyboards import get_admin_receipt_confirmation_keyboard

async def list_pending_receipts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a list of pending card-to-card transactions for the admin to confirm."""
    db = SessionLocal()
    try:
        pending_txs = transaction_queries.get_pending_card_to_card_transactions(db)
        if not pending_txs:
            await update.message.reply_text(_('messages.admin_no_pending_receipts'))
            return

        await update.message.reply_text(_('messages.admin_pending_receipts_header'))
        for tx in pending_txs:
            user_info = tx.user
            admin_message = _('messages.admin_receipt_notification',
                              user_id=user_info.user_id,
                              first_name=user_info.user_id, # In case first_name is not available
                              amount=tx.amount,
                              tx_id=tx.id)
            reply_markup = get_admin_receipt_confirmation_keyboard(tx.id)
            await update.message.reply_text(admin_message, reply_markup=reply_markup)

    except Exception as e:
        await log_error(context, e, "listing pending receipts")
        await update.message.reply_text(_('messages.error_general'))
    finally:
        db.close()


async def handle_receipt_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a receipt and automates service creation on all panels or wallet charging."""
    query = update.callback_query
    await query.answer()

    # Data is "confirm_receipt_{tx_id}" or "reject_receipt_{tx_id}"
    try:
        action_parts = query.data.split('_')
        action = action_parts[0] + "_" + action_parts[1]
        tx_id = int(action_parts[2])
    except (ValueError, IndexError) as e:
        await log_error(context, e, "parsing receipt confirmation callback")
        await query.edit_message_text(_('messages.error_general'), reply_markup=None)
        return

    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)
        if not tx or tx.status != TransactionStatus.PENDING:
            await query.edit_message_text(_('messages.admin_tx_already_processed'), reply_markup=None)
            return

        original_message = query.message.text

        if action == "confirm_receipt":
            if tx.type == TransactionType.SERVICE_PURCHASE and tx.plan:
                # --- Multi-Panel Service Creation Logic ---
                await query.edit_message_text(original_message + "\n\n" + _('messages.admin_creating_service_for_user', user_id=tx.user_id))

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
                        await log_error(context, e, f"Failed to create user on panel {panel.name} during receipt confirmation")
                        continue

                if not user_details_list:
                    await query.edit_message_text(_('messages.error_all_panels_failed'))
                    transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.FAILED) # Revert tx
                    return

                combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)

                service_queries.create_service_record(db, tx.user_id, tx.plan, service_username)
                transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)

                # --- Award Commission ---
                award_commission_for_purchase(db, tx)
                # ---

                await query.edit_message_text(original_message + "\n\n" + _('messages.admin_service_created_successfully', tx_id=tx_id), reply_markup=None)

                await context.bot.send_message(
                    chat_id=tx.user_id,
                    text=_('messages.purchase_successful_after_confirm', sub_link=combined_sub_link)
                )

            else:  # Regular wallet charge
                user_queries.update_wallet_balance(db, tx.user_id, tx.amount)
                transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.COMPLETED)

                await query.edit_message_text(original_message + "\n\n" + _('messages.admin_receipt_confirmed', tx_id=tx_id), reply_markup=None)
                await context.bot.send_message(
                    chat_id=tx.user_id,
                    text=_('messages.user_receipt_confirmed', amount=tx.amount)
                )

        elif action == "reject_receipt":
            transaction_queries.update_transaction_status(db, tx_id, TransactionStatus.FAILED)
            await query.edit_message_text(original_message + "\n\n" + _('messages.admin_receipt_rejected', tx_id=tx_id), reply_markup=None)
            await context.bot.send_message(
                chat_id=tx.user_id,
                text=_('messages.user_receipt_rejected')
            )
            
    except Exception as e:
        await log_error(context, e, "handling receipt confirmation")
        await query.edit_message_text(_('messages.error_general'), reply_markup=None)
    finally:
        db.close()