import json
from sqlalchemy.orm import Session
from database.models.transaction import Transaction
from database.queries import user_queries, setting_queries, commission_queries
from core.logger import get_logger
from core.telegram_logger import log_error

logger = get_logger(__name__)

def award_commission_for_purchase(db: Session, transaction: Transaction):
    """
    Checks if a purchase was made by a referred user and awards commission to the referrer
    based on a tiered (stepped) system defined by the admin.
    This function should be called after a transaction is successfully completed.
    """
    try:
        purchasing_user = transaction.user
        
        # 1. Check if the user was referred by someone
        if not purchasing_user.referrer_id:
            return

        referrer = user_queries.find_user_by_id(db, purchasing_user.referrer_id)
        
        # 2. Check if the referrer exists and is a marketer or admin
        if not referrer or referrer.role.value not in ['marketer', 'admin']:
            return

        # 3. Get the tiered commission settings from the database (stored as JSON)
        # Example format: '[{"threshold": 0, "rate": 10}, {"threshold": 10, "rate": 15}]'
        commission_tiers_json = setting_queries.get_setting(db, 'commission_tiers', '[]')
        try:
            # Sort tiers by threshold to ensure correct logic
            commission_tiers = sorted(json.loads(commission_tiers_json), key=lambda x: x['threshold'])
        except (json.JSONDecodeError, TypeError):
            commission_tiers = []

        if not commission_tiers:
            logger.info("Commission awarding skipped: No commission tiers are set.")
            return

        # 4. Determine the correct commission rate based on the number of referred users
        referred_count = user_queries.get_referred_users_count(db, referrer.user_id)
        commission_rate = 0
        # Iterate through tiers in reverse to find the highest applicable tier
        for tier in reversed(commission_tiers):
            if referred_count >= tier['threshold']:
                commission_rate = tier['rate']
                break
                
        if commission_rate <= 0:
            return

        # 5. Calculate commission amount
        commission_amount = (transaction.amount * commission_rate) // 100
        if commission_amount <= 0:
            return

        # 6. Create a commission record and update the referrer's balance
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
        # In a real application, you might need a context object to log this to a Telegram channel
        # For now, it logs to the file/console.