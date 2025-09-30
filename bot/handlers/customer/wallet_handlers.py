from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, transaction_queries
from bot.keyboards.inline_keyboards import get_wallet_menu_keyboard

async def wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the wallet menu with current balance and options."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id=user_id)
        balance = db_user.wallet_balance
        
        wallet_text = _('messages.wallet_info', balance=balance)
        reply_markup = get_wallet_menu_keyboard()
        
        await update.message.reply_text(wallet_text, reply_markup=reply_markup)
    finally:
        db.close()

async def transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback query handler to display user's transaction history."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        transactions = transaction_queries.get_user_transactions(db, user_id=user_id)
        
        if not transactions:
            history_text = _('messages.no_transactions_found')
        else:
            history_text = _('messages.transaction_history_header') + "\n\n"
            for tx in transactions:
                status = _(f'transactions.status.{tx.status.value}')
                tx_type = _(f'transactions.type.{tx.type.value}')
                # تاریخ را برای نمایش بهتر فرمت می‌کنیم
                date_str = tx.created_at.strftime('%Y-%m-%d %H:%M')
                history_text += _('messages.transaction_history_item',
                                  date=date_str,
                                  type=tx_type,
                                  amount=tx.amount,
                                  status=status)
    finally:
        db.close()
        
    await query.edit_message_text(text=history_text)