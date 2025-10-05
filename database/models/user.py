import enum
from datetime import datetime
from sqlalchemy import (Column, Integer, String, BigInteger, DateTime,
                        Enum, Boolean, ForeignKey)
from database.engine import Base

class UserRole(enum.Enum):
    customer = "customer"
    marketer = "marketer"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    wallet_balance = Column(BigInteger, nullable=False, default=0)
    referrer_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    # ---> فیلد جدید <---
    # مشخص می‌کند که آیا کاربر قبلا اکانت تست دریافت کرده است یا خیر
    received_test_account = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, role='{self.role.value}')>"