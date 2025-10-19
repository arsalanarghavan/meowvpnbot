# 📦 راهنمای Import بکاپ قدیمی

## 🎯 معرفی

اگر از ربات قدیمی یا سیستم دیگری دیتا دارید، می‌توانید آن را به راحتی Import کنید!

---

## 🚀 نحوه استفاده

### مرحله 1: نصب سیستم

```bash
sudo ./install.sh
```

وارد کردن اطلاعات:
- دامنه
- یوزرنیم
- پسورد

### مرحله 2: باز کردن Setup Wizard

```
https://dashboard.site.com/setup
```

### مرحله 3: انتخاب گزینه Backup

در صفحه خوش‌آمدگویی دو گزینه دارید:

```
🚀 نصب جدید (از ابتدا)
📦 بازیابی از بکاپ قدیمی  ← این رو بزن!
```

### مرحله 4: آپلود فایل demo.sql

1. کلیک "بازیابی از بکاپ"
2. فایل `demo.sql` را drag & drop کنید یا کلیک کنید
3. سیستم خودکار فایل را تحلیل می‌کند:

```
اطلاعات فایل:
✓ نام: demo.sql
✓ حجم: 1.2 MB
✓ نوع: MySQL
✓ تعداد جداول: 15
✓ تعداد رکوردها: 5,000+
```

### مرحله 5: انتخاب نوع Import

```
○ همه چیز (توصیه می‌شود)
○ فقط کاربران و موجودی‌ها
○ فقط تراکنش‌ها
○ فقط سرویس‌ها
```

### مرحله 6: شروع Import

کلیک **"شروع Import"**

```
[14:30:25] در حال پردازش...
[14:30:27] ✓ کاربران Import شد (250)
[14:30:30] ✓ تراکنش‌ها Import شد (1,500)
[14:30:35] ✓ سرویس‌ها Import شد (180)

✓ Import موفق!
```

### مرحله 7: ادامه Setup Wizard

بعد از Import موفق، به مرحله 1 منتقل می‌شوید:
- تنظیمات ربات
- تنظیمات پنل
- و غیره...

---

## 📊 فرمت‌های پشتیبانی شده

### 1. MySQL Dump
```sql
-- MySQL dump
CREATE TABLE `users` ...
INSERT INTO `users` VALUES ...
```

### 2. SQLite Dump
```sql
-- SQLite dump
CREATE TABLE users ...
INSERT INTO users VALUES ...
```

### 3. Generic SQL
```sql
INSERT INTO users (id, name) VALUES (1, 'John');
```

---

## 🔄 نگاشت جداول (MySQL → SQLite)

### کاربران
```
MySQL: account_ballances
  ├─ account_id       → user_id
  ├─ ballance         → wallet_balance
  ├─ created_at       → created_at
  └─ (auto)           → role = 'customer'

SQLite: users
```

### تراکنش‌ها
```
MySQL: transactions
  ├─ id               → id
  ├─ user_id          → user_id
  ├─ amount           → amount
  ├─ type             → type
  ├─ status           → status
  └─ created_at       → created_at

SQLite: transactions
```

### سرویس‌ها
```
MySQL: services
  ├─ id               → id
  ├─ user_id          → user_id
  ├─ username         → username_in_panel
  ├─ expire_date      → expire_date
  └─ is_active        → is_active

SQLite: services
```

---

## ⚙️ تنظیمات پیشرفته

### Import انتخابی

می‌توانید فقط بخشی از دیتا را Import کنید:

#### فقط کاربران
```
✓ کاربران و موجودی‌ها
✗ تراکنش‌ها
✗ سرویس‌ها
```

**مناسب برای:** شروع جدید با کاربران قدیمی

#### فقط تراکنش‌ها
```
✗ کاربران
✓ تراکنش‌ها
✗ سرویس‌ها
```

**مناسب برای:** Import تاریخچه مالی

#### همه چیز
```
✓ کاربران
✓ تراکنش‌ها
✓ سرویس‌ها
✓ پلن‌ها
```

**مناسب برای:** انتقال کامل سیستم

---

## 🛡️ امنیت و احتیاط

### قبل از Import:

1. **پشتیبان بگیرید:**
```bash
cp vpn_bot.db vpn_bot.db.backup
```

2. **فایل را بررسی کنید:**
   - حجم منطقی داشته باشد
   - از منبع معتبر باشد
   - بدون کد مخرب

3. **تست کنید:**
   - روی سرور تست اول Import کنید
   - نتیجه را بررسی کنید

### در حین Import:

- ✅ صبر کنید تا تمام شود
- ✅ صفحه را refresh نکنید
- ✅ مرورگر را نبندید

### بعد از Import:

1. **بررسی داده‌ها:**
   - تعداد کاربران
   - مبالغ کیف پول‌ها
   - تراکنش‌ها

2. **تست کنید:**
   - ورود به ربات
   - بررسی سرویس‌ها
   - تست پرداخت

---

## 🧪 تست Import

### چک کردن تعداد کاربران:

```bash
sqlite3 vpn_bot.db "SELECT COUNT(*) FROM users;"
```

### چک کردن مجموع موجودی:

```bash
sqlite3 vpn_bot.db "SELECT SUM(wallet_balance) FROM users;"
```

### لیست 10 کاربر اول:

```bash
sqlite3 vpn_bot.db "SELECT user_id, wallet_balance FROM users LIMIT 10;"
```

---

## 📁 مثال کامل

### فایل demo.sql شما شامل:

```
account_ballances:
  - 240+ کاربر
  - موجودی‌های مختلف
  - تاریخچه عضویت

transactions:
  - هزاران تراکنش
  - انواع مختلف
  - تاریخچه مالی
```

### بعد از Import:

```
دیتابیس SQLite:
✓ 240+ کاربر در جدول users
✓ هزاران تراکنش در جدول transactions
✓ تبدیل خودکار فرمت MySQL → SQLite
✓ حفظ روابط بین جداول
```

---

## 🔧 عیب‌یابی

### خطا: فایل خیلی بزرگ است

**راه حل:**
```bash
# تنظیم PHP upload limit
sudo nano /etc/php/8.1/fpm/php.ini
```

تغییر:
```ini
upload_max_filesize = 100M
post_max_size = 100M
```

```bash
sudo systemctl restart php8.1-fpm
```

### خطا: Timeout

**راه حل:**
```bash
# افزایش timeout
sudo nano /etc/php/8.1/fpm/php.ini
```

```ini
max_execution_time = 300
```

### خطا: Duplicate Entry

**راه حل:**
- گزینه "Replace" را انتخاب کنید
- یا فقط رکوردهای جدید Import شود

---

## 📝 نکات مهم

1. **فرمت فایل:**
   - SQL dump باشد (.sql)
   - UTF-8 encoding
   - حداکثر 50MB (قابل افزایش)

2. **زمان Import:**
   - فایل کوچک (<1MB): چند ثانیه
   - فایل متوسط (1-10MB): 1-2 دقیقه
   - فایل بزرگ (10-50MB): 5-10 دقیقه

3. **مصرف منابع:**
   - CPU: متوسط
   - RAM: بستگی به حجم فایل
   - Disk: اندازه فایل × 2

---

## ✅ چک‌لیست Import

قبل از Import:
- [ ] فایل بکاپ آماده است
- [ ] پشتیبان از دیتابیس فعلی گرفته شده
- [ ] اینترنت سرور پایدار است
- [ ] زمان کافی دارید

در حین Import:
- [ ] صفحه باز بماند
- [ ] منتظر بمانید
- [ ] پیشرفت را دنبال کنید

بعد از Import:
- [ ] تعداد رکوردها را چک کنید
- [ ] داده‌ها را بررسی کنید
- [ ] ادامه Setup Wizard را تکمیل کنید
- [ ] ربات را تست کنید

---

## 🎯 مزایا

✅ **آسان:** Drag & Drop  
✅ **سریع:** پردازش خودکار  
✅ **امن:** بررسی و validation  
✅ **هوشمند:** تشخیص خودکار فرمت  
✅ **منعطف:** Import انتخابی  
✅ **قابل اعتماد:** با خطا‌یابی  

---

**🎉 دیتاهای قدیمی خود را به راحتی منتقل کنید! 🎉**

