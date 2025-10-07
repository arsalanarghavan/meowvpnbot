from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.models.transaction import TransactionType, TransactionStatus
from database.queries import transaction_queries, user_queries, service_queries, panel_queries
from bot.keyboards.inline_keyboards import (
    get_payment_methods_keyboard, get_admin_receipt_confirmation_keyboard,
    get_wallet_menu_keyboard, get_online_payment_keyboard
)
from bot.states.conversation_states import AWAITING_AMOUNT, AWAITING_RECEIPT, AWAITING_ONLINE_PAYMENT_VERIFICATION, END_CONVERSION
from services.zarinpal import Zarinpal
from services.marzban_api import MarzbanAPI
import uuid

async def ask_for_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user to choose a payment method for increasing balance."""
    query = update.callback_query
    await query.answer()

    context.user_data['purchase_flow'] = False
    context.user_data.pop('selected_plan', None) # Clear any selected plan

    # Ask for the amount to charge
    await query.edit_message_text(_('messages.enter_charge_amount'))
    return AWAITING_AMOUNT


async def receive_charge_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the amount to charge the wallet and shows payment methods."""
    try:
        amount = int(update.message.text)
        if amount <= 1000: # Zarinpal has a minimum amount
            raise ValueError
        context.user_data['charge_amount'] = amount
        # Delete the user's message (the amount)
        await update.message.delete()
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_amount_min_1000'))
        return AWAITING_AMOUNT

    text = _('messages.choose_payment_method')
    reply_markup = get_payment_methods_keyboard(purchase_flow=False)
    
    # Check if a message was previously sent to edit, otherwise send a new one
    if 'message_to_edit' in context.user_data:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data['message_to_edit'],
            text=text,
            reply_markup=reply_markup
        )
    else:
        sent_message = await update.message.reply_text(text=text, reply_markup=reply_markup)
        context.user_data['message_to_edit'] = sent_message.message_id

    return END_CONVERSION


async def card_to_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the card-to-card payment process."""
    # (This function remains the same as your original code)
    # ...
    return AWAITING_RECEIPT

async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's sent receipt and forwards it to the admin."""
    # (This function remains the same as your original code)
    # ...
    return END_CONVERSION


# --- Online Payment Flow ---
async def start_online_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the online payment process using Zarinpal."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    db = SessionLocal()
    try:
        plan = context.user_data.get('selected_plan')
        if plan:
            amount = plan.price
            tx_type = TransactionType.SERVICE_PURCHASE
            plan_id = plan.id
        else:
            amount = context.user_data.get('charge_amount')
            tx_type = TransactionType.WALLET_CHARGE
            plan_id = None

        if not amount:
            await query.edit_message_text(_('messages.error_general'))
            return END_CONVERSION

        # Create a pending transaction
        tx = transaction_queries.create_transaction(db, user.id, amount, tx_type, plan_id)
        
        # Request payment from Zarinpal
        zarinpal_api = Zarinpal()
        description = f"خرید سرویس" if plan else f"شارژ کیف پول"
        authority, payment_url = await zarinpal_api.request_payment(amount, description, tx.id)

        if not authority:
            await query.edit_message_text(_('messages.error_payment_gateway'))
            transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.FAILED)
            return END_CONVERSION
        
        # Save authority in the transaction for verification
        transaction_queries.update_transaction_tracking_code(db, tx.id, authority)
        
        text = _('messages.redirecting_to_gateway')
        reply_markup = get_online_payment_keyboard(payment_url, tx.id)
        await query.edit_message_text(text, reply_markup=reply_markup)

    finally:
        db.close()
    
    return AWAITING_ONLINE_PAYMENT_VERIFICATION


async def verify_online_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifies the online payment after the user confirms."""
    query = update.callback_query
    await query.answer()

    tx_id = int(query.data.split('_')[2])
    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)
        if not tx or tx.status != TransactionStatus.PENDING:
            await query.edit_message_text(_('messages.admin_tx_already_processed'))
            return END_CONVERSION

        await query.edit_message_text(_('messages.verifying_payment'))

        zarinpal_api = Zarinpal()
        authority = tx.tracking_code # We stored authority here
        is_success, ref_id = await zarinpal_api.verify_payment(tx.amount, authority)

        if is_success:
            transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.COMPLETED)
            transaction_queries.update_transaction_tracking_code(db, tx.id, ref_id)

            if tx.type == TransactionType.SERVICE_PURCHASE and tx.plan:
                # --- Multi-Panel Service Creation Logic ---
                await query.edit_message_text(_('messages.creating_service_multi_server'))
                panels = panel_queries.get_all_panels(db)
                service_username = f"uid{tx.user_id}-{uuid.uuid4().hex[:8]}"
                user_details_list = []

                for panel in panels:
                    try:
                        api = MarzbanAPI(panel)
                        user_details = await api.create_user(plan=tx.plan, username=service_username)
                        user_details_list.append(user_details)
                    except Exception as e:
                        print(f"Failed to create user on panel {panel.name} during online payment: {e}")
                
                combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
                service_queries.create_service_record(db, tx.user_id, tx.plan, service_username)
                
                await query.edit_message_text(_('messages.purchase_successful', sub_link=combined_sub_link))

            else: # Wallet Charge
                user_queries.update_wallet_balance(db, tx.user_id, tx.amount)
                await query.edit_message_text(_('messages.payment_successful', amount=tx.amount, ref_id=ref_id))
        
        else: # Payment failed or not completed
            transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.FAILED)
            await query.edit_message_text(_('messages.payment_failed', error_code=ref_id))

    finally:
        db.close()

    context.user_data.clear()
    return END_CONVERSION


async def back_to_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # (This function remains the same as your original code)
    # ...
    pass

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # (This function remains the same as your original code)
    # ...
    return END_CONVERSION