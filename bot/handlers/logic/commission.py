from sqlalchemy.orm import Session
from database.models.transaction import Transaction
from database.queries import user_queries, setting_queries, commission_queries
from core.logger import get_logger

logger = get_logger(__name__)

def award_commission_for_purchase(db: Session, transaction: Transaction):
    """
    Checks if a purchase was made by a referred user and awards commission to the referrer.
    This function should be called after a transaction is successfully completed.
    """
    purchasing_user = transaction.user
    
    # 1. Check if the user was referred by someone
    if not purchasing_user.referrer_id:
        return

    referrer = user_queries.find_user_by_id(db, purchasing_user.referrer_id)
    
    # 2. Check if the referrer exists and is a marketer or admin
    if not referrer or referrer.role not in ['marketer', 'admin']:
        return

    # 3. Get the commission rate from settings
    try:
        commission_rate_str = setting_queries.get_setting(db, 'commission_rate', '0')
        commission_rate = int(commission_rate_str)
    except (ValueError, TypeError):
        commission_rate = 0
        
    if commission_rate <= 0:
        return

    # 4. Calculate commission
    commission_amount = (transaction.amount * commission_rate) // 100
    if commission_amount <= 0:
        return

    # 5. Create a commission record and update the referrer's balance
    try:
        commission_queries.create_commission(
            db,
            marketer_id=referrer.user_id,
            referred_user_id=purchasing_user.user_id,
            transaction_id=transaction.id,
            commission_amount=commission_amount
        )
        user_queries.update_commission_balance(db, referrer.user_id, commission_amount)
        logger.info(f"Awarded {commission_amount} commission to marketer {referrer.user_id} for transaction {transaction.id}")
    except Exception as e:
        logger.error(f"Failed to award commission for transaction {transaction.id}: {e}", exc_info=True)
        # In a real-world scenario, you might want to handle this error more robustly,
        # e.g., by rolling back the transaction or flagging it for manual review.