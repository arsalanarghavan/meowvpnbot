#!/bin/bash
# Pull از GitHub و Reset Setup Wizard

cd /var/www/meowvpnbot 2>/dev/null || cd /root/meowvpnbot 2>/dev/null || { echo "❌ پروژه یافت نشد!"; exit 1; }

echo "📥 در حال دریافت تغییرات از GitHub..."
git pull origin main

echo ""
echo "🔄 در حال ریست کردن Setup Wizard..."

SITE_ENV="$(pwd)/site/.env"

if [ ! -f "$SITE_ENV" ]; then
    echo "❌ فایل .env یافت نشد: $SITE_ENV"
    exit 1
fi

# بکاپ
cp "$SITE_ENV" "$SITE_ENV.backup_$(date +%Y%m%d_%H%M%S)"

# Reset
sed -i 's/SETUP_WIZARD_ENABLED=false/SETUP_WIZARD_ENABLED=true/g' "$SITE_ENV"
sed -i 's/BOT_INSTALLED=true/BOT_INSTALLED=false/g' "$SITE_ENV"
sed -i 's/^ADMIN_USERNAME=.*/ADMIN_USERNAME=/g' "$SITE_ENV"
sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=/g' "$SITE_ENV"

# اضافه کردن اگر وجود نداشت
grep -q "SETUP_WIZARD_ENABLED" "$SITE_ENV" || echo "SETUP_WIZARD_ENABLED=true" >> "$SITE_ENV"
grep -q "BOT_INSTALLED" "$SITE_ENV" || echo "BOT_INSTALLED=false" >> "$SITE_ENV"

# پاک کردن cache
cd site
php artisan config:clear 2>/dev/null || true
php artisan cache:clear 2>/dev/null || true
php artisan route:clear 2>/dev/null || true
php artisan view:clear 2>/dev/null || true

echo ""
echo "✅ تمام! Setup Wizard ریست شد."
echo "🌐 حالا به /setup بروید"

