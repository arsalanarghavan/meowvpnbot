# 🔄 دستورات حذف و نصب مجدد

## روش 1: حذف کامل و نصب مجدد (پیشنهادی)

```bash
# 1. برو به مسیر پروژه
cd /var/www/meowvpnbot

# 2. بکاپ از دیتابیس (اختیاری)
cp vpn_bot.db ~/backup_$(date +%Y%m%d_%H%M%S).db 2>/dev/null || true
cp .env ~/bot_env_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true
cp site/.env ~/site_env_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# 3. متوقف کردن سرویس‌ها
sudo systemctl stop meowvpn-bot
sudo systemctl disable meowvpn-bot
sudo rm -f /etc/systemd/system/meowvpn-bot.service
sudo systemctl daemon-reload

# 4. حذف Nginx configs
sudo rm -f /etc/nginx/sites-enabled/*meow* /etc/nginx/sites-enabled/*dashboard*
sudo rm -f /etc/nginx/sites-available/*meow* /etc/nginx/sites-available/*dashboard*
sudo nginx -t && sudo systemctl reload nginx

# 5. حذف فایل‌های پروژه
cd /var/www
sudo rm -rf meowvpnbot

# 6. Clone مجدد از GitHub
git clone https://github.com/arsalanarghavan/meowvpnbot.git
sudo chown -R $USER:$USER meowvpnbot
cd meowvpnbot

# 7. نصب
sudo ./install.sh
```

---

## روش 2: استفاده از install.sh (سریع‌تر)

```bash
# 1. برو به مسیر پروژه
cd /var/www/meowvpnbot

# 2. دریافت آخرین تغییرات
git pull origin main

# 3. اجرای install.sh و انتخاب گزینه 2 (نصب مجدد)
sudo ./install.sh
# وقتی پرسید: 2 (نصب مجدد)
# وقتی پرسید: yes
```

---

## روش 3: فقط دریافت تغییرات (بدون حذف)

```bash
# 1. برو به مسیر پروژه
cd /var/www/meowvpnbot

# 2. دریافت تغییرات
git pull origin main

# 3. به‌روزرسانی
sudo ./update.sh
```

---

## دستورات یک خطی

### حذف کامل و نصب مجدد:
```bash
cd /var/www && sudo rm -rf meowvpnbot && git clone https://github.com/arsalanarghavan/meowvpnbot.git && cd meowvpnbot && sudo chown -R $USER:$USER . && sudo ./install.sh
```

### فقط دریافت و به‌روزرسانی:
```bash
cd /var/www/meowvpnbot && git pull origin main && sudo ./update.sh
```

---

## نکات مهم

- ✅ قبل از حذف، بکاپ بگیرید
- ✅ اگر در `/root/meowvpnbot` هستید، به `/var/www/meowvpnbot` منتقل می‌شود
- ✅ بعد از نصب، Setup Wizard خودکار باز می‌شود
- ✅ DNS باید به IP سرور اشاره کند

