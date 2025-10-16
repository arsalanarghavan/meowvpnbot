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
    """Shows transaction history with enhanced details and filter options."""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    db = SessionLocal()
    try:
        # Get filter from callback data if present
        filter_type = None
        if '_' in query.data:
            parts = query.data.split('_')
            if len(parts) > 2:
                filter_type = parts[2]
        
        # Apply filter
        if filter_type and filter_type != 'all':
            from database.models.transaction import TransactionStatus
            status_filter = TransactionStatus[filter_type.upper()] if filter_type != 'all' else None
            transactions = transaction_queries.get_user_transactions_filtered(db, user_id=user_id, status=status_filter, limit=15)
        else:
            transactions = transaction_queries.get_user_transactions(db, user_id=user_id, limit=15)

        if not transactions:
            await query.edit_message_text(_('messages.no_transactions_found'))
            return

        # Calculate summary statistics
        from database.models.transaction import TransactionStatus
        total_completed = sum(tx.amount for tx in transactions if tx.status == TransactionStatus.COMPLETED)
        total_pending = sum(tx.amount for tx in transactions if tx.status == TransactionStatus.PENDING)

        history_text = _('messages.transaction_history_header_enhanced',
                        total_completed=total_completed,
                        total_pending=total_pending) + "\n\n"
        
        for tx in transactions:
            tx_type_key = f"transactions.type.{tx.type.name}"
            status_key = f"transactions.status.{tx.status.name}"
            history_text += _('messages.transaction_history_item',
                             date=tx.created_at.strftime('%Y-%m-%d %H:%M'),
                             type=_(tx_type_key),
                             amount=tx.amount,
                             status=_(status_key)) + "\n"

        # Add filter buttons
        keyboard = [
            [
                InlineKeyboardButton(_('buttons.transaction_filter.all'), callback_data='transaction_history_all'),
                InlineKeyboardButton(_('buttons.transaction_filter.completed'), callback_data='transaction_history_completed')
            ],
            [
                InlineKeyboardButton(_('buttons.transaction_filter.pending'), callback_data='transaction_history_pending'),
                InlineKeyboardButton(_('buttons.transaction_filter.failed'), callback_data='transaction_history_failed')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(history_text, parse_mode='Markdown', reply_markup=reply_markup)
    finally:
        db.close()