"""
Query functions for managing card accounts.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database.models.card_account import CardAccount

def create_card_account(db: Session, card_number: str, card_holder: str, 
                       daily_limit: int = 0, priority: int = 0, note: str = None) -> CardAccount:
    """Creates a new card account."""
    new_card = CardAccount(
        card_number=card_number,
        card_holder=card_holder,
        daily_limit=daily_limit,
        priority=priority,
        note=note
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

def get_all_cards(db: Session, only_active: bool = False) -> List[CardAccount]:
    """Returns all card accounts, optionally filtered by active status."""
    query = db.query(CardAccount).order_by(CardAccount.priority.asc())
    
    if only_active:
        query = query.filter(CardAccount.is_active == True)
    
    return query.all()

def get_card_by_id(db: Session, card_id: int) -> Optional[CardAccount]:
    """Returns a specific card account by ID."""
    return db.query(CardAccount).filter(CardAccount.id == card_id).first()

def get_available_card_for_amount(db: Session, amount: int) -> Optional[CardAccount]:
    """
    Returns the highest priority card that has capacity for the given amount.
    Priority is determined by the 'priority' field (lower number = higher priority).
    """
    cards = db.query(CardAccount).filter(
        CardAccount.is_active == True
    ).order_by(CardAccount.priority.asc()).all()
    
    for card in cards:
        if card.has_capacity(amount):
            return card
    
    return None  # No card has capacity

def add_amount_to_card(db: Session, card_id: int, amount: int) -> Optional[CardAccount]:
    """Adds an amount to a card's current daily total."""
    card = get_card_by_id(db, card_id)
    if card:
        card.current_amount += amount
        db.commit()
        db.refresh(card)
    return card

def reset_daily_amounts(db: Session) -> int:
    """
    Resets the current_amount for all cards to 0.
    Returns the number of cards reset.
    """
    cards = db.query(CardAccount).all()
    count = 0
    
    for card in cards:
        card.current_amount = 0
        card.last_reset_date = datetime.utcnow()
        count += 1
    
    db.commit()
    return count

def update_card(db: Session, card_id: int, **kwargs) -> Optional[CardAccount]:
    """Updates a card account with the provided fields."""
    card = get_card_by_id(db, card_id)
    if card:
        for key, value in kwargs.items():
            if hasattr(card, key):
                setattr(card, key, value)
        db.commit()
        db.refresh(card)
    return card

def delete_card(db: Session, card_id: int) -> bool:
    """Deletes a card account."""
    card = get_card_by_id(db, card_id)
    if card:
        db.delete(card)
        db.commit()
        return True
    return False

def toggle_card_status(db: Session, card_id: int) -> Optional[CardAccount]:
    """Toggles the is_active status of a card."""
    card = get_card_by_id(db, card_id)
    if card:
        card.is_active = not card.is_active
        db.commit()
        db.refresh(card)
    return card

def get_card_statistics(db: Session, card_id: int) -> dict:
    """Returns statistics for a specific card."""
    card = get_card_by_id(db, card_id)
    if not card:
        return {}
    
    return {
        'card_number': card.card_number,
        'current_amount': card.current_amount,
        'daily_limit': card.daily_limit,
        'remaining_capacity': card.remaining_capacity(),
        'usage_percentage': (card.current_amount / card.daily_limit * 100) if card.daily_limit > 0 else 0,
        'is_active': card.is_active,
        'priority': card.priority
    }

