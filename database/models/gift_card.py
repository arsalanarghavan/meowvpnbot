from sqlalchemy import (Column, Integer, String, BigInteger, Boolean, ForeignKey)
from sqlalchemy.orm import relationship

from database.engine import Base

class GiftCard(Base):
    __tablename__ = 'gift_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # کد منحصر به فرد کارت هدیه (مثلا: 8-4-4-12 UUID)
    code = Column(String(50), nullable=False, unique=True, index=True)
    
    # مبلغ کارت هدیه به تومان
    amount = Column(BigInteger, nullable=False)
    
    # وضعیت کارت (استفاده شده یا نشده)
    is_used = Column(Boolean, nullable=False, default=False)
    
    # کاربری که از کارت استفاده کرده است
    used_by_user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=True)
    
    # برای دسترسی به اطلاعات کاربری که از کارت استفاده کرده
    user = relationship("User")