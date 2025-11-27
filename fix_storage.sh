#!/bin/bash

# اسکریپت ایجاد پوشه‌های storage برای Laravel
# این اسکریپت باید در سرور اجرا شود

PROJECT_ROOT="/var/www/meowvpnbot"
SITE_DIR="$PROJECT_ROOT/site"

echo "=========================================="
echo "ایجاد پوشه‌های storage برای Laravel"
echo "=========================================="
echo ""

# بررسی وجود مسیر پروژه
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ خطا: مسیر پروژه یافت نشد: $PROJECT_ROOT"
    exit 1
fi

if [ ! -d "$SITE_DIR" ]; then
    echo "❌ خطا: مسیر site یافت نشد: $SITE_DIR"
    exit 1
fi

echo "✓ مسیر پروژه: $PROJECT_ROOT"
echo "✓ مسیر site: $SITE_DIR"
echo ""

# ایجاد پوشه‌های storage
echo "در حال ایجاد پوشه‌ها..."
mkdir -p "$SITE_DIR/storage/framework/sessions"
mkdir -p "$SITE_DIR/storage/framework/views"
mkdir -p "$SITE_DIR/storage/framework/cache"
mkdir -p "$SITE_DIR/storage/logs"
mkdir -p "$SITE_DIR/bootstrap/cache"

if [ $? -eq 0 ]; then
    echo "✓ پوشه‌ها ایجاد شدند"
else
    echo "❌ خطا در ایجاد پوشه‌ها"
    exit 1
fi

# ایجاد فایل .gitkeep
echo ""
echo "در حال ایجاد فایل‌های .gitkeep..."
touch "$SITE_DIR/storage/framework/sessions/.gitkeep"
touch "$SITE_DIR/storage/framework/views/.gitkeep"
touch "$SITE_DIR/storage/framework/cache/.gitkeep"
touch "$SITE_DIR/storage/logs/.gitkeep"
touch "$SITE_DIR/bootstrap/cache/.gitkeep"

# ایجاد فایل laravel.log (اگر وجود ندارد)
if [ ! -f "$SITE_DIR/storage/logs/laravel.log" ]; then
    touch "$SITE_DIR/storage/logs/laravel.log"
    echo "✓ فایل laravel.log ایجاد شد"
fi

# تنظیم مجوزها
echo ""
echo "در حال تنظیم مجوزها..."
chmod -R 775 "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache"
if [ $? -eq 0 ]; then
    echo "✓ مجوزها تنظیم شدند (775)"
else
    echo "⚠ هشدار: تنظیم مجوزها با خطا مواجه شد"
fi

# تنظیم مالکیت
echo ""
echo "در حال تنظیم مالکیت..."

# بررسی وجود کاربر www-data
if id "www-data" &>/dev/null; then
    chown -R www-data:www-data "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ مالکیت برای www-data تنظیم شد"
    else
        echo "⚠ هشدار: تنظیم مالکیت با خطا مواجه شد (ممکن است نیاز به sudo باشد)"
        echo "   دستور: sudo chown -R www-data:www-data $SITE_DIR/storage $SITE_DIR/bootstrap/cache"
    fi
elif id "nginx" &>/dev/null; then
    chown -R nginx:nginx "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ مالکیت برای nginx تنظیم شد"
    else
        echo "⚠ هشدار: تنظیم مالکیت با خطا مواجه شد (ممکن است نیاز به sudo باشد)"
        echo "   دستور: sudo chown -R nginx:nginx $SITE_DIR/storage $SITE_DIR/bootstrap/cache"
    fi
else
    echo "⚠ هشدار: کاربر www-data یا nginx یافت نشد"
    echo "   لطفاً دستور زیر را با sudo اجرا کنید:"
    echo "   sudo chown -R www-data:www-data $SITE_DIR/storage $SITE_DIR/bootstrap/cache"
fi

# بررسی نهایی
echo ""
echo "=========================================="
echo "بررسی نهایی:"
echo "=========================================="

if [ -d "$SITE_DIR/storage/logs" ]; then
    echo "✓ پوشه logs وجود دارد"
    ls -la "$SITE_DIR/storage/logs/" | head -5
else
    echo "❌ پوشه logs وجود ندارد!"
fi

echo ""
if [ -f "$SITE_DIR/storage/logs/laravel.log" ]; then
    echo "✓ فایل laravel.log وجود دارد"
    echo "   مسیر: $SITE_DIR/storage/logs/laravel.log"
    echo "   اندازه: $(du -h "$SITE_DIR/storage/logs/laravel.log" | cut -f1)"
else
    echo "❌ فایل laravel.log وجود ندارد!"
fi

echo ""
echo "=========================================="
echo "✅ انجام شد!"
echo "=========================================="
echo ""
echo "برای مشاهده لاگ:"
echo "  tail -f $SITE_DIR/storage/logs/laravel.log"
echo ""

