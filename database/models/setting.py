from sqlalchemy import Column, String
from database.engine import Base

class Setting(Base):
    __tablename__ = 'settings'

    # کلید تنظیمات (مثال: 'card_number', 'zarinpal_merchant_id')
    key = Column(String(50), primary_key=True, index=True)
    
    # مقدار تنظیمات
    value = Column(String(255), nullable=True)