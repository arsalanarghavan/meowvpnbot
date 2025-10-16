# 🚀 راهنمای استقرار کامل ربات VPN

## 📋 پیش‌نیازها

### نرم‌افزارها:
- Python 3.9 یا بالاتر
- PostgreSQL یا SQLite
- یک سرور لینوکس (Ubuntu/Debian توصیه می‌شود)
- یک پنل Marzban فعال و در دسترس

### اطلاعات مورد نیاز:
- توکن ربات تلگرام (از @BotFather)
- آیدی عددی ادمین(ها)
- اطلاعات اتصال به پنل Marzban
- (اختیاری) کد مرچنت زرین‌پال
- (اختیاری) آیدی کانال لاگ

## 📥 نصب

### 1. کلون پروژه
```bash
cd /mnt/1AF200F7F200D941/Projects/Bots
git clone <repository-url> meowvpnbot
cd meowvpnbot
```

### 2. نصب Dependencies
```bash
pip install -r requirements.txt
```

یا با virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # در لینوکس/مک
# یا
venv\Scripts\activate  # در ویندوز

pip install -r requirements.txt
```

### 3. تنظیم فایل .env

فایل `.env` را در ریشه پروژه ایجاد کنید:

```env
# === Telegram Bot Configuration ===
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=YourBotUsername

# === Admin IDs (با کاما جدا شوند) ===
ADMIN_ID=123456789,987654321

# === Database ===
# برای SQLite (توسعه):
DATABASE_URL=sqlite:///./meowvpn.db

# یا برای PostgreSQL (پروداکشن):
# DATABASE_URL=postgresql://user:password@localhost/dbname

# === Logging ===
LOG_CHANNEL_ID=-1001234567890

# === Payment Gateway ===
ZARINPAL_MERCHANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# === Optional ===
CHANNEL_LOCK_ID=@YourChannelUsername
```

### 4. اجرای Migration ها

```bash
# ایجاد اولین migration (اگر وجود ندارد)
alembic revision --autogenerate -m "Initial migration"

# اجرای تمام migration ها
alembic upgrade head
```

## ⚙️ تنظیمات اولیه

### 1. اضافه کردن پنل Marzban

پس از اجرای ربات، از پنل ادمین:
1. وارد «تنظیمات ربات» شوید
2. «مدیریت پنل‌ها» را انتخاب کنید
3. «افزودن پنل جدید» را بزنید
4. اطلاعات پنل را وارد کنید:
   - نام: یک نام توصیفی (مثلاً "پنل اصلی")
   - URL: آدرس کامل پنل (https://panel.example.com)
   - نام کاربری: username ادمین پنل
   - رمز عبور: password ادمین پنل

### 2. ایجاد پلن‌ها

از پنل ادمین:
1. «تنظیمات ربات» → «مدیریت پلن‌ها»
2. «افزودن پلن جدید»
3. مشخصات پلن را وارد کنید:
   - نام
   - دسته‌بندی (عادی، ویژه، گیمینگ، ترید)
   - مدت زمان (روز)
   - حجم (گیگابایت) - 0 برای نامحدود
   - قیمت (تومان)
   - تعداد کاربر همزمان

### 3. تنظیمات پرداخت

از پنل ادمین:
1. «تنظیمات ربات» → «تنظیمات پرداخت»
2. وارد کردن:
   - شماره کارت (برای کارت به کارت)
   - نام صاحب حساب
   - کد مرچنت زرین‌پال (اختیاری)

### 4. تنظیمات کمیسیون

برای فعال‌سازی سیستم بازاریابی:
1. «تنظیمات ربات» → «تنظیمات کمیسیون»
2. افزودن پلکان‌های کمیسیون:
   - مثال: از 0 کاربر → 5%
   - از 10 کاربر → 7%
   - از 50 کاربر → 10%

## 🏃 اجرای ربات

### حالت توسعه:
```bash
python main.py
```

### حالت پروداکشن (با systemd):

#### ایجاد فایل service:
```bash
sudo nano /etc/systemd/system/meowvpnbot.service
```

محتوای فایل:
```ini
[Unit]
Description=MeowVPN Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/mnt/1AF200F7F200D941/Projects/Bots/meowvpnbot
Environment="PATH=/home/your_username/venv/bin"
ExecStart=/home/your_username/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### فعال‌سازی و اجرا:
```bash
sudo systemctl daemon-reload
sudo systemctl enable meowvpnbot
sudo systemctl start meowvpnbot

# بررسی وضعیت:
sudo systemctl status meowvpnbot

# مشاهده لاگ‌ها:
sudo journalctl -u meowvpnbot -f
```

## 🧪 تست ربات

### 1. تست‌های اولیه:
- [ ] ارسال `/start` و بررسی منوی اصلی
- [ ] بررسی دکمه «اطلاعات حساب»
- [ ] بررسی «کیف پول»
- [ ] تست «اکانت تست» (اگر فعال باشد)

### 2. تست خرید:
- [ ] انتخاب دسته‌بندی سرویس
- [ ] انتخاب پلن
- [ ] تایید خرید
- [ ] تست پرداخت از کیف پول
- [ ] تست کارت به کارت
- [ ] دریافت لینک اشتراک

### 3. تست پنل ادمین:
- [ ] ورود با `/admin`
- [ ] بررسی داشبورد
- [ ] جستجوی کاربر
- [ ] تایید رسید
- [ ] ایجاد پلن جدید
- [ ] پیام همگانی

### 4. تست بازاریابی:
- [ ] تبدیل به بازاریاب از دکمه «کسب درآمد»
- [ ] دریافت لینک دعوت
- [ ] ثبت‌نام کاربر جدید با لینک رفرال
- [ ] بررسی کمیسیون پس از خرید
- [ ] درخواست تسویه حساب

## 🔧 رفع مشکلات رایج

### مشکل: ربات پاسخ نمی‌دهد
**راه حل:**
1. توکن ربات را چک کنید
2. اتصال اینترنت سرور را بررسی کنید
3. لاگ‌های ربات را مشاهده کنید
4. مطمئن شوید پورت‌های خروجی باز هستند

### مشکل: خطا در اتصال به پنل
**راه حل:**
1. URL پنل را بررسی کنید (باید https باشد)
2. نام کاربری و رمز عبور را چک کنید
3. مطمئن شوید پنل Marzban در دسترس است
4. فایروال سرور را بررسی کنید

### مشکل: Migration اجرا نمی‌شود
**راه حل:**
```bash
# پاک کردن تاریخچه migration (فقط در توسعه)
alembic downgrade base
alembic upgrade head

# یا ایجاد migration جدید
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

### مشکل: پرداخت آنلاین کار نمی‌کند
**راه حل:**
1. کد مرچنت زرین‌پال را بررسی کنید
2. مطمئن شوید سرور به درگاه دسترسی دارد
3. callback URL ربات را چک کنید

## 📊 Monitoring و نگهداری

### لاگ‌ها:
```bash
# مشاهده لاگ‌های ربات
tail -f /path/to/bot.log

# یا با systemd
sudo journalctl -u meowvpnbot -f --lines=100
```

### پشتیبان‌گیری:

#### پشتیبان‌گیری دستی:
```bash
# برای SQLite
cp meowvpn.db meowvpn_backup_$(date +%Y%m%d).db

# برای PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d).sql
```

#### پشتیبان‌گیری خودکار:
از پنل ادمین ربات، دکمه «پشتیبان‌گیری» را بزنید.

### Job های خودکار:

ربات دارای 2 job خودکار است:

1. **Auto-renewal (ساعت 1 صبح):**
   - بررسی سرویس‌هایی که تمدید خودکار دارند
   - تمدید در صورت موجودی کافی

2. **Notifications (ساعت 9 صبح):**
   - بررسی سرویس‌های در حال انقضا
   - بررسی سرویس‌های با حجم کم
   - ارسال نوتیفیکیشن به کاربران

## 🔒 امنیت

### توصیه‌های امنیتی:

1. **فایل .env را محافظت کنید:**
```bash
chmod 600 .env
```

2. **از HTTPS استفاده کنید:**
   - برای پنل Marzban
   - برای کال‌بک پرداخت

3. **Firewall را تنظیم کنید:**
```bash
# فقط پورت‌های ضروری را باز کنید
ufw allow 22/tcp
ufw allow 443/tcp
ufw enable
```

4. **به‌روزرسانی منظم:**
```bash
# به‌روزرسانی پکیج‌ها
pip install --upgrade -r requirements.txt

# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y
```

5. **پشتیبان‌گیری منظم:**
   - حداقل هفته‌ای یکبار
   - ذخیره در مکان امن (خارج از سرور)

## 🎯 بهینه‌سازی

### برای حجم کاربر بالا:

1. **استفاده از PostgreSQL به جای SQLite**

2. **فعال‌سازی Connection Pooling:**
در `database/engine.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

3. **استفاده از Redis برای Cache:**
(قابلیت آینده - در نسخه‌های بعدی)

4. **افزایش تعداد Worker ها:**
در `main.py`:
```python
application = ApplicationBuilder()\
    .token(BOT_TOKEN)\
    .concurrent_updates(True)\
    .build()
```

## 📱 استفاده از ربات

### برای مشتریان:
1. شروع با `/start`
2. خرید سرویس از منوی «🛍️ خرید سرویس»
3. مدیریت سرویس‌ها از «🔧 مدیریت سرویس»
4. شارژ کیف پول از «💰 کیف پول»
5. کسب درآمد از «💵 کسب درآمد»

### برای بازاریاب‌ها:
1. تبدیل به بازاریاب از «💵 کسب درآمد»
2. دریافت لینک دعوت از «📈 پنل بازاریابی»
3. به اشتراک‌گذاری لینک
4. دریافت کمیسیون از هر خرید
5. درخواست تسویه حساب

### برای ادمین‌ها:
1. ورود به پنل با `/admin`
2. مشاهده داشبورد
3. مدیریت کاربران
4. تایید رسیدها
5. تنظیمات ربات (پلن‌ها، پنل‌ها، متن‌ها)
6. پیام همگانی
7. پشتیبان‌گیری

## 📞 پشتیبانی

در صورت بروز مشکل:

### 1. بررسی لاگ‌ها:
```bash
# لاگ سیستمی
sudo journalctl -u meowvpnbot -n 100

# لاگ کانال تلگرام
# اگر LOG_CHANNEL_ID تنظیم کرده باشید، خطاها در کانال ارسال می‌شوند
```

### 2. دیباگ:
```bash
# اجرا با verbose logging
python main.py
```

### 3. مشکلات رایج:

| مشکل | راه حل |
|------|--------|
| ربات استارت نمی‌خورد | توکن و .env را چک کنید |
| پنل متصل نمیشه | URL، username، password را بررسی کنید |
| پرداخت کار نمی‌کند | کد مرچنت و تنظیمات را چک کنید |
| نوتیفیکیشن ارسال نمیشه | job_queue فعال باشد و کاربر ربات را بلاک نکرده باشد |
| Migration خطا میده | `alembic downgrade base` و دوباره `upgrade head` |

## 🔄 به‌روزرسانی

برای به‌روزرسانی ربات:

```bash
# 1. توقف ربات
sudo systemctl stop meowvpnbot

# 2. پشتیبان‌گیری
cp meowvpn.db meowvpn_backup.db

# 3. دریافت آخرین نسخه
git pull origin main

# 4. به‌روزرسانی dependencies
pip install --upgrade -r requirements.txt

# 5. اجرای migration های جدید
alembic upgrade head

# 6. راه‌اندازی مجدد
sudo systemctl start meowvpnbot
```

## 📈 نکات بهینه‌سازی عملکرد

### 1. Database Optimization:
```sql
-- ایجاد ایندکس‌های مفید
CREATE INDEX idx_services_user_id ON services(user_id);
CREATE INDEX idx_services_expire_date ON services(expire_date);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
```

### 2. Cron Jobs:
اضافه کردن backup خودکار روزانه:
```bash
crontab -e

# اضافه کردن خط زیر:
0 3 * * * cp /path/to/meowvpn.db /path/to/backups/meowvpn_$(date +\%Y\%m\%d).db
```

### 3. Log Rotation:
```bash
sudo nano /etc/logrotate.d/meowvpnbot

# محتوا:
/var/log/meowvpnbot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 your_user your_user
}
```

## 🎊 تبریک!

ربات شما آماده است! اکنون دارای:

✅ سیستم خرید چند روشی
✅ مدیریت چند پنل
✅ سیستم بازاریابی
✅ نوتیفیکیشن‌های هوشمند
✅ داشبورد پیشرفته
✅ FAQ جامع
✅ و بیش از 20 قابلیت دیگر!

**موفق باشید! 🚀**

---

نسخه: 2.5.0 | تاریخ: 2025-10-16

