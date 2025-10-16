from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models.user import User, UserRole

def find_or_create_user(db: Session, user_id: int, referrer_id: Optional[int] = None) -> User:
    """Finds a user by their Telegram user_id. If not found, creates one with an optional referrer."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user:
        return db_user

    # Only set referrer_id if the user doesn't exist
    new_user = User(user_id=user_id)
    if referrer_id:
        # Check if referrer exists before assigning
        referrer_exists = db.query(User).filter(User.user_id == referrer_id).first()
        if referrer_exists:
            new_user.referrer_id = referrer_id

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def find_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Finds a user by their Telegram user_id. Returns None if not found."""
    return db.query(User).filter(User.user_id == user_id).first()

def update_wallet_balance(db: Session, user_id: int, amount: int) -> Optional[User]:
    """Adds or subtracts a specified amount from a user's wallet balance."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.wallet_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def update_commission_balance(db: Session, user_id: int, amount: int) -> Optional[User]:
    """Adds or subtracts a specified amount from a user's commission balance."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.commission_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, new_role: UserRole) -> Optional[User]:
    """Updates the role of a specific user."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        # Ensure admin role is not assigned accidentally
        if new_role != UserRole.admin and db_user.role == UserRole.admin:
            # Add logic here if you want to prevent demoting an admin, or log it.
            # For now, we allow it.
            pass
        db_user.role = new_role
        db.commit()
        db.refresh(db_user)
    return db_user

def set_user_received_test_account(db: Session, user_id: int) -> Optional[User]:
    """Flags that a user has received their test account."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.received_test_account = True
        db.commit()
        db.refresh(db_user)
    return db_user

def get_total_user_count(db: Session) -> int:
    """Returns the total number of users registered in the bot."""
    return db.query(User).count()

def get_referred_users_count(db: Session, referrer_id: int) -> int:
    """Returns the total number of users referred by a specific user."""
    return db.query(User).filter(User.referrer_id == referrer_id).count()

def get_all_user_ids(db: Session) -> List[int]:
    """Fetches a list of all user_ids from the database."""
    result = db.execute(select(User.user_id))
    return [row[0] for row in result]

def get_user_count_by_role(db: Session, role: str) -> int:
    """Returns the number of users with a specific role."""
    from database.models.user import UserRole
    return db.query(User).filter(User.role == UserRole[role]).count()

def get_active_services_count(db: Session) -> int:
    """Returns the total number of active services."""
    from database.models.service import Service
    return db.query(Service).filter(Service.is_active == True).count()

def get_active_services_by_category(db: Session, category) -> int:
    """Returns the number of active services for a specific plan category."""
    from database.models.service import Service
    from database.models.plan import Plan
    return db.query(Service).join(Plan).filter(
        Service.is_active == True,
        Plan.category == category
    ).count()

def get_total_revenue(db: Session) -> int:
    """Returns the total revenue from all completed transactions."""
    from database.models.transaction import Transaction, TransactionStatus, TransactionType
    from sqlalchemy import func
    result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.type.in_([TransactionType.SERVICE_PURCHASE, TransactionType.WALLET_CHARGE])
    ).scalar()
    return result or 0

def get_monthly_revenue(db: Session) -> int:
    """Returns the revenue from the current month."""
    from database.models.transaction import Transaction, TransactionStatus, TransactionType
    from sqlalchemy import func, extract
    from datetime import datetime
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.status == TransactionStatus.COMPLETED,
        Transaction.type.in_([TransactionType.SERVICE_PURCHASE, TransactionType.WALLET_CHARGE]),
        extract('month', Transaction.created_at) == current_month,
        extract('year', Transaction.created_at) == current_year
    ).scalar()
    return result or 0

def get_total_pending_commissions(db: Session) -> int:
    """Returns the total pending commissions across all marketers."""
    from sqlalchemy import func
    result = db.query(func.sum(User.commission_balance)).filter(
        User.role == UserRole.marketer
    ).scalar()
    return result or 0

def get_active_referrals_count(db: Session, referrer_id: int) -> int:
    """Returns the count of referrals who have at least one active service."""
    from database.models.service import Service
    referred_users = db.query(User.user_id).filter(User.referrer_id == referrer_id).all()
    referred_user_ids = [u[0] for u in referred_users]
    
    if not referred_user_ids:
        return 0
    
    active_users = db.query(Service.user_id).filter(
        Service.user_id.in_(referred_user_ids),
        Service.is_active == True
    ).distinct().count()
    
    return active_users

def get_total_earned_commission(db: Session, referrer_id: int) -> int:
    """Returns the total commission earned by a marketer (including paid out)."""
    from database.models.commission import Commission
    from sqlalchemy import func
    result = db.query(func.sum(Commission.amount)).filter(
        Commission.marketer_id == referrer_id
    ).scalar()
    return result or 0

def get_monthly_earned_commission(db: Session, referrer_id: int) -> int:
    """Returns the commission earned this month by a marketer."""
    from database.models.commission import Commission
    from sqlalchemy import func, extract
    from datetime import datetime
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    result = db.query(func.sum(Commission.amount)).filter(
        Commission.marketer_id == referrer_id,
        extract('month', Commission.created_at) == current_month,
        extract('year', Commission.created_at) == current_year
    ).scalar()
    return result or 0