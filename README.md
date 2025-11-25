# 🐱 MeowVPN Bot - سیستم کامل مدیریت VPN

ربات تلگرام + پنل مدیریت وب با Setup Wizard هوشمند

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PHP](https://img.shields.io/badge/PHP-8.2-purple.svg)](https://php.net)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Laravel](https://img.shields.io/badge/Laravel-9.x-red.svg)](https://laravel.com)

---

## 🚀 نصب با یک دستور

```bash
git clone https://github.com/yourusername/meowvpnbot.git && cd meowvpnbot && sudo ./install.sh
```

**همین! بقیه خودکار است!** ✨

---

## ✨ ویژگی‌های منحصر به فرد

### 🎯 نصب هوشمند:
- ✅ **تشخیص خودکار مسیر** - از `/root` به `/var/www` منتقل می‌شود
- ✅ **Setup Wizard گرافیکی** - بدون نیاز به Terminal
- ✅ **SSL خودکار** - Let's Encrypt
- ✅ **Subdomain بدون پورت** - تمیز و حرفه‌ای
- ✅ **Auto-Restart** - همیشه آنلاین

### 🔐 امنیت:
- ✅ **مجوزهای صحیح** - www-data ownership
- ✅ **HTTPS اجباری** - SSL خودکار
- ✅ **بدون رمز پیش‌فرض** - تنظیم در Wizard
- ✅ **احراز هویت با نقش** - Admin + Marketer

### 📦 قابلیت‌ها:
- ✅ **Import بکاپ** - انتقال از سیستم قدیمی
- ✅ **پنل مدیریت کامل** - 10 بخش مدیریتی
- ✅ **ربات تلگرام** - 27+ Handler
- ✅ **پشتیبانی از 4 نوع پلن** - عادی، ویژه، گیمینگ، ترید

---

## 📋 پیش‌نیازها

**هیچی! همه چیز خودکار نصب می‌شه:**

- ✅ Python 3.12 + venv
- ✅ pip
- ✅ PHP 8.2 (حتی اگر 8.3 داشتی)
- ✅ Composer
- ✅ Nginx
- ✅ Certbot (SSL)
- ✅ lsof, net-tools

**فقط یک سرور Ubuntu/Debian نیاز داری!**

---

## 🎯 فرآیند نصب (5 دقیقه)

### 1. دانلود:
```bash
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
```

### 2. نصب:
```bash
sudo ./install.sh
```

### 3. جواب 2 سوال:
```
دامنه: mysite.com
ساب‌دامین: dashboard
DNS آماده؟: y
```

### 4. نصب خودکار:

اسکریپت خودکار:
- تشخیص می‌ده که در `/root` هستی
- پروژه رو به `/var/www/meowvpnbot` منتقل می‌کنه
- مجوزها رو درست می‌کنه (www-data)
- همه dependencies رو نصب می‌کنه
- Nginx + SSL رو راه‌اندازی می‌کنه
- Auto-Restart رو فعال می‌کنه

### 5. باز کردن Setup Wizard:
```
https://dashboard.mysite.com/setup
```

### 6. تکمیل Wizard (5 مرحله):
- مرحله 0: ایجاد حساب ادمین
- مرحله 1: تنظیمات ربات تلگرام
- مرحله 2: تنظیمات پنل VPN
- مرحله 3: تنظیمات پرداخت
- مرحله 4: نصب و راه‌اندازی خودکار

### 7. ✅ تمام!

---

## 🌐 پنل مدیریت وب

### قابلیت‌ها:
- 📊 **داشبورد** - آمار real-time با نمودار
- 👥 **مدیریت کاربران** - CRUD کامل
- 🖥️ **مدیریت سرویس‌ها** - کنترل کامل
- 📦 **مدیریت پلن‌ها** - 4 دسته
- 🌐 **مدیریت پنل‌ها** - چند پنل همزمان
- 💰 **تراکنش‌ها** - گزارش مالی کامل
- 📢 **بازاریاب‌ها** - سیستم کمیسیون
- 🎁 **کارت‌های هدیه** - تولید و مدیریت
- 💳 **کارت‌های بانکی** - Multi-card support
- ⚙️ **تنظیمات** - کنترل کامل سیستم

---

## 🤖 ربات تلگرام

### برای مشتریان:
- خرید سرویس (4 دسته)
- مدیریت سرویس
- کیف پول
- اکانت تست رایگان
- FAQ تعاملی

### برای بازاریاب‌ها:
- لینک دعوت
- آمار کامل
- کمیسیون پلکانی
- تسویه حساب

### برای ادمین:
- پنل مدیریت کامل
- آمار و گزارش
- مدیریت کاربران
- تنظیمات

---

## 🔄 Auto-Restart و Monitoring

سیستم هوشمند **Systemd**:

- ✅ اگر ربات کرش کرد → 10 ثانیه بعد ریستارت
- ✅ اگر سرور ریبوت شد → خودکار start
- ✅ اگر Nginx قطع شد → حداکثر 5 دقیقه ریستارت
- ✅ Health Check → هر 5 دقیقه
- ✅ لاگ‌گذاری → تمام رویدادها

**Uptime: 99.9%+** 🚀

---

## 🔧 مدیریت

### دستورات مفید:

```bash
# وضعیت
systemctl status meowvpn-bot
systemctl status nginx

# ریستارت
systemctl restart meowvpn-bot
systemctl restart nginx

# لاگ
journalctl -u meowvpn-bot -f
tail -f /var/log/nginx/dashboard_error.log

# به‌روزرسانی
cd /var/www/meowvpnbot
git pull origin main
bash fix_laravel.sh
systemctl restart meowvpn-bot nginx
```

---

## 🐛 حل مشکلات

### خطای 404 File not found:
```bash
cd /var/www/meowvpnbot
bash fix_laravel.sh
```

### خطای Permission denied:
```bash
cd /var/www/meowvpnbot
sudo chown -R www-data:www-data .
sudo chmod -R 755 .
sudo chmod -R 775 site/storage site/bootstrap/cache
systemctl restart nginx php8.2-fpm
```

### پورت 80 اشغال است:
```bash
# چک کردن
sudo lsof -ti:80

# متوقف کردن Apache
sudo systemctl stop apache2
sudo systemctl disable apache2

# ریستارت Nginx
systemctl restart nginx
```

---

## 📦 Import بکاپ

در Setup Wizard:
1. گزینه "بازیابی از بکاپ"
2. آپلود فایل SQL
3. Import خودکار

یا دستی:
```bash
sqlite3 /var/www/meowvpnbot/bot.db < backup.sql
```

---

## 🔄 پاک کردن و نصب مجدد

### روش 1: فقط Reset Setup Wizard (سریع)

اگر فقط می‌خواهید Setup Wizard را دوباره فعال کنید:

```bash
cd /var/www/meowvpnbot  # یا /root/meowvpnbot
bash reset_setup.sh
```

این اسکریپت:
- ✅ Setup Wizard را فعال می‌کند
- ✅ BOT_INSTALLED را false می‌کند
- ✅ Cache Laravel را پاک می‌کند
- ✅ بکاپ از .env می‌گیرد

**بعد از اجرا:** به `/setup` بروید و از اول شروع کنید.

---

### روش 2: نصب مجدد کامل (پیشنهادی)

اگر می‌خواهید **همه چیز** را پاک کنید و از اول نصب کنید:

```bash
cd /var/www/meowvpnbot  # یا /root/meowvpnbot
bash fresh_install.sh
```

این اسکریپت:
- ✅ بکاپ از دیتابیس و .env می‌گیرد
- ✅ سرویس‌ها را متوقف می‌کند
- ✅ Systemd service را حذف می‌کند
- ✅ Nginx configs را حذف می‌کند
- ✅ فایل‌های پروژه را حذف می‌کند
- ✅ از GitHub دوباره clone می‌کند
- ✅ نصب کامل انجام می‌دهد

**بعد از اجرا:** Setup Wizard خودکار باز می‌شود.

---

### روش 3: حذف کامل (Uninstall)

اگر می‌خواهید **همه چیز** را حذف کنید (بدون نصب مجدد):

```bash
cd /var/www/meowvpnbot  # یا /root/meowvpnbot
bash uninstall.sh
```

این اسکریپت:
- ✅ بکاپ می‌گیرد (اختیاری)
- ✅ سرویس‌ها را متوقف می‌کند
- ✅ Systemd service را حذف می‌کند
- ✅ Nginx configs را حذف می‌کند
- ✅ SSL certificates را حذف می‌کند (اختیاری)
- ✅ فایل‌های پروژه را حذف می‌کند
- ✅ Log files را حذف می‌کند (اختیاری)

**بعد از اجرا:** همه چیز حذف شده است.

---

### مشکل: `/setup` به login redirect می‌شود

اگر `/setup` به جای باز کردن wizard، صفحه login را نشان می‌دهد:

```bash
# 1. Reset Setup Wizard
cd /var/www/meowvpnbot  # یا /root/meowvpnbot
bash reset_setup.sh

# 2. پاک کردن cache
cd site
php artisan config:clear
php artisan cache:clear
php artisan route:clear

# 3. بررسی .env
grep -E "SETUP_WIZARD_ENABLED|BOT_INSTALLED|ADMIN_USERNAME" site/.env
```

باید این مقادیر را ببینید:
```
SETUP_WIZARD_ENABLED=true
BOT_INSTALLED=false
ADMIN_USERNAME=  # خالی یا وجود نداشته باشد
```

اگر `ADMIN_USERNAME` مقدار دارد، آن را پاک کنید:
```bash
sed -i 's/^ADMIN_USERNAME=.*/ADMIN_USERNAME=/g' site/.env
```

---

## 🔄 به‌روزرسانی

### روش ساده:
```bash
cd /var/www/meowvpnbot
git pull origin main
bash fix_laravel.sh
systemctl restart meowvpn-bot nginx
```

### روش کامل:
```bash
cd /var/www/meowvpnbot
sudo ./update.sh
```

---

## 📊 آمار پروژه

- **14** Controller PHP
- **27+** Handler ربات
- **10** Model دیتابیس
- **74** صفحه View
- **84** Route
- **3** Middleware
- **13,000+** خط کد
- **100%** قابلیت‌های ربات در پنل

---

## 🎯 تکنولوژی‌ها

### Backend:
- Python 3.12 (ربات)
- python-telegram-bot
- SQLAlchemy + Alembic
- Virtual Environment

### Frontend:
- PHP 8.2 (پنل)
- Laravel 9.x
- Bootstrap 4 RTL
- Chart.js

### Infrastructure:
- Nginx
- Let's Encrypt SSL
- Systemd
- SQLite

---

## 📁 ساختار پروژه

```
meowvpnbot/
├── main.py                 # ورودی ربات
├── bot.db                  # دیتابیس SQLite
├── .env                    # تنظیمات ربات
├── requirements.txt        # Dependencies Python
├── install.sh              # نصب خودکار
├── update.sh               # به‌روزرسانی
├── fix_laravel.sh          # رفع مشکلات Laravel
├── move_to_var_www.sh      # انتقال به /var/www
├── check_nginx.sh          # بررسی Nginx
├── test_venv.sh            # تست venv
├── debug_404.sh            # دیباگ 404
├── site/                   # پنل Laravel
│   ├── app/
│   │   ├── Http/Controllers/
│   │   ├── Models/
│   │   └── ...
│   ├── resources/views/
│   ├── routes/web.php
│   └── ...
├── handlers/               # Handler های ربات
├── models/                 # Model های ربات
└── utils/                  # ابزارها
```

---

## 🤝 مشارکت

1. Fork کنید
2. Branch بسازید (`git checkout -b feature/AmazingFeature`)
3. Commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request باز کنید

---

## 📝 لایسنس

این پروژه تحت لایسنس MIT است - فایل [LICENSE](LICENSE) را ببینید.

---

## 📞 پشتیبانی

- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/meowvpnbot/issues)
- 📧 Email: support@example.com
- 💬 Telegram: @YourSupport

---

## ⭐ ستاره بدهید!

اگر این پروژه به شما کمک کرد، یک ⭐ بدهید!

---

<div align="center">

**ساخته شده با ❤️ برای جامعه ایرانی**

</div>
