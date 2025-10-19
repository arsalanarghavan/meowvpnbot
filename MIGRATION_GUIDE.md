# 📚 راهنمای مایگریشن دیتابیس

این راهنما برای انتقال دیتا از ربات قدیمی (فقط Hiddify) به ربات جدید (Hiddify + Marzban) است.

## ⚠️ هشدارهای مهم

1. **حتماً قبل از اجرا از دیتابیس جدید بکاپ بگیرید!**
2. این اسکریپت فقط INSERT می‌کند و دیتای قبلی را پاک نمی‌کند
3. ابتدا با تعداد کمی رکورد تست کنید
4. بعضی فیلدها در دیتابیس قدیمی وجود نداشته و پیش‌فرض می‌گیرند

## 📋 پیش‌نیازها

```bash
# نصب کتابخانه‌های مورد نیاز
pip install pymysql
```

## 🔧 مراحل مایگریشن

### مرحله 1: آماده‌سازی

```bash
# اطمینان از وجود فایل demo.sql در دایرکتوری ربات
ls -lh demo.sql

# بکاپ از دیتابیس جدید
# اگر SQLite:
cp bot_database.db bot_database.db.backup

# اگر MySQL/PostgreSQL:
# از دستورات مربوطه برای بکاپ استفاده کنید
```

### مرحله 2: اجرای مایگریشن

```bash
# اجرای اسکریپت مایگریشن
python migrate_old_database.py
```

### مرحله 3: بررسی نتایج

```bash
# بررسی فایل لاگ خطاها (اگر وجود داشته باشد)
cat migration_errors.log
```

## 📊 نگاشت (Mapping) جداول

### کاربران (Users)

| دیتابیس قدیمی | دیتابیس جدید | توضیحات |
|--------------|-------------|---------|
| `users.account_id` | `users.user_id` | شناسه کاربر |
| `users.role` (admin/agent/user) | `users.role` (admin/marketer/customer) | نقش کاربر - agent → marketer |
| `account_ballances.ballance` | `users.wallet_balance` | موجودی کیف پول |
| `referral_wallets.amount` | `users.commission_balance` | موجودی کمیسیون |
| `bot_users.*` | - | اطلاعات تلگرام (در جدول جداگانه نیست) |

### پنل‌ها (Panels)

| دیتابیس قدیمی | دیتابیس جدید | توضیحات |
|--------------|-------------|---------|
| `pannels.location` | `panels.name` | نام پنل |
| `pannels.type` (همیشه hiddify) | `panels.panel_type` | نوع پنل |
| `pannels.url_port` | `panels.api_base_url` | آدرس پنل |
| `pannels.username` | `panels.username` | نام کاربری |
| `pannels.password` | `panels.password` | رمز عبور |

### پلن‌ها (Plans)

| دیتابیس قدیمی | دیتابیس جدید | توضیحات |
|--------------|-------------|---------|
| `product_categories.category_name` | `plans.name` | نام پلن |
| `product_categories.expire_day` | `plans.duration_days` | مدت زمان |
| `product_categories.volume` | `plans.traffic_gb` | حجم ترافیک |
| `product_categories.price` | `plans.price` | قیمت |
| - | `plans.device_limit` | محدودیت دستگاه (پیش‌فرض: 1) |

### سرویس‌ها (Services)

| دیتابیس قدیمی | دیتابیس جدید | توضیحات |
|--------------|-------------|---------|
| `products.account_id` | `services.user_id` | شناسه کاربر |
| `products.product_categories_id` | `services.plan_id` | شناسه پلن |
| UUID از `subscription_link` | `services.username_in_panel` | نام کاربری در پنل |
| `products.remark` | `services.note` | یادداشت |
| `products.created_at` | `services.start_date` | تاریخ شروع |
| `created_at + expire_day` | `services.expire_date` | تاریخ انقضا (محاسبه می‌شود) |
| `products.isActive` | `services.is_active` | وضعیت فعال |

### تراکنش‌ها (Transactions)

| دیتابیس قدیمی | دیتابیس جدید | توضیحات |
|--------------|-------------|---------|
| `transactions.account_id` | `transactions.user_id` | شناسه کاربر |
| `transactions.amount` | `transactions.amount` | مبلغ |
| `transactions.confirmed` | `transactions.status` | confirmed==1 → COMPLETED |
| `transactions.recipe_number` | `transactions.tracking_code` | کد پیگیری |
| `transactions.payment_type_id` | `transactions.type` | نوع تراکنش |

## 🔍 موارد نیازمند بررسی دستی

### 1. Referrer_id
در دیتابیس قدیمی، اطلاعات referral در جدول `referral_logs` است، ولی در دیتابیس جدید باید `referrer_id` در جدول `users` تنظیم شود. این کار نیاز به یک کوئری اضافی دارد که در نسخه فعلی اسکریپت پیاده‌سازی نشده.

**راه حل:**
```sql
-- بعد از مایگریشن، این کوئری را اجرا کنید
UPDATE users
SET referrer_id = (
    SELECT referral_user_id 
    FROM referral_logs 
    WHERE referral_to_id = users.user_id 
    LIMIT 1
)
WHERE user_id IN (SELECT DISTINCT referral_to_id FROM referral_logs);
```

### 2. Plan_id در Transactions
در دیتابیس قدیمی، تراکنش‌ها `plan_id` ندارند. اگر نیاز دارید این اطلاعات را اضافه کنید، باید با استفاده از تاریخ تراکنش و خریدهای کاربر، پلن مربوطه را تشخیص دهید.

### 3. Commission Records
اگر می‌خواهید سوابق کمیسیون را هم منتقل کنید، باید جدول `referral_logs` را به `commissions` مپ کنید. این بخش در نسخه فعلی اسکریپت پیاده‌سازی نشده.

## 🐛 رفع مشکلات رایج

### خطا: "User not found"
- **علت**: کاربری در جدول users قدیمی وجود ندارد
- **راه حل**: بررسی کنید که آیا تمام کاربران موجود در `bot_users` در `users` هم هستند

### خطا: "Plan not found"
- **علت**: دسته‌بندی محصول غیرفعال است یا حذف شده
- **راه حل**: فقط `product_categories` با `is_active=1` مایگریت می‌شوند

### خطا: "Invalid UUID"
- **علت**: لینک subscription فرمت استاندارد UUID ندارد
- **راه حل**: اسکریپت به صورت خودکار یک username جایگزین می‌سازد

## 📈 آمار مایگریشن

در پایان مایگریشن، یک خلاصه نمایش داده می‌شود:

```
📊 خلاصه مایگریشن
==========================================================
  users: ✅ 445 | ❌ 2
  panels: ✅ 6 | ❌ 0
  plans: ✅ 18 | ❌ 0
  services: ✅ 1138 | ❌ 3
  transactions: ✅ 423 | ❌ 2

  کل موفق: 2030
  کل ناموفق: 7
```

## 🔒 نکات امنیتی

1. فایل `demo.sql` حاوی اطلاعات حساس است - بعد از مایگریشن آن را پاک کنید
2. فایل `migration_errors.log` ممکن است حاوی اطلاعات کاربران باشد
3. بکاپ‌های خود را در مکانی امن نگهداری کنید

## 📞 پشتیبانی

اگر با مشکلی مواجه شدید:
1. ابتدا فایل `migration_errors.log` را بررسی کنید
2. خطاهای رایج را در بخش "رفع مشکلات" چک کنید
3. از دستور زیر برای دریافت اطلاعات بیشتر استفاده کنید:

```bash
python migrate_old_database.py --verbose
```

## ✅ چک‌لیست بعد از مایگریشن

- [ ] تعداد کاربران با دیتابیس قدیمی مطابقت دارد
- [ ] موجودی کیف پول‌ها درست منتقل شده
- [ ] پنل‌ها قابل دسترسی هستند
- [ ] پلن‌ها با قیمت و مدت زمان درست ساخته شده‌اند
- [ ] سرویس‌های فعال درست کار می‌کنند
- [ ] تراکنش‌ها با وضعیت صحیح ثبت شده‌اند
- [ ] بکاپ دیتابیس قدیمی در جای امنی ذخیره شده
- [ ] فایل `demo.sql` پاک شده (بعد از اطمینان از موفقیت)
- [ ] Referrer_id ها به‌روزرسانی شده‌اند (کوئری SQL)

---

**نسخه:** 1.0.0  
**تاریخ آخرین به‌روزرسانی:** 2025-10-19  
**سازگار با:** MeowVPN Bot v2.0+

