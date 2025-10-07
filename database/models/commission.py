from sqlalchemy import (Column, Integer, BigInteger, DateTime, Boolean, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from database.engine import Base

class Commission(Base):
    __tablename__ = 'commissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # کاربری که کمیسیون را دریافت می‌کند (بازاریاب)
    marketer_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True)
    
    # کاربری که خرید را انجام داده و معرف داشته است
    referred_user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    
    # تراکنش خریدی که این کمیسیون از آن حاصل شده است
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False, unique=True)
    
    # مبلغ کمیسیون به تومان
    commission_amount = Column(BigInteger, nullable=False)
    
    # تاریخ ثبت کمیسیون
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # آیا این کمیسیون پرداخت شده است؟ (برای مدیریت تسویه حساب)
    is_paid_out = Column(Boolean, default=False, nullable=False)

    marketer = relationship("User", foreign_keys=[marketer_id])
    referred_user = relationship("User", foreign_keys=[referred_user_id])
    transaction = relationship("Transaction")