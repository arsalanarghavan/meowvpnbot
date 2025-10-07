from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, commission_queries

async def handle_payout_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles admin's decision on a payout request."""
    query = update.callback_query
    await query.answer()

    action, marketer_id_str = query.data.split('_', 1)
    marketer_id = int(marketer_id_str)
    
    db = SessionLocal()
    try:
        marketer = user_queries.find_user_by_id(db, marketer_id)
        if not marketer:
            await query.edit_message_text("کاربر یافت نشد.", reply_markup=None)
            return

        original_message = query.message.text
        
        if action == 'payoutconfirm':
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
                await query.edit_message_text(original_message + "\n\n" + "موجودی کاربر برای تسویه صفر است.", reply_markup=None)

        elif action == 'payoutreject':
            new_admin_text = original_message + "\n\n" + _('messages.admin_payout_rejected')
            await query.edit_message_text(new_admin_text, reply_markup=None)
            await context.bot.send_message(chat_id=marketer_id, text=_('messages.marketer_payout_rejected'))
            
    finally:
        db.close()