# 🔧 راهنمای حل مشکل سرور فعلی

## 📋 وضعیت فعلی:
- ✗ پروژه در `/root/meowvpnbot` است
- ✗ خطای `Permission denied` می‌گیره
- ✗ www-data نمی‌تونه به `/root` دسترسی داشته باشه

## ✅ راه‌حل:

---

## مرحله 1️⃣: به‌روزرسانی از GitHub

```bash
cd /root/meowvpnbot
git fetch origin
git reset --hard origin/main
```

**توضیح:** آخرین تغییرات (شامل `move_to_var_www.sh`) رو دانلود می‌کنه

---

## مرحله 2️⃣: اجرای اسکریپت انتقال

```bash
cd /root/meowvpnbot
bash move_to_var_www.sh
```

**این اسکریپت خودکار:**

```
✅ از دیتابیس بکاپ می‌گیره
✅ پروژه رو به /var/www/meowvpnbot منتقل می‌کنه
✅ مجوزها رو درست می‌کنه (www-data:www-data)
✅ Nginx config رو به‌روز می‌کنه
✅ Systemd service رو به‌روز می‌کنه
✅ Laravel cache رو پاک می‌کنه
✅ همه سرویس‌ها رو ریستارت می‌کنه
✅ تست می‌کنه که کار می‌کنه
```

---

## مرحله 3️⃣: رفع مشکلات Laravel

```bash
cd /var/www/meowvpnbot
bash fix_laravel.sh
```

**این اسکریپت:**
- پاکسازی cache های Laravel
- تنظیم مجوزها
- ساخت route cache جدید
- نمایش همه route ها
- چک کردن وضعیت

---

## مرحله 4️⃣: تست

```bash
# تست با curl
curl -I https://dashboard.meowbile.ir/setup

# چک سرویس‌ها
systemctl status nginx
systemctl status php8.2-fpm

# چک لاگ‌ها
tail -20 /var/log/nginx/dashboard_error.log
```

---

## مرحله 5️⃣: باز کردن سایت

```
https://dashboard.meowbile.ir/setup
```

**باید Setup Wizard رو ببینی!** ✨

---

## 🎯 خلاصه دستورات (کپی-پیست):

```bash
# 1. به‌روزرسانی
cd /root/meowvpnbot
git fetch origin
git reset --hard origin/main

# 2. انتقال به /var/www
bash move_to_var_www.sh

# 3. رفع مشکلات Laravel
cd /var/www/meowvpnbot
bash fix_laravel.sh

# 4. تست
curl -I https://dashboard.meowbile.ir/setup

# 5. باز کردن در مرورگر
# https://dashboard.meowbile.ir/setup
```

---

## ⚠️ اگر خطا داد:

### خطای git:
```bash
cd /root/meowvpnbot
git stash
git fetch origin
git reset --hard origin/main
```

### اگر move_to_var_www.sh نبود:
```bash
cd /root/meowvpnbot
git pull origin main --force
# بعد دوباره bash move_to_var_www.sh
```

### اگر هنوز 404 میده:
```bash
# چک Nginx config
cat /etc/nginx/sites-available/dashboard.meowbile.ir

# باید ببینی:
# root /var/www/meowvpnbot/site/public;

# اگر اشتباه بود:
sudo nano /etc/nginx/sites-available/dashboard.meowbile.ir
# تغییر root به: /var/www/meowvpnbot/site/public
sudo systemctl restart nginx
```

---

## 📊 چک کردن وضعیت نهایی:

```bash
# مسیر پروژه
ls -la /var/www/meowvpnbot

# مجوزها
ls -la /var/www/meowvpnbot/site/storage
ls -la /var/www/meowvpnbot/site/bootstrap/cache

# سرویس‌ها
systemctl status nginx
systemctl status php8.2-fpm
systemctl status meowvpn-bot

# لاگ‌ها
tail -20 /var/log/nginx/dashboard_error.log
tail -20 /var/www/meowvpnbot/site/storage/logs/laravel.log
```

---

## 🎉 بعد از موفقیت:

پروژه قدیمی در `/root` رو می‌تونی حذف کنی:

```bash
# حتماً مطمئن شو که همه چیز کار می‌کنه!
# بعد:
sudo rm -rf /root/meowvpnbot
```

یا نگهش دار به عنوان بکاپ! 💾

---

## 💡 نکات مهم:

1. **بکاپ خودکار:** اسکریپت از دیتابیس بکاپ می‌گیره در `/root/`
2. **بدون قطعی:** سرویس‌ها فقط چند ثانیه قطع می‌شن
3. **بازگشت آسان:** اگر مشکلی بود، می‌تونی برگردونی
4. **امن:** همه config ها رو backup می‌کنه

---

**🚀 همین الان شروع کن! فقط 2-3 دقیقه طول می‌کشه!**

