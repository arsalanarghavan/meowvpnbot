from sqlalchemy.orm import Session
from database.models.commission import Commission
from typing import List

def create_commission(db: Session, marketer_id: int, referred_user_id: int, transaction_id: int, commission_amount: int) -> Commission:
    """Creates a new commission record in the database."""
    new_commission = Commission(
        marketer_id=marketer_id,
        referred_user_id=referred_user_id,
        transaction_id=transaction_id,
        commission_amount=commission_amount
    )
    db.add(new_commission)
    db.commit()
    db.refresh(new_commission)
    return new_commission

def get_unpaid_commissions_by_marketer(db: Session, marketer_id: int) -> List[Commission]:
    """Fetches all unpaid commissions for a specific marketer."""
    return db.query(Commission).filter(
        Commission.marketer_id == marketer_id,
        Commission.is_paid_out == False
    ).all()

def mark_commissions_as_paid(db: Session, marketer_id: int):
    """Marks all unpaid commissions for a marketer as paid."""
    unpaid_commissions = get_unpaid_commissions_by_marketer(db, marketer_id)
    for commission in unpaid_commissions:
        commission.is_paid_out = True
    db.commit()