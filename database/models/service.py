from datetime import datetime
from sqlalchemy import (Column, Integer, String, BigInteger, DateTime, 
                        Boolean, ForeignKey)
from sqlalchemy.orm import relationship

from database.engine import Base

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # کلید خارجی برای اتصال به جدول کاربران
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True)
    
    # کلید خارجی برای اتصال به جدول پلن‌ها
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    
    # نام کاربری که برای این سرویس در پنل مرزبان ساخته شده است
    username_in_panel = Column(String(100), nullable=False, unique=True)
    
    # یادداشتی که کاربر برای سرویس خود انتخاب می‌کند (مثال: گوشی شخصی)
    note = Column(String(100), nullable=True)
    
    # تاریخ شروع سرویس
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # تاریخ انقضای سرویس
    expire_date = Column(DateTime, nullable=False)
    
    # وضعیت تمدید خودکار
    auto_renew = Column(Boolean, nullable=False, default=False)
    
    # وضعیت کلی سرویس (فعال، منقضی شده، لغو شده)
    is_active = Column(Boolean, nullable=False, default=True)

    # ایجاد ارتباط با مدل‌های دیگر برای دسترسی راحت‌تر
    user = relationship("User")
    plan = relationship("Plan")