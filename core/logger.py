import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# تنظیمات لاگ
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB default
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))  # Keep 5 backup files

# تبدیل سطح لاگ از رشته به عدد
log_level = getattr(logging, LOG_LEVEL, logging.INFO)

# ایجاد formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Handler برای فایل با rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)

# Handler برای کنسول
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)
console_handler.setFormatter(formatter)

# تنظیم root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# کاهش سطح لاگ برای کتابخانه‌های خارجی
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str):
    """یک نمونه لاگر با نام مشخص برمی‌گرداند."""
    return logging.getLogger(name)