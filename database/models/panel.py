from sqlalchemy import (Column, Integer, String, Boolean, Enum as SQLEnum)
from database.engine import Base
import enum

class PanelType(enum.Enum):
    """نوع پنل VPN"""
    MARZBAN = "marzban"
    HIDDIFY = "hiddify"

class Panel(Base):
    __tablename__ = 'panels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # نام پنل برای شناسایی توسط ادمین (مثال: پنل اصلی آلمان)
    name = Column(String(100), nullable=False)
    
    # نوع پنل (Marzban یا Hiddify)
    panel_type = Column(SQLEnum(PanelType), nullable=False, default=PanelType.MARZBAN)
    
    # آدرس اصلی پنل برای ارسال درخواست‌های API
    api_base_url = Column(String(255), nullable=False, unique=True)
    
    # نام کاربری ادمین پنل
    username = Column(String(100), nullable=False)
    
    # رمز عبور ادمین پنل
    password = Column(String(100), nullable=False)
    
    # وضعیت پنل (فعال/غیرفعال)
    is_active = Column(Boolean, nullable=False, default=True)