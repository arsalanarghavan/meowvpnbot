# رفع خطای Route [/] not defined

## مشکل:
خطای `Route [/] not defined` به این دلیل بود که در view ها از `route('/')` استفاده شده بود، اما route برای `/` name نداشت.

## راه‌حل:
1. ✅ Route `/` را name کردیم به `home`
2. ✅ همه view ها را از `route('/')` به `route('home')` تغییر دادیم

## دستورات برای اعمال تغییرات در سرور:

```bash
cd /var/www/meowvpnbot/site

# پاک کردن کش Laravel
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear

# یا همه را با یک دستور:
php artisan optimize:clear
```

## بررسی:

بعد از پاک کردن کش، صفحه اصلی باید بدون خطا کار کند.

## اگر هنوز خطا دارید:

1. بررسی کنید که فایل‌های view به‌روزرسانی شده‌اند
2. بررسی کنید که route `home` وجود دارد:
   ```bash
   php artisan route:list | grep home
   ```

