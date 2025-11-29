from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL  # آدرس دیتابیس را از فایل تنظیمات می‌خوانیم

# بررسی DATABASE_URL قبل از استفاده
if not DATABASE_URL or DATABASE_URL == "your_database_url":
    raise ValueError(
        "DATABASE_URL is not set or is invalid! "
        "Please set DATABASE_URL in .env file. "
        "Example: DATABASE_URL=sqlite:///vpn_bot.db"
    )

# ایجاد موتور اصلی SQLAlchemy با استفاده از آدرس اتصال
# pool_pre_ping=True به موتور دستور می‌دهد که قبل از هر عملیات، اتصال به دیتابیس را چک کند تا از قطعی جلوگیری شود
# pool_size: تعداد اتصالات همزمان در pool
# max_overflow: حداکثر اتصالات اضافی که می‌تواند ایجاد شود
# pool_timeout: زمان انتظار برای دریافت اتصال از pool (ثانیه)
# pool_recycle: زمان بازسازی اتصالات (ثانیه) - برای جلوگیری از timeout
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # 1 hour
    echo=False  # Set to True for SQL query logging in development
)

# ایجاد یک کلاس SessionLocal که هر نمونه از آن یک جلسه دیتابیس جدید خواهد بود
# autocommit=False و autoflush=False تنظیمات استاندارد برای کنترل دستی تراکنش‌ها هستند
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ایجاد یک کلاس Base که تمام مدل‌های دیتابیس ما (جداول) از آن ارث‌بری خواهند کرد
Base = declarative_base()

# یک تابع کمکی برای ایجاد و بستن خودکار جلسه دیتابیس
# این تابع تضمین می‌کند که پس از اتمام کار، اتصال به دیتابیس به درستی بسته شود
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()