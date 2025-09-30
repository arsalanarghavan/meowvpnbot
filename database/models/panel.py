from sqlalchemy import (Column, Integer, String, Boolean)
from database.engine import Base

class Panel(Base):
    __tablename__ = 'panels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # نام پنل برای شناسایی توسط ادمین (مثال: پنل اصلی آلمان)
    name = Column(String(100), nullable=False)
    
    # آدرس اصلی پنل برای ارسال درخواست‌های API
    api_base_url = Column(String(255), nullable=False, unique=True)
    
    # نام کاربری ادمین پنل
    username = Column(String(100), nullable=False)
    
    # رمز عبور ادمین پنل
    password = Column(String(100), nullable=False)
    
    # وضعیت پنل (فعال/غیرفعال)
    is_active = Column(Boolean, nullable=False, default=True)