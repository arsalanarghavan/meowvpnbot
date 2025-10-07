import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from core.translator import _
from core.config import ADMIN_ID
from database.engine import SessionLocal
from database.models.transaction import TransactionType, TransactionStatus
from database.queries import (transaction_queries, user_queries, service_queries,
                              panel_queries, setting_queries)
from bot.keyboards.inline_keyboards import (get_payment_methods_keyboard,
                                            get_admin_receipt_confirmation_keyboard,
                                            get_wallet_menu_keyboard,
                                            get_online_payment_keyboard)
from bot.states.conversation_states import (AWAITING_AMOUNT, AWAITING_RECEIPT,
                                            AWAITING_ONLINE_PAYMENT_VERIFICATION, END_CONVERSION)
from services.zarinpal import Zarinpal
from services.marzban_api import MarzbanAPI
from bot.logic.commission import award_commission_for_purchase # <-- ایمپورت جدید


async def ask_for_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user to choose a payment method for increasing balance."""
    query = update.callback_query
    await query.answer()

    context.user_data['purchase_flow'] = False
    context.user_data.pop('selected_plan', None)  # Clear any selected plan

    # Store the message to edit it after getting the amount
    context.user_data['message_to_edit'] = query.message.message_id
    await query.edit_message_text(_('messages.enter_charge_amount'))
    return AWAITING_AMOUNT


async def receive_charge_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the amount to charge the wallet and shows payment methods."""
    try:
        amount = int(update.message.text)
        if amount < 1000:  # Zarinpal has a minimum amount of 1000 Toman
            raise ValueError
        context.user_data['charge_amount'] = amount
        # Delete the user's message (the amount)
        await update.message.delete()
    except (ValueError, TypeError):
        await update.message.reply_text(_('messages.error_invalid_amount_min_1000'))
        # We stay in the same state to ask for the amount again
        return AWAITING_AMOUNT

    text = _('messages.choose_payment_method')
    reply_markup = get_payment_methods_keyboard(purchase_flow=False)

    # Edit the original message ("Enter charge amount") to show payment methods
    message_id_to_edit = context.user_data.get('message_to_edit')
    if message_id_to_edit:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id_to_edit,
            text=text,
            reply_markup=reply_markup
        )
    else: # Fallback
        await update.message.reply_text(text=text, reply_markup=reply_markup)

    # The conversation about getting the amount is over.
    # The next step will be triggered by a callback query for the payment method.
    return END_CONVERSION


async def card_to_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the card-to-card payment process, either from purchase or wallet charge."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    db = SessionLocal()
    try:
        # Get card info from settings
        card_number = setting_queries.get_setting(db, 'card_number', _('messages.setting_not_set'))
        card_holder = setting_queries.get_setting(db, 'card_holder', _('messages.setting_not_set'))

        plan = context.user_data.get('selected_plan')
        if plan:
            # We are in a purchase flow
            amount = plan.price
            tx = transaction_queries.create_transaction(
                db, user_id=user.id, amount=amount, tx_type=TransactionType.SERVICE_PURCHASE, plan_id=plan.id
            )
        else:
            # This is a wallet charge flow
            amount = context.user_data.get('charge_amount')
            if not amount:
                await query.edit_message_text(_('messages.error_general'))
                return END_CONVERSION
            tx = transaction_queries.create_transaction(
                db, user_id=user.id, amount=amount, tx_type=TransactionType.WALLET_CHARGE
            )

        context.user_data['active_tx_id'] = tx.id

        card_info_text = _('messages.card_to_card_instructions',
                           amount=amount,
                           tx_id=tx.id,
                           card_number=card_number,
                           card_holder=card_holder)
        await query.edit_message_text(text=card_info_text)

    finally:
        db.close()

    return AWAITING_RECEIPT


async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's sent receipt and forwards it to the admin."""
    user = update.effective_user
    tx_id = context.user_data.get('active_tx_id')

    if not tx_id:
        await update.message.reply_text(_('messages.error_general'))
        return END_CONVERSION

    db = SessionLocal()
    try:
        tx = transaction_queries.get_transaction_by_id(db, tx_id)

        admin_message = _('messages.admin_receipt_notification',
                          user_id=user.id,
                          first_name=user.first_name,
                          amount=tx.amount,
                          tx_id=tx.id)

        reply_markup = get_admin_receipt_confirmation_keyboard(tx.id)

        # Forward the message (photo or text)
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user.id, message_id=update.message.message_id)
        # Send the details and confirmation buttons
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, reply_markup=reply_markup)

        await update.message.reply_text(_('messages.receipt_sent_for_review'))

    finally:
        db.close()

    context.user_data.clear()
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
        if not zarinpal_api.merchant_id:
            await query.edit_message_text(_('messages.error_payment_gateway_not_configured'))
            transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.FAILED)
            return END_CONVERSION

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
                if not panels:
                    await query.edit_message_text(_('messages.no_panels_configured'))
                    return END_CONVERSION
                
                service_username = f"uid{tx.user_id}-{uuid.uuid4().hex[:8]}"
                user_details_list = []

                for panel in panels:
                    try:
                        api = MarzbanAPI(panel)
                        user_details = await api.create_user(plan=tx.plan, username=service_username)
                        user_details_list.append(user_details)
                    except Exception as e:
                        print(f"Failed to create user on panel {panel.name} during online payment: {e}")
                
                if not user_details_list:
                    await query.edit_message_text(_('messages.error_all_panels_failed'))
                    transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.FAILED) # Revert tx
                    return END_CONVERSION

                combined_sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
                service_queries.create_service_record(db, tx.user_id, tx.plan, service_username)

                # --- Award Commission ---
                award_commission_for_purchase(db, tx)
                # ---
                
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
    """Callback query handler to go back to the wallet menu."""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, query.from_user.id)
        balance = db_user.wallet_balance
        wallet_text = _('messages.wallet_info', balance=balance)
        reply_markup = get_wallet_menu_keyboard()
        await query.edit_message_text(wallet_text, reply_markup=reply_markup)
    finally:
        db.close()


async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the payment conversation."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(_('messages.operation_cancelled'))
    else:
        await update.message.reply_text(_('messages.operation_cancelled'))
    context.user_data.clear()
    return END_CONVERSION