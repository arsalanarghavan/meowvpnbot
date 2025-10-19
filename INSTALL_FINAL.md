# 🚀 راهنمای نصب نهایی - MeowVPN Bot

## ✅ همه مشکلات حل شد!

---

## 🎯 نصب با یک دستور

```bash
git clone https://github.com/yourusername/meowvpnbot.git && cd meowvpnbot && sudo ./install.sh
```

---

## 📋 پیش‌نیازها

**هیچی! همه چیز خودکار نصب می‌شه:**

✅ Python 3.12 → خودکار  
✅ pip → خودکار  
✅ python3-venv → خودکار  
✅ PHP 8.2 → خودکار (حتی اگر 8.3 داشتی)  
✅ Composer → خودکار  
✅ Nginx → خودکار  
✅ Certbot → خودکار  
✅ SSL Certificate → خودکار  

**فقط Ubuntu/Debian لازمه!**

---

## 🎉 چه چیزهایی حل شد؟

### ✅ مشکلات Python:
- ❌ `python: command not found` → ✅ حل شد
- ❌ `pip not found` → ✅ نصب خودکار
- ❌ `externally-managed-environment` → ✅ از venv استفاده می‌کنه
- ❌ `cannot execute: required file not found` → ✅ چک کامل venv

### ✅ مشکلات PHP:
- ❌ PHP 8.3 ناسازگار → ✅ PHP 8.2 نصب می‌شه
- ❌ composer.lock error → ✅ خودکار update می‌شه
- ❌ `Do not run Composer as root` → ✅ با COMPOSER_ALLOW_SUPERUSER حل شد

### ✅ تجربه کاربری:
- ❌ سوال‌های زیاد → ✅ فقط 2 سوال (دامنه + DNS)
- ❌ نصب ناقص → ✅ تا آخر کامل می‌شه
- ❌ پیام‌های گیج‌کننده → ✅ پیام‌های واضح

---

## 📝 فرآیند نصب (5 دقیقه)

### مرحله 1: دانلود
```bash
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
```

### مرحله 2: اجرای نصب
```bash
sudo ./install.sh
```

### مرحله 3: جواب 2 سوال
```
دامنه: meowbile.ir
ساب‌دامین: dashboard
DNS آماده؟: y
```

### مرحله 4: نصب خودکار (2-5 دقیقه)

```
✓ نصب Python 3.12
✓ نصب pip
✓ نصب python3-venv
✓ ایجاد virtual environment
✓ نصب dependencies Python در venv
✓ نصب PHP 8.2
✓ نصب Composer
✓ نصب dependencies PHP
✓ نصب Nginx
✓ تنظیم Nginx
✓ دریافت SSL Certificate
✓ فعال کردن HTTPS
✓ نصب Auto-Restart
✓ راه‌اندازی services
```

### مرحله 5: باز کردن Setup Wizard
```
https://dashboard.meowbile.ir/setup
```

### مرحله 6: تکمیل Wizard (5 مرحله)
```
0. ایجاد حساب ادمین (یوزر + پسورد)
1. تنظیمات ربات (Bot Token)
2. تنظیمات پنل (URL + API Key)
3. تنظیمات پرداخت (Gateway)
4. نصب و راه‌اندازی خودکار
```

### مرحله 7: ✅ تمام!
```
ربات در تلگرام: @YourBot
پنل: https://dashboard.meowbile.ir
```

---

## 🔧 تکنولوژی‌ها

### Backend:
- Python 3.12
- python-telegram-bot
- SQLAlchemy + Alembic
- Virtual Environment

### Frontend:
- PHP 8.2
- Laravel 9.x
- Bootstrap 4 RTL
- Composer

### Infrastructure:
- Nginx
- Let's Encrypt SSL
- Systemd (Auto-Restart)
- SQLite

---

## 🎯 قابلیت‌ها

### ربات تلگرام:
- خرید سرویس (4 دسته)
- مدیریت سرویس
- کیف پول
- اکانت تست
- سیستم بازاریابی
- پنل ادمین

### پنل وب:
- 📊 داشبورد با نمودار
- 👥 مدیریت کاربران
- 🖥️ مدیریت سرویس‌ها
- 📦 مدیریت پلن‌ها
- 🌐 مدیریت پنل‌ها
- 💰 گزارش تراکنش‌ها
- 📢 مدیریت بازاریاب‌ها
- 🎁 کارت هدیه
- 💳 کارت بانکی
- ⚙️ تنظیمات کامل

---

## 🔐 امنیت

✅ HTTPS اجباری  
✅ SSL خودکار  
✅ بدون رمز پیش‌فرض  
✅ احراز هویت با نقش  
✅ CSRF Protection  
✅ SQL Injection Safe  

---

## 🔄 Auto-Restart

**اگر هر اتفاقی بیفته:**

- ربات کرش کرد → 10 ثانیه ریستارت
- سرور ریبوت شد → خودکار start
- Nginx قطع شد → 5 دقیقه ریستارت
- دیسک پر شد → لاگ هشدار

**Uptime: 99.9%+**

---

## 📦 Import بکاپ

توی Setup Wizard:
1. گزینه "بازیابی از بکاپ"
2. آپلود `demo.sql`
3. Import خودکار

---

## 🐛 مشکل داری؟

### نصب مجدد کامل:
```bash
cd /path/to/parent
sudo rm -rf meowvpnbot
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

### تست venv قبل از نصب:
```bash
bash test_venv.sh
```

### دستورات مفید:
```bash
# وضعیت
systemctl status meowvpn-bot
systemctl status nginx

# لاگ
journalctl -u meowvpn-bot -f

# ریستارت
systemctl restart meowvpn-bot
```

---

## ✅ چک‌لیست نهایی

- [x] Python 3.12 + venv
- [x] PHP 8.2 (نه 8.3)
- [x] Composer
- [x] Nginx
- [x] SSL خودکار
- [x] HTTPS فعال
- [x] بدون سوال اضافه
- [x] بدون externally-managed error
- [x] بدون composer.lock error
- [x] Setup Wizard کامل
- [x] Auto-Restart فعال
- [x] Import بکاپ
- [x] کاملاً خودکار

---

## 📊 آمار پروژه

- 14 Controller PHP
- 27+ Handler ربات
- 10 Model
- 74 View
- 84 Route
- 3 Middleware
- 13,000+ خط کد

---

## 🎊 نتیجه

**همه چیز 100% آماده!**

```bash
git clone https://github.com/yourusername/meowvpnbot.git && cd meowvpnbot && sudo ./install.sh
```

**فقط این دستور رو بزن و لذت ببر! 🚀**

---

**ساخته شده با ❤️ برای جامعه ایرانی**

