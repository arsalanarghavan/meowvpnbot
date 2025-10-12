from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, commission_queries
from core.telegram_logger import log_error

async def handle_payout_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a payout request."""
    query = update.callback_query
    await query.answer()

    # callback_data is in the format: 'payout_confirm_{user_id}' or 'payout_reject_{user_id}'
    try:
        # --- FIX: More robust and clearer parsing of the callback data ---
        parts = query.data.split('_')
        action = f"{parts[0]}_{parts[1]}"  # This will result in "payout_confirm" or "payout_reject"
        marketer_id = int(parts[2])
    except (ValueError, IndexError) as e:
        await log_error(context, e, "Parsing payout callback data")
        await query.edit_message_text(_('messages.error_general'), reply_markup=None)
        return

    db = SessionLocal()
    try:
        marketer = user_queries.find_user_by_id(db, marketer_id)
        if not marketer:
            await query.edit_message_text(_('messages.admin_user_not_found'), reply_markup=None)
            return

        original_message = query.message.text

        if action == 'payout_confirm':
            payout_amount = marketer.commission_balance
            if payout_amount > 0:
                # Reset balance and mark commissions as paid
                commission_queries.mark_commissions_as_paid(db, marketer_id)
                user_queries.update_commission_balance(db, marketer_id, -payout_amount)

                # Notify admin and marketer
                new_admin_text = original_message + "\n\n" + _('messages.admin_payout_confirmed', amount=payout_amount)
                await query.edit_message_text(new_admin_text, reply_markup=None)
                await context.bot.send_message(chat_id=marketer_id, text=_('messages.marketer_payout_confirmed', amount=payout_amount))
            else:
                await query.edit_message_text(original_message + "\n\n" + _('messages.payout_error_zero_balance'), reply_markup=None)

        elif action == 'payout_reject':
            new_admin_text = original_message + "\n\n" + _('messages.admin_payout_rejected')
            await query.edit_message_text(new_admin_text, reply_markup=None)
            await context.bot.send_message(chat_id=marketer_id, text=_('messages.marketer_payout_rejected'))
            
    except Exception as e:
        await log_error(context, e, "Handling payout decision")
        await query.edit_message_text(_('messages.error_general_with_details', error=str(e)), reply_markup=None)
    finally:
        db.close()