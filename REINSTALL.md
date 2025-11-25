# 🔄 حذف کامل و نصب مجدد

## دستورات کامل:

```bash
# 1. بکاپ از دیتابیس (اختیاری)
cd /var/www/meowvpnbot
cp vpn_bot.db ~/backup_$(date +%Y%m%d_%H%M%S).db 2>/dev/null || true
cp .env ~/bot_env_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true
cp site/.env ~/site_env_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# 2. متوقف کردن سرویس‌ها
sudo systemctl stop meowvpn-bot
sudo systemctl disable meowvpn-bot
sudo rm -f /etc/systemd/system/meowvpn-bot.service
sudo systemctl daemon-reload

# 3. حذف Nginx configs
sudo rm -f /etc/nginx/sites-enabled/*panel* /etc/nginx/sites-enabled/*dashboard* /etc/nginx/sites-enabled/*meow*
sudo rm -f /etc/nginx/sites-available/*panel* /etc/nginx/sites-available/*dashboard* /etc/nginx/sites-available/*meow*
sudo nginx -t && sudo systemctl reload nginx

# 4. حذف فایل‌های پروژه
cd /var/www
sudo rm -rf meowvpnbot

# 5. Clone مجدد از GitHub
git clone https://github.com/arsalanarghavan/meowvpnbot.git
sudo chown -R $USER:$USER meowvpnbot
cd meowvpnbot

# 6. نصب
sudo ./install.sh
```

---

## دستور یک خطی (سریع):

```bash
cd /var/www && sudo rm -rf meowvpnbot && git clone https://github.com/arsalanarghavan/meowvpnbot.git && cd meowvpnbot && sudo chown -R $USER:$USER . && sudo ./install.sh
```

---

## یا استفاده از install.sh (با بکاپ):

```bash
cd /var/www/meowvpnbot
git pull origin main
sudo ./install.sh
# گزینه 2: نصب مجدد
# yes
```

---

## نکات:

- ✅ قبل از حذف، بکاپ بگیرید
- ✅ بعد از نصب، Setup Wizard خودکار باز می‌شود
- ✅ DNS باید به IP سرور اشاره کند
