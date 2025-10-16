"""
Service statistics and analytics for users.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import service_queries, transaction_queries
from database.models.transaction import TransactionType, TransactionStatus, Transaction
from database.models.service import Service
from sqlalchemy import func, extract
from datetime import datetime, timedelta

async def show_my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows user's personal statistics about their usage."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = SessionLocal()
    try:
        # Get active services
        active_services = service_queries.get_user_active_services(db, user_id)
        
        # Get all-time service count
        all_services = db.query(Service).filter(Service.user_id == user_id).all()
        
        # Get spending statistics
        total_spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.type == TransactionType.SERVICE_PURCHASE
        ).scalar() or 0
        
        # Get monthly spending
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.type == TransactionType.SERVICE_PURCHASE,
            extract('month', Transaction.created_at) == current_month,
            extract('year', Transaction.created_at) == current_year
        ).scalar() or 0
        
        text = _('messages.user_stats',
                active_services=len(active_services),
                total_services=len(all_services),
                total_spent=total_spent,
                monthly_spent=monthly_spent)
        
        await query.edit_message_text(text, parse_mode='Markdown')
        
    finally:
        db.close()

