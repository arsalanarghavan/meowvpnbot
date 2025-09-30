import uuid
from typing import List
from sqlalchemy.orm import Session
from database.models.gift_card import GiftCard

def create_gift_cards(db: Session, amount: int, count: int) -> List[str]:
    """Creates a specified number of gift cards with a given amount."""
    new_codes = []
    for _ in range(count):
        # Generate a unique code
        code = str(uuid.uuid4())
        new_card = GiftCard(code=code, amount=amount)
        db.add(new_card)
        new_codes.append(code)
    db.commit()
    return new_codes

def find_gift_card_by_code(db: Session, code: str) -> GiftCard:
    """Finds a gift card by its code."""
    return db.query(GiftCard).filter(GiftCard.code == code).first()

def redeem_gift_card(db: Session, card: GiftCard, user_id: int) -> GiftCard:
    """Marks a gift card as used by a specific user."""
    card.is_used = True
    card.used_by_user_id = user_id
    db.commit()
    db.refresh(card)
    return card