# 🐱 MeowVPN Bot + Website - کامل‌ترین ربات VPN تلگرام

یک سیستم کامل و یکپارچه شامل ربات تلگرام و پنل مدیریت وب

---

## 🚀 نصب با یک دستور

```bash
git clone https://github.com/yourusername/meowvpnbot.git && cd meowvpnbot && sudo ./install.sh
```

**همین! بقیه خودکار است! ✨**

---

## ✨ ویژگی‌های منحصر به فرد

- ✅ **Setup Wizard گرافیکی** - نصب بدون terminal
- ✅ **نصب یک دستوری** - همه چیز خودکار
- ✅ **SSL خودکار** - Let's Encrypt
- ✅ **Subdomain** - بدون پورت
- ✅ **Auto-Restart** - همیشه در حال اجرا
- ✅ **Import بکاپ** - انتقال از سیستم قدیمی
- ✅ **بدون رمز پیش‌فرض** - امنیت 100%
- ✅ **پنل مدیریت کامل** - 10 بخش مدیریتی

---

## 📋 پیش‌نیازها

**هیچی! همه چیز خودکار نصب می‌شه:**

- Python 3.9+ → خودکار نصب
- pip → خودکار نصب
- PHP 8.0+ → خودکار نصب
- Composer → خودکار نصب
- Nginx → خودکار نصب
- Certbot → خودکار نصب
- Supervisor → خودکار نصب

**فقط یک سرور Ubuntu/Debian نیاز داری!**

---

## 🎯 فرآیند نصب (5 دقیقه)

### 1. دانلود

```bash
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
```

### 2. نصب

```bash
sudo ./install.sh
```

### 3. جواب سوالات (فقط 2 تا!)

```
دامنه: meowbile.ir
ساب‌دامین: dashboard
DNS تنظیم شده؟ y
```

### 4. نصب خودکار (2-5 دقیقه)

```
✓ نصب Python و pip
✓ ایجاد virtual environment
✓ نصب dependencies Python
✓ نصب PHP و Composer
✓ نصب dependencies PHP
✓ نصب Nginx
✓ دریافت SSL Certificate
✓ فعال کردن HTTPS
✓ نصب Auto-Restart
✓ راه‌اندازی سرویس‌ها
```

### 5. باز کردن Setup Wizard

```
https://dashboard.meowbile.ir/setup
```

### 6. تکمیل Wizard (4 مرحله)

```
مرحله 0: ایجاد حساب ادمین
مرحله 1: تنظیمات ربات تلگرام
مرحله 2: تنظیمات پنل VPN
مرحله 3: تنظیمات پرداخت
مرحله 4: نصب خودکار
```

### 7. تمام! ✅

```
ربات در تلگرام آماده!
پنل در https://dashboard.meowbile.ir
```

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

### قابلیت‌ها:

**برای مشتریان:**
- خرید سرویس (4 دسته: عادی، ویژه، گیمینگ، ترید)
- مدیریت سرویس (تمدید، تمدید خودکار، لغو)
- کیف پول و پرداخت
- اکانت تست رایگان
- FAQ تعاملی

**برای بازاریاب‌ها:**
- لینک دعوت
- آمار کامل
- کمیسیون پلکانی
- تسویه حساب

**برای ادمین:**
- پنل مدیریت کامل
- آمار و گزارش
- مدیریت کاربران
- تنظیمات

---

## 🔐 امنیت

- ✅ بدون رمز پیش‌فرض
- ✅ HTTPS اجباری
- ✅ SSL خودکار
- ✅ CSRF Protection
- ✅ SQL Injection Safe
- ✅ احراز هویت با نقش‌ها

---

## 🔄 سیستم Auto-Restart

### اگر اتفاقی بیفته:

- **ربات کرش کرد** → 10 ثانیه بعد ریستارت ✅
- **سرور ریبوت شد** → همه چیز خودکار start ✅
- **Nginx قطع شد** → حداکثر 5 دقیقه ریستارت ✅
- **دیسک پر شد** → هشدار در لاگ ✅

**Uptime: 99.9%** 🚀

---

## 📦 Import بکاپ قدیمی

اگر دیتای قدیمی دارید:

1. در Setup Wizard گزینه "بازیابی از بکاپ" را بزنید
2. فایل `demo.sql` را آپلود کنید
3. Import خودکار انجام می‌شود

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
tail -f /var/log/meowvpn-health.log

# به‌روزرسانی
cd meowvpnbot
sudo ./update.sh
```

---

## 🐛 حل مشکلات

مشکل داری؟ فایل `TROUBLESHOOTING.md` را ببین یا:

```bash
# حذف و نصب مجدد
cd /path/to/parent
sudo rm -rf meowvpnbot
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

---

## 📊 آمار

- 14 کنترلر PHP
- 27+ Handler ربات
- 10 Model دیتابیس
- 74 صفحه View
- 84 Route
- 13,000+ خط کد
- 100% قابلیت‌های ربات در پنل

---

## 🎯 تکنولوژی‌ها

**Backend:**
- Python 3.9+ (ربات)
- python-telegram-bot
- SQLAlchemy + Alembic

**Frontend:**
- PHP 8.0+ (پنل)
- Laravel 9.x
- Bootstrap 4 RTL

**Infrastructure:**
- Nginx
- Let's Encrypt SSL
- Systemd
- SQLite

---

## 📞 پشتیبانی

- GitHub: [Issues](https://github.com/yourusername/meowvpnbot/issues)
- Email: support@example.com
- Telegram: @YourSupport

---

## ⭐ ستاره بدهید!

اگر مفید بود یک ⭐ بدهید!

---

**ساخته شده با ❤️ برای جامعه ایرانی**

