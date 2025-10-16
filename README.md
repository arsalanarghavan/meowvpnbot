# 🐱 MeowVPN Bot

<div align="center">

![Version](https://img.shields.io/badge/version-2.5.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production--ready-success.svg)

**یکی از کامل‌ترین و پیشرفته‌ترین ربات‌های فروش VPN در تلگرام**

[قابلیت‌ها](#-قابلیت‌ها) •
[نصب](#-نصب-سریع) •
[مستندات](#-مستندات) •
[پشتیبانی](#-پشتیبانی)

</div>

---

## 🌟 ویژگی‌های برجسته

- 🌐 **پشتیبانی از چند پنل** - اتصال و مدیریت چند پنل Marzban به صورت همزمان
- 💰 **سیستم پرداخت چندگانه** - کیف پول، درگاه آنلاین، کارت به کارت
- 📈 **سیستم بازاریابی پیشرفته** - کمیسیون پلکانی و پنل تحلیلی
- 🔔 **نوتیفیکیشن هوشمند** - هشدار انقضا و حجم کم
- 📊 **داشبورد جامع** - آمار real-time برای ادمین
- ❓ **FAQ تعاملی** - 5 دسته راهنمای کامل فارسی
- 🎯 **UX عالی** - منوهای دسته‌بندی شده و ساده

## 🚀 نصب سریع

```bash
# 1. کلون پروژه
git clone <repo-url> meowvpnbot
cd meowvpnbot

# 2. نصب dependencies
pip install -r requirements.txt

# 3. تنظیم .env
cp .env.example .env
nano .env  # مقادیر را وارد کنید

# 4. اجرای migration
alembic upgrade head

# 5. اجرای ربات
python main.py
```

📖 **راهنمای کامل:** [QUICK_START.md](QUICK_START.md)

## 📋 قابلیت‌ها

### 👤 برای مشتریان
- خرید سرویس با 4 دسته‌بندی (عادی، ویژه، گیمینگ، ترید)
- مدیریت کامل سرویس (تمدید، تمدید خودکار، لغو)
- کیف پول با تاریخچه فیلتر شده
- اکانت تست رایگان
- FAQ جامع
- نوتیفیکیشن‌های هوشمند

### 📈 برای بازاریاب‌ها
- لینک دعوت اختصاصی
- آمار تفصیلی (دعوت‌ها، فروش، درآمد)
- کمیسیون پلکانی
- تسویه حساب آسان
- پنل تحلیلی

### 👑 برای ادمین
- داشبورد جامع با آمار real-time
- مدیریت کاربران (جستجو، ویرایش، مسدودسازی)
- مدیریت بازاریاب‌ها
- تایید خودکار رسیدها
- مدیریت پلن‌ها و پنل‌ها
- تنظیمات کامل ربات
- پیام همگانی
- پشتیبان‌گیری

📖 **لیست کامل:** [FEATURES.md](FEATURES.md)

## 🏗️ معماری

```
meowvpnbot/
├── bot/
│   ├── handlers/          # Handler های تلگرام
│   │   ├── customer/      # قابلیت‌های کاربران
│   │   ├── marketer/      # قابلیت‌های بازاریاب
│   │   └── admin/         # قابلیت‌های ادمین
│   ├── keyboards/         # کیبوردها
│   ├── middlewares/       # Middleware ها
│   ├── states/            # State های conversation
│   ├── jobs.py            # Job های خودکار
│   └── notifications.py   # سیستم نوتیفیکیشن
├── core/                  # Core modules
│   ├── config.py          # تنظیمات
│   ├── logger.py          # لاگینگ
│   └── translator.py      # سیستم ترجمه
├── database/              # دیتابیس
│   ├── models/            # مدل‌های SQLAlchemy
│   │   └── queries/       # Query functions
│   └── engine.py          # Database engine
├── services/              # سرویس‌های خارجی
│   ├── marzban_api.py     # Marzban API client
│   └── zarinpal.py        # درگاه پرداخت
├── locales/               # فایل‌های ترجمه
│   └── fa.json            # ترجمه فارسی
├── alembic/               # Migration ها
└── main.py                # Entry point
```

## 🎯 تکنولوژی‌ها

- **Framework:** python-telegram-bot 20.x
- **Database:** SQLAlchemy ORM (PostgreSQL/SQLite)
- **Migration:** Alembic
- **Async:** asyncio
- **Payment:** Zarinpal API
- **VPN Panel:** Marzban API

## 📊 آمار

- 100+ قابلیت فعال
- 2500+ خط کد
- 25+ فایل
- 35+ متن فارسی
- 15+ Query function
- 7 Job خودکار

## 📖 مستندات

- 📘 [راهنمای سریع](QUICK_START.md) - شروع در 5 دقیقه
- 📗 [راهنمای استقرار](DEPLOYMENT_GUIDE.md) - راهنمای کامل
- 📙 [لیست قابلیت‌ها](FEATURES.md) - تمام قابلیت‌ها
- 📕 [قابلیت‌های نوآورانه](INNOVATIVE_FEATURES.md) - ویژگی‌های منحصر به فرد
- 📔 [تاریخچه تغییرات](CHANGELOG.md) - تغییرات هر نسخه
- 📓 [خلاصه بهبودها](README_IMPROVEMENTS.md) - تغییرات اخیر

## 🔧 پیش‌نیازها

- Python 3.9 یا بالاتر
- PostgreSQL یا SQLite
- یک یا چند پنل Marzban فعال
- توکن ربات تلگرام

## ⚙️ نصب و راه‌اندازی

### نصب ساده:
```bash
pip install -r requirements.txt
cp .env.example .env
# فایل .env را ویرایش کنید
alembic upgrade head
python main.py
```

### نصب Production:
راهنمای کامل در [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 تست

```bash
# اجرای ربات در حالت توسعه
python main.py

# تست موارد اصلی:
# 1. /start
# 2. خرید سرویس
# 3. پنل ادمین (/admin)
# 4. تبدیل به بازاریاب
```

## 🤝 مشارکت

این پروژه open-source است و از مشارکت شما استقبال می‌کنیم!

### نحوه مشارکت:
1. Fork کنید
2. یک branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. یک Pull Request باز کنید

### راهنمای توسعه:
- کد تمیز و مستند بنویسید
- از Type hints استفاده کنید
- Error handling اضافه کنید
- تست کنید قبل از commit

## 📞 پشتیبانی

- 🐛 **گزارش باگ:** [Issues](https://github.com/your-repo/issues)
- 💬 **سوالات:** [Discussions](https://github.com/your-repo/discussions)
- 📧 **ایمیل:** support@example.com
- 💼 **تلگرام:** @YourSupportID

## 📜 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است - فایل [LICENSE](LICENSE) را برای جزئیات بیشتر ببینید.

## 🙏 تشکر

این پروژه با استفاده از ابزارها و کتابخانه‌های زیر ساخته شده:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Marzban](https://github.com/Gozargah/Marzban)
- [Zarinpal](https://www.zarinpal.com/)

## ⭐ ستاره بدهید!

اگر این پروژه برای شما مفید بود، لطفاً یک ⭐ بدهید!

---

<div align="center">

**ساخته شده با ❤️ برای جامعه ایرانی**

[⬆ بازگشت به بالا](#-meowvpn-bot)

</div>

