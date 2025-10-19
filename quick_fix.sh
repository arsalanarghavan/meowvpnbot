#!/bin/bash

# سریع‌ترین راه برای حل همه مشکلات

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  🔧 حل سریع همه مشکلات${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# تشخیص مسیر
if [ -d "/var/www/meowvpnbot" ]; then
    PROJECT_DIR="/var/www/meowvpnbot"
elif [ -d "/root/meowvpnbot" ]; then
    PROJECT_DIR="/root/meowvpnbot"
else
    echo -e "${RED}✗ پروژه یافت نشد!${NC}"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${YELLOW}▶ پروژه: $PROJECT_DIR${NC}"
echo ""

# 1. حل مشکل git ownership
echo -e "${YELLOW}▶ حل مشکل git...${NC}"
sudo git config --global --add safe.directory "$PROJECT_DIR"
echo -e "${GREEN}✓${NC}"

# 2. بکاپ
echo -e "${YELLOW}▶ بکاپ...${NC}"
if [ -f "bot.db" ]; then
    cp bot.db ~/bot_backup_$(date +%Y%m%d_%H%M%S).db
    echo -e "${GREEN}✓ bot.db${NC}"
fi
if [ -f ".env" ]; then
    cp .env ~/env_backup_$(date +%Y%m%d_%H%M%S).txt
    echo -e "${GREEN}✓ .env${NC}"
fi

# 3. git pull
echo -e "${YELLOW}▶ به‌روزرسانی کد...${NC}"
git pull origin main
echo -e "${GREEN}✓${NC}"

# 4. مجوزها
echo -e "${YELLOW}▶ تنظیم مجوزها...${NC}"
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"
sudo chmod -R 775 "$PROJECT_DIR/site/storage"
sudo chmod -R 775 "$PROJECT_DIR/site/bootstrap/cache"
echo -e "${GREEN}✓${NC}"

# 5. Python venv
echo -e "${YELLOW}▶ Python dependencies...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    deactivate
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}ℹ venv نیست${NC}"
fi

# 6. PHP dependencies
echo -e "${YELLOW}▶ PHP dependencies...${NC}"
cd site
export COMPOSER_ALLOW_SUPERUSER=1
composer install --optimize-autoloader --no-interaction --quiet 2>/dev/null || composer update --optimize-autoloader --no-interaction --quiet
cd ..
echo -e "${GREEN}✓${NC}"

# 7. Laravel cache
echo -e "${YELLOW}▶ پاک کردن cache...${NC}"
cd site
php artisan config:clear --quiet
php artisan cache:clear --quiet
php artisan view:clear --quiet
php artisan route:clear --quiet
rm -rf bootstrap/cache/*.php
rm -rf storage/framework/views/*.php
php artisan config:cache --quiet
php artisan route:cache --quiet
cd ..
echo -e "${GREEN}✓${NC}"

# 8. ریستارت سرویس‌ها
echo -e "${YELLOW}▶ ریستارت سرویس‌ها...${NC}"
sudo systemctl restart php8.2-fpm 2>/dev/null || sudo systemctl restart php-fpm 2>/dev/null
sudo systemctl restart nginx
sudo systemctl restart meowvpn-bot 2>/dev/null || echo -e "${YELLOW}ℹ ربات هنوز نصب نشده${NC}"
echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ تمام!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# نمایش لینک
if [ -f "site/.env" ]; then
    APP_URL=$(grep "APP_URL=" site/.env | cut -d '=' -f 2)
    echo -e "${YELLOW}🌐 لینک سایت:${NC}"
    echo -e "  ${GREEN}$APP_URL${NC}"
    echo ""
    
    if grep -q "SETUP_WIZARD_ENABLED=true" site/.env 2>/dev/null; then
        echo -e "${YELLOW}🔧 Setup Wizard:${NC}"
        echo -e "  ${GREEN}$APP_URL/setup${NC}"
        echo ""
    fi
fi

echo -e "${YELLOW}💡 اگه مشکلی بود:${NC}"
echo "  - Hard Refresh: Ctrl+Shift+R"
echo "  - Incognito Mode"
echo "  - چک لاگ: tail -f /var/log/nginx/dashboard_error.log"

