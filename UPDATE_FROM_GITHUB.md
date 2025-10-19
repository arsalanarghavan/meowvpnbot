# 🔄 به‌روزرسانی از GitHub

## 🚀 روش سریع (پیشنهادی):

### اگر تغییرات محلی نداری:

```bash
cd /root/meowvpnbot
git fetch origin
git reset --hard origin/main
```

**یا:**

```bash
cd /root/meowvpnbot
git pull origin main --force
```

---

## 🔄 روش کامل (نصب مجدد):

### 1. پشتیبان‌گیری از دیتابیس:
```bash
cp /root/meowvpnbot/bot.db /root/bot_backup.db
cp /root/meowvpnbot/.env /root/env_backup.txt
cp /root/meowvpnbot/site/.env /root/site_env_backup.txt
```

### 2. حذف پروژه قدیمی:
```bash
cd /root
rm -rf meowvpnbot
```

### 3. دانلود دوباره:
```bash
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
```

### 4. بازگرداندن تنظیمات:
```bash
cp /root/bot_backup.db bot.db
cp /root/env_backup.txt .env
cp /root/site_env_backup.txt site/.env
```

### 5. نصب مجدد:
```bash
sudo ./install.sh
```

---

## 🔧 روش به‌روزرسانی هوشمند:

### استفاده از اسکریپت update.sh:

```bash
cd /root/meowvpnbot
sudo ./update.sh
```

این اسکریپت:
- ✅ از دیتابیس پشتیبان می‌گیره
- ✅ آخرین تغییرات رو می‌گیره
- ✅ dependencies رو به‌روز می‌کنه
- ✅ سرویس‌ها رو ریستارت می‌کنه

---

## 📦 فقط فایل‌های خاص:

### اگر فقط یک فایل نیاز داری:

```bash
cd /root/meowvpnbot

# دانلود فقط install.sh
git checkout origin/main -- install.sh

# دانلود فقط fix_laravel.sh
git checkout origin/main -- fix_laravel.sh

# دانلود فقط یک controller
git checkout origin/main -- site/app/Http/Controllers/SetupWizardController.php
```

---

## 🆕 دانلود اولیه (از صفر):

```bash
cd /root
git clone https://github.com/yourusername/meowvpnbot.git
cd meowvpnbot
sudo ./install.sh
```

---

## ⚠️ اگر خطا داد:

### خطای "Your local changes would be overwritten":
```bash
cd /root/meowvpnbot

# دیدن تغییرات
git status

# حفظ تغییرات و بعد pull
git stash
git pull origin main
git stash pop

# یا نادیده گرفتن تغییرات
git reset --hard origin/main
git pull origin main
```

### خطای "Permission denied":
```bash
sudo chown -R $USER:$USER /root/meowvpnbot
```

---

## 🎯 بعد از به‌روزرسانی:

### 1. رفع مشکلات Laravel:
```bash
cd /root/meowvpnbot
bash fix_laravel.sh
```

### 2. ریستارت سرویس‌ها:
```bash
sudo systemctl restart meowvpn-bot
sudo systemctl restart nginx
sudo systemctl restart php8.2-fpm
```

### 3. چک وضعیت:
```bash
systemctl status meowvpn-bot
systemctl status nginx
```

---

## 📊 چک نسخه:

### دیدن آخرین commit:
```bash
cd /root/meowvpnbot
git log -1 --oneline
```

### دیدن تفاوت با GitHub:
```bash
git fetch origin
git diff origin/main
```

---

## 🔑 دستورات مفید:

```bash
# دیدن وضعیت فعلی
git status

# دیدن تغییرات
git diff

# دیدن لیست فایل‌های تغییر یافته
git diff --name-only origin/main

# برگشت به حالت قبل
git reset --hard HEAD

# دانلود آخرین تغییرات بدون merge
git fetch origin

# دیدن branch های موجود
git branch -a
```

---

## 🎉 توصیه:

**ساده‌ترین روش:**

```bash
cd /root/meowvpnbot
git pull origin main
bash fix_laravel.sh
sudo systemctl restart meowvpn-bot nginx
```

**اگر خطا داد:**

```bash
cd /root/meowvpnbot
git fetch origin
git reset --hard origin/main
bash fix_laravel.sh
sudo systemctl restart meowvpn-bot nginx
```

---

**همین! ✨**

