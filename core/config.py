import os
from dotenv import load_dotenv
from typing import List, Optional

# از پوشه اصلی پروژه، فایل .env را بارگذاری می‌کند
load_dotenv()

def validate_config():
    """Validates required environment variables at startup."""
    errors = []
    warnings = []
    
    # Required variables
    required_vars = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
    }
    
    for var_name, var_value in required_vars.items():
        if not var_value or var_value in ["your_bot_token_here", "your_database_url"]:
            errors.append(f"{var_name} is not set or has default value")
    
    # Validate DATABASE_URL format
    db_url = required_vars["DATABASE_URL"]
    if db_url:
        if not db_url.startswith(("sqlite:///", "postgresql://", "mysql://")):
            errors.append("DATABASE_URL must start with sqlite:///, postgresql://, or mysql://")
        # Check for credentials in URL (security warning)
        if "://" in db_url and "@" in db_url:
            if "password" in db_url.lower() or "pass" in db_url.lower():
                # Password should be in URL, but warn if it's too simple
                pass
    
    # Validate BOT_TOKEN format (Telegram bot tokens have format: numbers:letters)
    bot_token = required_vars.get("TELEGRAM_BOT_TOKEN")
    if bot_token and bot_token != "your_bot_token_here":
        if ":" not in bot_token or len(bot_token) < 30:
            errors.append("TELEGRAM_BOT_TOKEN format appears invalid")
    
    # Check optional but recommended variables
    if not os.getenv("ADMIN_ID"):
        warnings.append("ADMIN_ID is not set - admin commands will not work")
    
    if not os.getenv("ZARINPAL_MERCHANT_ID"):
        warnings.append("ZARINPAL_MERCHANT_ID is not set - online payments will not work")
    
    # Security checks
    if os.getenv("LOG_CHANNEL_ID"):
        try:
            log_channel = int(os.getenv("LOG_CHANNEL_ID"))
            if log_channel > 0:
                warnings.append("LOG_CHANNEL_ID should be negative for channels")
        except (ValueError, TypeError):
            warnings.append("LOG_CHANNEL_ID format may be invalid")
    
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        if warnings:
            error_msg += "\n\nWarnings:\n" + "\n".join(f"  - {w}" for w in warnings)
        raise ValueError(error_msg)
    
    if warnings:
        import warnings as py_warnings
        for warning in warnings:
            py_warnings.warn(warning, UserWarning)
    
    return True

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