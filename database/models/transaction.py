import enum
from datetime import datetime
from sqlalchemy import (Column, Integer, String, BigInteger, DateTime, 
                        Enum, ForeignKey)
from sqlalchemy.orm import relationship

from database.engine import Base

class TransactionStatus(enum.Enum):
    PENDING = "در انتظار"
    COMPLETED = "موفق"
    FAILED = "ناموفق"

class TransactionType(enum.Enum):
    WALLET_CHARGE = "شارژ کیف پول"
    SERVICE_PURCHASE = "خرید سرویس"
    GIFT_CARD = "کارت هدیه"

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True)
    
    # مبلغ تراکنش به تومان
    amount = Column(BigInteger, nullable=False)
    
    # نوع تراکنش (شارژ کیف پول، خرید و...)
    type = Column(Enum(TransactionType), nullable=False)
    
    # وضعیت تراکنش (در انتظار، موفق، ناموفق)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    
    # کد پیگیری (مثلا کد بازگشتی از درگاه پرداخت یا کد رسید کارت به کارت)
    tracking_code = Column(String(100), nullable=True, unique=True)
    
    # تاریخ و زمان ثبت تراکنش
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User")