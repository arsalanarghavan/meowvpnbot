#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  رفع مشکلات Laravel${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# پیدا کردن مسیر site
if [ -d "site" ]; then
    SITE_DIR="site"
elif [ -d "../site" ]; then
    SITE_DIR="../site"
else
    echo -e "${RED}✗ پوشه site یافت نشد!${NC}"
    exit 1
fi

cd "$SITE_DIR"
echo -e "${YELLOW}▶ در حال کار روی: $(pwd)${NC}"
echo ""

# 1. پاکسازی کش‌ها
echo -e "${YELLOW}▶ پاکسازی کش‌ها...${NC}"
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear
echo -e "${GREEN}✓ کش‌ها پاک شدند${NC}"
echo ""

# 2. تنظیم مجوزها
echo -e "${YELLOW}▶ تنظیم مجوزها...${NC}"
mkdir -p storage/framework/{sessions,views,cache}
mkdir -p storage/logs
mkdir -p bootstrap/cache

chmod -R 775 storage bootstrap/cache

# تنظیم ownership
if id -u www-data &> /dev/null; then
    echo "  تنظیم owner: www-data"
    sudo chown -R www-data:www-data storage bootstrap/cache
elif id -u nginx &> /dev/null; then
    echo "  تنظیم owner: nginx"
    sudo chown -R nginx:nginx storage bootstrap/cache
fi

echo -e "${GREEN}✓ مجوزها تنظیم شدند${NC}"
echo ""

# 3. Cache مجدد
echo -e "${YELLOW}▶ ساخت cache جدید...${NC}"
php artisan config:cache
php artisan route:cache
echo -e "${GREEN}✓ Cache ساخته شد${NC}"
echo ""

# 4. لیست route ها
echo -e "${YELLOW}▶ لیست route های setup:${NC}"
php artisan route:list --name=setup | head -15
echo ""

# 5. چک .env
echo -e "${YELLOW}▶ چک .env:${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env موجود است${NC}"
    echo "  APP_URL: $(grep APP_URL .env | cut -d '=' -f 2)"
    echo "  SETUP_WIZARD_ENABLED: $(grep SETUP_WIZARD_ENABLED .env | cut -d '=' -f 2)"
    echo "  BOT_INSTALLED: $(grep BOT_INSTALLED .env | cut -d '=' -f 2)"
else
    echo -e "${RED}✗ .env یافت نشد!${NC}"
fi
echo ""

# 6. چک controller
echo -e "${YELLOW}▶ چک SetupWizardController:${NC}"
if [ -f "app/Http/Controllers/SetupWizardController.php" ]; then
    echo -e "${GREEN}✓ SetupWizardController موجود است${NC}"
else
    echo -e "${RED}✗ SetupWizardController یافت نشد!${NC}"
fi
echo ""

# 7. چک views
echo -e "${YELLOW}▶ چک views:${NC}"
if [ -d "resources/views/setup" ]; then
    echo -e "${GREEN}✓ پوشه setup موجود است${NC}"
    echo "  فایل‌ها:"
    ls -1 resources/views/setup/
else
    echo -e "${RED}✗ پوشه setup یافت نشد!${NC}"
fi
echo ""

# 8. تست وب سرور
echo -e "${YELLOW}▶ تست دسترسی:${NC}"
if [ -f "public/index.php" ]; then
    echo -e "${GREEN}✓ public/index.php موجود است${NC}"
    ls -lh public/index.php
else
    echo -e "${RED}✗ public/index.php یافت نشد!${NC}"
fi
echo ""

# 9. لاگ‌های خطا
echo -e "${YELLOW}▶ آخرین خطاهای Laravel:${NC}"
if [ -f "storage/logs/laravel.log" ]; then
    tail -20 storage/logs/laravel.log
else
    echo "  هیچ خطایی ثبت نشده"
fi
echo ""

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ انجام شد!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}حالا setup رو امتحان کن:${NC}"
echo -e "  ${GREEN}https://dashboard.meowbile.ir/setup${NC}"

