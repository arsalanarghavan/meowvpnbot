"""
Card Account model for managing multiple card-to-card payment accounts.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime

from database.engine import Base

class CardAccount(Base):
    """Model for managing multiple card accounts with limits and priorities."""
    __tablename__ = 'card_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Card information
    card_number = Column(String(16), nullable=False, unique=True, index=True)
    card_holder = Column(String(100), nullable=False)
    
    # Financial limits
    daily_limit = Column(BigInteger, nullable=False, default=0)  # 0 means unlimited
    current_amount = Column(BigInteger, nullable=False, default=0)  # Amount received today
    
    # Priority and status
    priority = Column(Integer, nullable=False, default=0)  # Lower number = higher priority
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_reset_date = Column(DateTime, nullable=True)  # Last time current_amount was reset
    
    # Notes
    note = Column(String(200), nullable=True)
    
    def __repr__(self):
        return f"<CardAccount(id={self.id}, card_number={self.card_number}, priority={self.priority})>"
    
    def has_capacity(self, amount: int) -> bool:
        """Check if this card has capacity for the given amount."""
        if not self.is_active:
            return False
        
        if self.daily_limit == 0:  # Unlimited
            return True
        
        return (self.current_amount + amount) <= self.daily_limit
    
    def remaining_capacity(self) -> int:
        """Returns the remaining capacity for today."""
        if self.daily_limit == 0:
            return float('inf')
        
        return max(0, self.daily_limit - self.current_amount)

