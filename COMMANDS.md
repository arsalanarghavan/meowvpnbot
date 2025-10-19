# 📋 دستورات کامل

## 1️⃣ حذف کامل (روی سرور فعلی):

```bash
cd /var/www/meowvpnbot
sudo ./uninstall.sh
```

**یا حذف دستی:**
```bash
# توقف سرویس
sudo systemctl stop meowvpn-bot
sudo systemctl disable meowvpn-bot

# حذف service
sudo rm /etc/systemd/system/meowvpn-bot.service
sudo systemctl daemon-reload

# حذف Nginx config
sudo rm /etc/nginx/sites-enabled/dashboard.*
sudo rm /etc/nginx/sites-available/dashboard.*
sudo systemctl reload nginx

# حذف فایل‌ها
sudo rm -rf /var/www/meowvpnbot

# حذف از root (اگه هست)
sudo rm -rf /root/meowvpnbot
```

---

## 2️⃣ Push به GitHub (روی لوکال):

```bash
cd /mnt/1AF200F7F200D941/Projects/Bots/meowvpnbot

git add .
git commit -m "✨ Complete Setup: Auto-redirect to wizard, Uninstaller, Updated scripts"
git push origin main
```

**یا اگه repo جدیده:**
```bash
cd /mnt/1AF200F7F200D941/Projects/Bots/meowvpnbot

git init
git add .
git commit -m "🎉 Initial commit: Complete bot + website with setup wizard"
git branch -M main
git remote add origin https://github.com/yourusername/meowvpnbot.git
git push -u origin main
```

---

## 3️⃣ نصب از GitHub (روی سرور جدید):

```bash
# نصب با یک دستور
git clone https://github.com/yourusername/meowvpnbot.git && cd meowvpnbot && sudo ./install.sh
```

**یا جداگانه:**
```bash
# دانلود
git clone https://github.com/yourusername/meowvpnbot.git

# ورود
cd meowvpnbot

# نصب
sudo ./install.sh
```

**سوالات نصب (فقط 2 تا):**
```
دامنه: mysite.com
ساب‌دامین: dashboard
DNS آماده؟: y
```

**بعدش:**
- نصب خودکار (2-5 دقیقه)
- باز کردن: `https://dashboard.mysite.com/setup`
- تکمیل Setup Wizard
- تمام! ✅

---

## 4️⃣ به‌روزرسانی (روی سرور):

```bash
cd /var/www/meowvpnbot
sudo ./update.sh
```

---

## 5️⃣ دستورات کمکی:

```bash
# رفع مشکلات Laravel
cd /var/www/meowvpnbot
bash fix_laravel.sh

# پاک کردن cache و اعمال تغییرات
bash apply_changes.sh

# بررسی Nginx
bash check_nginx.sh

# دیباگ 404
bash debug_404.sh

# تست Python venv
bash test_venv.sh

# وضعیت سرویس‌ها
sudo systemctl status meowvpn-bot
sudo systemctl status nginx
sudo systemctl status php8.2-fpm

# لاگ‌ها
journalctl -u meowvpn-bot -f
tail -f /var/log/nginx/dashboard_error.log
```

---

## 6️⃣ حل مشکل git ownership:

```bash
sudo git config --global --add safe.directory /var/www/meowvpnbot
sudo chown -R $USER:$USER /var/www/meowvpnbot/.git
```

---

## 7️⃣ مدیریت:

```bash
# ریستارت
sudo systemctl restart meowvpn-bot
sudo systemctl restart nginx
sudo systemctl restart php8.2-fpm

# توقف
sudo systemctl stop meowvpn-bot

# start
sudo systemctl start meowvpn-bot

# چک وضعیت
sudo systemctl is-active meowvpn-bot
```

---

## 8️⃣ بکاپ دستی:

```bash
# دیتابیس
cp /var/www/meowvpnbot/bot.db ~/backup_$(date +%Y%m%d).db

# تنظیمات
cp /var/www/meowvpnbot/.env ~/backup_bot_env.txt
cp /var/www/meowvpnbot/site/.env ~/backup_site_env.txt
```

---

## 9️⃣ نصب مجدد (Clean Install):

```bash
# حذف کامل
cd /var/www/meowvpnbot
sudo ./uninstall.sh

# نصب مجدد
cd ~
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

---

## 🔟 Import بکاپ:

```bash
# در Setup Wizard:
# گزینه "بازیابی از بکاپ"
# آپلود فایل SQL

# یا دستی:
sqlite3 /var/www/meowvpnbot/bot.db < backup.sql
```

