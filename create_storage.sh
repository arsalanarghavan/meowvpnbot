#!/bin/bash

# اسکریپت ایجاد پوشه‌های storage برای Laravel

PROJECT_ROOT="/var/www/meowvpnbot"
SITE_DIR="$PROJECT_ROOT/site"

echo "ایجاد پوشه‌های storage..."

# ایجاد پوشه‌های storage
mkdir -p "$SITE_DIR/storage/framework/sessions"
mkdir -p "$SITE_DIR/storage/framework/views"
mkdir -p "$SITE_DIR/storage/framework/cache"
mkdir -p "$SITE_DIR/storage/logs"
mkdir -p "$SITE_DIR/bootstrap/cache"

# تنظیم مجوزها
chmod -R 775 "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache"

# تنظیم مالکیت
if id "www-data" &>/dev/null; then
    chown -R www-data:www-data "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache"
    echo "✓ مجوزها برای www-data تنظیم شد"
elif id "nginx" &>/dev/null; then
    chown -R nginx:nginx "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache"
    echo "✓ مجوزها برای nginx تنظیم شد"
else
    echo "⚠ هشدار: کاربر www-data یا nginx یافت نشد. مجوزها تنظیم نشدند."
fi

# ایجاد فایل .gitkeep برای git
touch "$SITE_DIR/storage/framework/sessions/.gitkeep"
touch "$SITE_DIR/storage/framework/views/.gitkeep"
touch "$SITE_DIR/storage/framework/cache/.gitkeep"
touch "$SITE_DIR/storage/logs/.gitkeep"
touch "$SITE_DIR/bootstrap/cache/.gitkeep"

echo "✓ پوشه‌های storage ایجاد شدند"
echo ""
echo "مسیر لاگ: $SITE_DIR/storage/logs/laravel.log"

