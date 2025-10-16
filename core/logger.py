import logging
import sys

# سطح لاگ‌گیری را بر روی INFO تنظیم می‌کنیم تا پیام‌های اطلاعاتی، هشدارها و خطاها نمایش داده شوند
# برای دیباگ دقیق‌تر می‌توانید آن را به logging.DEBUG تغییر دهید
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # لاگ‌ها را در یک فایل به نام bot.log ذخیره می‌کند
        logging.FileHandler("bot.log"),
        # لاگ‌ها را در ترمینال یا کنسول نیز نمایش می‌دهد
        logging.StreamHandler(sys.stdout)
    ]
)

# یک لاگر اختصاصی برای کتابخانه تلگرام می‌گیریم تا لاگ‌های آن نیز مدیریت شود
logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str):
    """یک نمونه لاگر با نام مشخص برمی‌گرداند."""
    return logging.getLogger(name)