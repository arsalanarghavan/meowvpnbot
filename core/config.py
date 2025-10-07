import os
from dotenv import load_dotenv

# از پوشه اصلی پروژه، فایل .env را بارگذاری می‌کند
load_dotenv()

# --- Telegram Bot Configuration ---
# توکن ربات تلگرام که به صورت رشته خوانده می‌شود
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# یوزرنیم ربات تلگرام (بدون @) که برای ساخت لینک بازگشت از درگاه پرداخت لازم است
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

# آیدی عددی ادمین اصلی که خوانده شده و به عدد صحیح (integer) تبدیل می‌شود
# در صورتی که مقداری برای آن تعیین نشده باشد، None در نظر گرفته می‌شود
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None

# --- Database Configuration ---
# آدرس اتصال به دیتابیس
DATABASE_URL = os.getenv("DATABASE_URL")

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