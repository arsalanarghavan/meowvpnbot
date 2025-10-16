# 🚀 راهنمای نصب و به‌روزرسانی خودکار

## ⚡ نصب با یک دستور!

### روش 1: نصب سریع (توصیه می‌شود) ⭐

```bash
bash install.sh
```

**همین!** اسکریپت خودکار همه چیز را انجام می‌دهد:
- ✅ بررسی Python و pip
- ✅ ایجاد virtual environment
- ✅ نصب dependencies
- ✅ تنظیم .env
- ✅ اجرای migrations
- ✅ (اختیاری) ایجاد systemd service

---

### روش 2: نصب دستی

```bash
# 1. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. تنظیمات
cp .env.example .env
nano .env  # ویرایش کنید

# 4. Database
alembic upgrade head

# 5. اجرا
python main.py
```

---

## 🔄 به‌روزرسانی با یک دستور!

### استفاده از Updater:

```bash
bash update.sh
```

این اسکریپت خودکار:
- ✅ پشتیبان‌گیری از دیتابیس
- ✅ دریافت آخرین نسخه (git pull)
- ✅ به‌روزرسانی dependencies
- ✅ اجرای migrations جدید
- ✅ پاک‌سازی cache
- ✅ ریستارت ربات

---

## 📋 جزئیات اسکریپت Installer

### چه کارهایی انجام می‌دهد؟

#### 1. بررسی پیش‌نیازها
- بررسی نصب Python 3.9+
- بررسی نصب pip
- نصب خودکار pip در صورت عدم وجود

#### 2. محیط مجازی (Virtual Environment)
- ایجاد venv در پوشه پروژه
- فعال‌سازی خودکار
- جداسازی dependencies

#### 3. نصب Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

شامل:
- python-telegram-bot
- sqlalchemy
- alembic
- و سایر dependencies

#### 4. تنظیم .env
- کپی از .env.example
- پرسش برای ویرایش فوری
- راهنمای تنظیمات

#### 5. Database Migration
```bash
alembic upgrade head
```

- ایجاد تمام جداول
- اجرای تمام migrations

#### 6. Systemd Service (اختیاری)
- ایجاد خودکار فایل service
- فعال‌سازی برای اجرای خودکار در بوت
- راهنمای دستورات مدیریت

---

## 📋 جزئیات اسکریپت Updater

### چه کارهایی انجام می‌دهد؟

#### 1. بررسی وضعیت
- تشخیص ربات در حال اجرا
- توقف امن ربات

#### 2. پشتیبان‌گیری
**SQLite:**
```bash
backups/backup_20251016_120000.db
```

**PostgreSQL:**
راهنمای دستور pg_dump

#### 3. Git Pull
- ذخیره تغییرات local (git stash)
- دریافت آخرین نسخه
- بازگردانی تغییرات local

#### 4. به‌روزرسانی Dependencies
```bash
pip install --upgrade -r requirements.txt
```

#### 5. Migrations جدید
```bash
alembic upgrade head
```

#### 6. پاک‌سازی
- حذف __pycache__
- حذف *.pyc

#### 7. ریستارت
- اجرا با systemd یا
- اجرا در background

---

## 🎯 مثال‌های استفاده

### نصب اولیه:

```bash
# کلون پروژه
git clone <repo-url> meowvpnbot
cd meowvpnbot

# نصب
bash install.sh

# پاسخ به سوالات:
# آیا ادامه دهید? y
# ویرایش .env الان? y (و اطلاعات را وارد کنید)
# ایجاد systemd service? y

# تمام! ربات آماده است
```

### به‌روزرسانی:

```bash
cd meowvpnbot

# به‌روزرسانی
bash update.sh

# پاسخ به سوالات:
# آیا ادامه دهید? y
# Git pull? y
# اجرای ربات? y

# تمام! ربات به‌روزرسانی شد
```

---

## 🔧 عیب‌یابی

### خطا: Python not found

**راه‌حل:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### خطا: Permission denied

**راه‌حل:**
```bash
# اضافه کردن مجوز اجرا
chmod +x install.sh update.sh
```

### خطا: alembic command not found

**راه‌حل:**
```bash
# فعال‌سازی venv
source venv/bin/activate

# نصب مجدد
pip install alembic
```

### خطا: Git conflicts

**راه‌حل:**
```bash
# مشاهده تغییرات
git status

# حل تعارض‌ها یا
# رد کردن تغییرات local
git reset --hard origin/main
```

---

## ⚙️ تنظیمات پیشرفته

### تغییر زمان reset کارت‌ها:

در `main.py`:
```python
job_queue.run_daily(
    reset_card_daily_amounts, 
    time=time(hour=0, minute=1),  # تغییر این خط
    name='daily_card_reset'
)
```

### تغییر زمان بررسی نوتیفیکیشن‌ها:

```python
job_queue.run_daily(
    check_services_for_notifications, 
    time=time(hour=9, minute=0),  # تغییر این خط
    name='daily_notification_check'
)
```

### استفاده از PostgreSQL:

```bash
# نصب psycopg2
pip install psycopg2-binary

# تغییر .env
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## 🔐 امنیت

### توصیه‌های مهم:

#### 1. محافظت از .env:
```bash
chmod 600 .env
```

#### 2. اجرا با کاربر غیر root:
```bash
# ایجاد کاربر اختصاصی
sudo useradd -m -s /bin/bash meowvpn

# تغییر مالکیت
sudo chown -R meowvpn:meowvpn /path/to/meowvpnbot

# اجرا
sudo -u meowvpn bash install.sh
```

#### 3. فایروال:
```bash
# فقط پورت‌های ضروری
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 📊 پس از نصب

### چک‌لیست:

- [ ] ربات اجرا شده و بدون خطاست
- [ ] `/start` در تلگرام پاسخ می‌دهد
- [ ] `/admin` کار می‌کند
- [ ] پنل Marzban اضافه شده
- [ ] پلن‌ها ایجاد شده
- [ ] کارت‌های بانکی اضافه شده
- [ ] یک خرید تست انجام شده
- [ ] Systemd service فعال است (اختیاری)
- [ ] Backup خودکار تنظیم شده

### تست عملکرد:

```bash
# بررسی وضعیت (با systemd)
sudo systemctl status meowvpnbot

# مشاهده لاگ‌ها
sudo journalctl -u meowvpnbot -f

# یا بدون systemd
tail -f bot.log
```

---

## 🔄 به‌روزرسانی منظم

### توصیه:

```bash
# هر هفته یکبار
cd /path/to/meowvpnbot
bash update.sh
```

### Automation:

افزودن به crontab برای به‌روزرسانی خودکار:

```bash
# ویرایش crontab
crontab -e

# اضافه کردن (به‌روزرسانی هفتگی شنبه‌ها ساعت 4 صبح)
0 4 * * 6 cd /path/to/meowvpnbot && bash update.sh
```

---

## 🆘 پشتیبانی

### لاگ‌ها:

```bash
# Systemd
sudo journalctl -u meowvpnbot -n 100

# Manual
tail -f bot.log

# خطاهای Python
python main.py  # اجرا در foreground برای دیباگ
```

### Rollback:

اگر به‌روزرسانی مشکل داشت:

```bash
# 1. توقف ربات
sudo systemctl stop meowvpnbot

# 2. بازگشت به نسخه قبل (Git)
git log --oneline -5  # مشاهده آخرین commit ها
git checkout <commit-hash>

# 3. بازگشت migration
alembic downgrade -1

# 4. ریستارت
sudo systemctl start meowvpnbot
```

---

## 💡 نکات مهم

### ✅ انجام دهید:

1. **قبل از هر به‌روزرسانی:**
   - پشتیبان‌گیری (updater خودکار انجام می‌دهد)
   - مطالعه CHANGELOG.md

2. **بعد از به‌روزرسانی:**
   - تست عملکرد اصلی
   - بررسی لاگ‌ها
   - یک خرید تست

3. **منظم:**
   - پشتیبان‌گیری هفتگی
   - بررسی لاگ‌ها
   - به‌روزرسانی ماهانه

### ⚠️ اجتناب کنید:

1. **نصب بدون virtual environment**
   - ممکن است با packages سیستمی تداخل کند

2. **به‌روزرسانی بدون پشتیبان**
   - همیشه backup بگیرید

3. **نادیده گرفتن خطاها**
   - هر خطایی را بررسی کنید

---

## 🎊 مزایای استفاده از اسکریپت‌ها

### Installer:
- ⚡ سرعت بالا (5 دقیقه)
- 🤖 خودکار 100%
- 🛡️ بدون خطا
- 📦 همه‌چیز آماده
- 🎯 آماده Production

### Updater:
- 🔄 به‌روزرسانی سریع (2 دقیقه)
- 💾 پشتیبان خودکار
- 🔐 امن و مطمئن
- 🧹 پاک‌سازی خودکار
- 🚀 ریستارت هوشمند

---

## 📚 مستندات مرتبط

- [QUICK_START.md](QUICK_START.md) - شروع سریع
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - راهنمای کامل
- [README.md](README.md) - نمای کلی

---

<div align="center">

**با این اسکریپت‌ها، نصب و به‌روزرسانی به سادگی آب خوردن است! 🎉**

نسخه: 2.5.0+ | تاریخ: 2025-10-16

</div>

