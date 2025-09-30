from typing import List
from sqlalchemy.orm import Session
from database.models.transaction import Transaction, TransactionType, TransactionStatus

def get_user_transactions(db: Session, user_id: int, limit: int = 10) -> List[Transaction]:
    """
    Fetches the most recent transactions for a specific user from the database.
    """
    return db.query(Transaction).filter(Transaction.user_id == user_id)\
                                .order_by(Transaction.created_at.desc())\
                                .limit(limit).all()

def create_transaction(db: Session, user_id: int, amount: int, tx_type: TransactionType) -> Transaction:
    """Creates a new transaction record in the database."""
    new_tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=tx_type,
        status=TransactionStatus.PENDING
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

def get_transaction_by_id(db: Session, tx_id: int) -> Transaction:
    """Finds a transaction by its ID."""
    return db.query(Transaction).filter(Transaction.id == tx_id).first()

def update_transaction_status(db: Session, tx_id: int, status: TransactionStatus) -> Transaction:
    """Updates the status of a specific transaction."""
    db_tx = get_transaction_by_id(db, tx_id)
    if db_tx:
        db_tx.status = status
        db.commit()
        db.refresh(db_tx)
    return db_tx