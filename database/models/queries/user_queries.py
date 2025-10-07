from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from database.models.user import User

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

def find_user_by_id(db: Session, user_id: int) -> User:
    """Finds a user by their Telegram user_id. Returns None if not found."""
    return db.query(User).filter(User.user_id == user_id).first()

def update_wallet_balance(db: Session, user_id: int, amount: int) -> User:
    """Adds or subtracts a specified amount from a user's wallet balance."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.wallet_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def update_commission_balance(db: Session, user_id: int, amount: int) -> User:
    """Adds or subtracts a specified amount from a user's commission balance."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.commission_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user

def set_user_received_test_account(db: Session, user_id: int) -> User:
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