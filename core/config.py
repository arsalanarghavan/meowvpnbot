import os
from dotenv import load_dotenv
from typing import List, Optional

# از پوشه اصلی پروژه، فایل .env را بارگذاری می‌کند
load_dotenv()

# --- Telegram Bot Configuration ---
# توکن ربات تلگرام که به صورت رشته خوانده می‌شود
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# یوزرنیم ربات تلگرام (بدون @) که برای ساخت لینک بازگشت از درگاه پرداخت لازم است
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

# FIX: Support for multiple admin IDs
def get_admin_ids() -> List[int]:
    """Reads comma-separated admin IDs from .env and returns a list of integers."""
    admin_ids_str = os.getenv("ADMIN_ID")
    if not admin_ids_str:
        return []
    try:
        # Split the string by comma and convert each part to an integer
        return [int(admin_id.strip()) for admin_id in admin_ids_str.split(',')]
    except (ValueError, TypeError):
        return []

# آیدی‌های عددی ادمین‌ها به صورت لیستی از اعداد صحیح
ADMIN_IDS = get_admin_ids()
# For backward compatibility, keep a single ADMIN_ID if needed (e.g., for logging)
ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else None


# --- Database Configuration ---
# آدرس اتصال به دیتابیس
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Logging Configuration ---
# آیدی کانالی که می‌خواهید لاگ‌ها و خطاها در آن ارسال شود
LOG_CHANNEL_ID = None
log_channel_id_str = os.getenv("LOG_CHANNEL_ID")
if log_channel_id_str:
    try:
        LOG_CHANNEL_ID = int(log_channel_id_str.strip())
    except (ValueError, TypeError):
        # اگر مقدار نامعتبر باشد، None می‌ماند و warning نمی‌دهیم (اختیاری است)
        pass


# --- Marzban Panel API Configuration ---
# این بخش دیگر به صورت مستقیم استفاده نمی‌شود و اطلاعات پنل‌ها از دیتابیس خوانده می‌شود
# اما برای حفظ ساختار اولیه، می‌توانید آن‌ها را نگه دارید یا حذف کنید.
MARZBAN_API_BASE_URL = os.getenv("MARZBAN_API_BASE_URL")
MARZBAN_API_USERNAME = os.getenv("MARZBAN_API_USERNAME")
MARZBAN_API_PASSWORD = os.getenv("MARZBAN_API_PASSWORD")

# --- Payment Gateway Configuration ---
# کد مرچنت درگاه پرداخت زرین‌پال
ZARINPAL_MERCHANT_ID = os.getenv("ZARINPAL_MERCHANT_ID")

# --- Optional Settings ---
# آیدی کانال برای قفل عضویت اجباری
CHANNEL_LOCK_ID = os.getenv("CHANNEL_LOCK_ID")