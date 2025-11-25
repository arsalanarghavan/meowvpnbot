# 🐱 MeowVPN Bot

ربات تلگرام + پنل مدیریت وب با Setup Wizard

---

## 🚀 نصب

```bash
git clone https://github.com/arsalanarghavan/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

**همه چیز خودکار نصب می‌شه!**

---

## ✨ ویژگی‌ها

- ✅ Setup Wizard گرافیکی
- ✅ SSL خودکار (Let's Encrypt)
- ✅ Auto-Restart با Systemd
- ✅ پنل مدیریت کامل
- ✅ ربات تلگرام با 27+ Handler
- ✅ Import بکاپ قدیمی

---

## 📋 پیش‌نیازها

**هیچی! همه چیز خودکار نصب می‌شه:**
- Python 3.12 + venv
- PHP 8.2
- Composer
- Nginx
- Certbot

**فقط یک سرور Ubuntu/Debian نیاز داری!**

---

## 🎯 نصب (5 دقیقه)

1. Clone و نصب:
```bash
git clone https://github.com/arsalanarghavan/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

2. جواب سوالات:
```
دامنه: mysite.com
ساب‌دامین: dashboard
DNS آماده؟: y
```

3. باز کردن Setup Wizard:
```
https://dashboard.mysite.com/setup
```

4. تکمیل Wizard:
- ایجاد حساب ادمین
- تنظیمات ربات تلگرام
- تنظیمات پنل VPN
- تنظیمات پرداخت
- نصب خودکار

---

## 🔧 دستورات

### به‌روزرسانی:
```bash
cd /var/www/meowvpnbot
sudo ./update.sh
```

### حذف کامل:
```bash
cd /var/www/meowvpnbot
sudo ./uninstall.sh
```

### نصب مجدد:
```bash
cd /var/www/meowvpnbot
sudo ./install.sh
# گزینه 2: نصب مجدد
```

### وضعیت سرویس‌ها:
```bash
systemctl status meowvpn-bot
systemctl status nginx
```

### لاگ‌ها:
```bash
journalctl -u meowvpn-bot -f
```

---

## 🐛 حل مشکلات

### خطای Permission denied:
```bash
cd /var/www/meowvpnbot
sudo chown -R www-data:www-data site/storage site/bootstrap/cache
sudo chmod -R 775 site/storage site/bootstrap/cache
sudo systemctl restart nginx php8.2-fpm
```

### پورت 80 اشغال است:
```bash
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo systemctl restart nginx
```

### `/setup` به login redirect می‌شود:
```bash
cd /var/www/meowvpnbot/site
sed -i 's/^ADMIN_USERNAME=.*/ADMIN_USERNAME=/g' .env
sed -i 's/SETUP_WIZARD_ENABLED=false/SETUP_WIZARD_ENABLED=true/g' .env
sed -i 's/BOT_INSTALLED=true/BOT_INSTALLED=false/g' .env
php artisan config:clear
php artisan cache:clear
php artisan route:clear
```

---

## 📦 Import بکاپ

در Setup Wizard:
1. گزینه "بازیابی از بکاپ"
2. آپلود فایل SQL
3. Import خودکار

---

## 📁 ساختار پروژه

```
meowvpnbot/
├── main.py              # ورودی ربات
├── install.sh           # نصب
├── update.sh            # به‌روزرسانی
├── uninstall.sh         # حذف
├── backup_database.sh   # بکاپ
├── site/                # پنل Laravel
├── bot/                 # کد ربات
├── database/            # مدل‌های دیتابیس
└── services/            # API های پنل
```

---

## 📝 لایسنس

MIT License

---

<div align="center">

**ساخته شده با ❤️**

[⭐ Star on GitHub](https://github.com/arsalanarghavan/meowvpnbot)

</div>
