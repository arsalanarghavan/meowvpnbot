from sqlalchemy.orm import Session
from database.models.user import User

def find_or_create_user(db: Session, user_id: int) -> User:
    """Finds a user by their Telegram user_id. If not found, creates one."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user:
        return db_user
    new_user = User(user_id=user_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def find_user_by_id(db: Session, user_id: int) -> User:
    """Finds a user by their Telegram user_id. Returns None if not found."""
    return db.query(User).filter(User.user_id == user_id).first()

def update_wallet_balance(db: Session, user_id: int, amount: int) -> User:
    """Adds a specified amount to a user's wallet balance."""
    db_user = find_user_by_id(db, user_id)
    if db_user:
        db_user.wallet_balance += amount
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