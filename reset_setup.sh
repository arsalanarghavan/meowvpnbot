#!/bin/bash

# ==========================================
# Reset Setup - ریست کردن Setup Wizard
# ==========================================

set -e

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# تشخیص مسیر پروژه
if [ -d "/var/www/meowvpnbot" ]; then
    PROJECT_DIR="/var/www/meowvpnbot"
elif [ -d "/root/meowvpnbot" ]; then
    PROJECT_DIR="/root/meowvpnbot"
else
    echo "پروژه یافت نشد!"
    exit 1
fi

SITE_ENV="$PROJECT_DIR/site/.env"

if [ ! -f "$SITE_ENV" ]; then
    echo "فایل .env یافت نشد: $SITE_ENV"
    exit 1
fi

print_info "مسیر پروژه: $PROJECT_DIR"
echo ""

# بکاپ از .env
BACKUP_FILE="$SITE_ENV.backup_$(date +%Y%m%d_%H%M%S)"
cp "$SITE_ENV" "$BACKUP_FILE"
print_success "بکاپ: $BACKUP_FILE"
echo ""

# Reset کردن تنظیمات
print_info "در حال ریست کردن Setup Wizard..."

# فعال کردن wizard
sed -i 's/SETUP_WIZARD_ENABLED=false/SETUP_WIZARD_ENABLED=true/g' "$SITE_ENV"
sed -i 's/SETUP_WIZARD_ENABLED=0/SETUP_WIZARD_ENABLED=true/g' "$SITE_ENV"

# غیرفعال کردن bot installed
sed -i 's/BOT_INSTALLED=true/BOT_INSTALLED=false/g' "$SITE_ENV"
sed -i 's/BOT_INSTALLED=1/BOT_INSTALLED=false/g' "$SITE_ENV"

# پاک کردن admin username/password (اختیاری)
read -p "آیا می‌خواهید username/password ادمین را هم پاک کنید؟ (y/n): " RESET_ADMIN

if [[ $RESET_ADMIN =~ ^[Yy]$ ]]; then
    sed -i 's/^ADMIN_USERNAME=.*/ADMIN_USERNAME=/g' "$SITE_ENV"
    sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=/g' "$SITE_ENV"
    print_success "Username/Password ادمین پاک شد"
fi

# اضافه کردن اگر وجود نداشت
if ! grep -q "SETUP_WIZARD_ENABLED" "$SITE_ENV"; then
    echo "" >> "$SITE_ENV"
    echo "SETUP_WIZARD_ENABLED=true" >> "$SITE_ENV"
fi

if ! grep -q "BOT_INSTALLED" "$SITE_ENV"; then
    echo "BOT_INSTALLED=false" >> "$SITE_ENV"
fi

if ! grep -q "FIRST_RUN" "$SITE_ENV"; then
    echo "FIRST_RUN=true" >> "$SITE_ENV"
fi

# پاک کردن cache Laravel
print_info "پاک کردن cache Laravel..."
cd "$PROJECT_DIR/site"
php artisan config:clear 2>/dev/null || true
php artisan cache:clear 2>/dev/null || true
php artisan route:clear 2>/dev/null || true
php artisan view:clear 2>/dev/null || true

print_success "Cache پاک شد"
echo ""

print_success "✅ Setup Wizard ریست شد!"
echo ""
print_info "حالا می‌توانید به /setup بروید و از اول شروع کنید."
echo ""

