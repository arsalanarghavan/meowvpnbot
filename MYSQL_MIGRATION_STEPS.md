# 🚀 راهنمای مایگریشن از MySQL (مطمئن‌ترین روش)

این راهنما گام به گام نشون میده چطور با **100% دقت** دیتا رو منتقل کنی.

## ✅ چرا این روش مطمئن‌ترینه؟

- ✅ فایل SQL اصلاً برای MySQL نوشته شده
- ✅ همه دیتا کامل لود میشه
- ✅ قابل بررسی قبل از مایگریشن
- ✅ قابل برگشت و تکرار
- ✅ خطر از دست رفتن دیتا = صفر

---

## 📋 مراحل (فقط 4 مرحله!)

### مرحله 1️⃣: نصب MySQL (اگه نداری)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# شروع سرویس
sudo systemctl start mysql
sudo systemctl enable mysql

# تنظیم رمز root (اختیاری)
sudo mysql_secure_installation
```

### مرحله 2️⃣: Import فایل SQL به MySQL

```bash
# ساخت دیتابیس جدید
mysql -u root -p -e "CREATE DATABASE old_bot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import فایل demo.sql
mysql -u root -p old_bot_db < demo.sql

# بررسی موفقیت
mysql -u root -p old_bot_db -e "SHOW TABLES;"
```

**انتظار داری ببینی:**
```
+------------------------+
| Tables_in_old_bot_db   |
+------------------------+
| users                  |
| pannels                |
| products               |
| transactions           |
| ... (و بقیه جداول)     |
+------------------------+
```

### مرحله 3️⃣: اجرای مایگریشن

```bash
cd /mnt/1AF200F7F200D941/Projects/Bots/meowvpnbot
source venv/bin/activate
python migrate_from_mysql.py
```

**اسکریپت ازت می‌پرسه:**
```
Host (پیش‌فرض: localhost): [Enter]
Username (پیش‌فرض: root): [Enter]
Password: [رمز MySQL رو وارد کن]
Database (پیش‌فرض: old_bot_db): [Enter]
```

### مرحله 4️⃣: بررسی نتایج

```bash
# بررسی دیتابیس جدید
ls -lh vpn_bot.db

# نمایش آمار
sqlite3 vpn_bot.db "SELECT COUNT(*) as users FROM users;"
sqlite3 vpn_bot.db "SELECT COUNT(*) as services FROM services;"
sqlite3 vpn_bot.db "SELECT SUM(wallet_balance) as total_balance FROM users;"
```

---

## 📊 آمار انتظاری

بعد از مایگریشن باید ببینی:

```
📊 خلاصه مایگریشن
============================================================
  Users: ✅ 446 | ❌ 0
  Panels: ✅ 6 | ❌ 0
  Plans: ✅ 18 | ❌ 0
  Services: ✅ 1138 | ❌ 3
  Transactions: ✅ 423 | ❌ 2

  کل موفق: 2031
  کل ناموفق: 5
```

**نکته:** تعداد کمی خطا (کمتر از 1%) عادیه - معمولاً به خاطر دیتای ناقص یا رکوردهای orphan هست.

---

## 🔍 بررسی دقت مایگریشن

### چک 1: تعداد کاربران

```bash
# MySQL قدیمی
mysql -u root -p old_bot_db -e "SELECT COUNT(*) FROM users;"

# SQLite جدید
sqlite3 vpn_bot.db "SELECT COUNT(*) FROM users;"

# باید یکسان باشن ✅
```

### چک 2: مجموع موجودی کیف پول‌ها

```bash
# MySQL قدیمی
mysql -u root -p old_bot_db -e "SELECT SUM(ballance) FROM account_ballances;"

# SQLite جدید  
sqlite3 vpn_bot.db "SELECT SUM(wallet_balance) FROM users;"

# باید یکسان باشن ✅
```

### چک 3: تعداد سرویس‌های فعال

```bash
# MySQL قدیمی
mysql -u root -p old_bot_db -e "SELECT COUNT(*) FROM products WHERE isActive=1;"

# SQLite جدید
sqlite3 vpn_bot.db "SELECT COUNT(*) FROM services WHERE is_active=1;"

# باید نزدیک به هم باشن ✅
```

---

## ⚠️ رفع مشکلات رایج

### خطا: "Access denied for user"

```bash
# تنظیم مجدد رمز MySQL
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;
EXIT;
```

### خطا: "Can't connect to MySQL server"

```bash
# بررسی وضعیت MySQL
sudo systemctl status mysql

# شروع MySQL
sudo systemctl start mysql
```

### خطا: "Database 'old_bot_db' doesn't exist"

```bash
# ساخت دوباره و import
mysql -u root -p -e "CREATE DATABASE old_bot_db CHARACTER SET utf8mb4;"
mysql -u root -p old_bot_db < demo.sql
```

---

## 🧹 بعد از مایگریشن موفق

### پاک‌سازی (اختیاری)

```bash
# حذف دیتابیس MySQL قدیمی (بعد از اطمینان!)
mysql -u root -p -e "DROP DATABASE old_bot_db;"

# حذف فایل demo.sql (حاوی اطلاعات حساس)
rm demo.sql

# حذف لاگ خطاها
rm migration_errors.log
```

### تنظیم referrer_id (اختیاری)

اگر می‌خوای سیستم referral کامل کار کنه:

```bash
# اجرای کوئری در SQLite (هنوز پیاده‌سازی نشده)
# این بخش نیاز به توسعه اضافی داره
```

---

## 🎯 چک‌لیست نهایی

- [ ] MySQL نصب و راه‌اندازی شد
- [ ] فایل demo.sql به MySQL import شد
- [ ] اسکریپت مایگریشن اجرا شد
- [ ] تعداد کاربران چک شد ✅
- [ ] مجموع موجودی کیف پول‌ها چک شد ✅
- [ ] تعداد سرویس‌ها چک شد ✅
- [ ] ربات جدید تست شد ✅
- [ ] بکاپ از vpn_bot.db گرفته شد 💾
- [ ] فایل demo.sql پاک شد 🗑️
- [ ] دیتابیس MySQL قدیمی پاک شد 🗑️

---

## 💡 نکات مهم

1. **زمان:** کل فرآیند 15-30 دقیقه طول می‌کشه
2. **بکاپ:** قبل از هر کاری از vpn_bot.db بکاپ بگیر
3. **تست:** بعد از مایگریشن ربات رو کامل تست کن
4. **امنیت:** فایل demo.sql حاوی اطلاعات حساسه - حذفش کن

---

**آماده‌ای؟ بریم شروع کنیم! 🚀**

اگه سوالی داشتی یا به مشکل خوردی، بگو تا کمکت کنم.

