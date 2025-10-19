#!/bin/bash
##############################################
# MeowVPN Bot - Website Updater
# به‌روزرسانی خودکار پنل وب مدیریت
##############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         MeowVPN Bot - Website Panel Updater            ║"
echo "║             به‌روزرسانی پنل وب مدیریت                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
SITE_DIR="$PROJECT_ROOT/site"

echo -e "${BLUE}[1/6]${NC} بررسی پیش‌نیازها..."

if [ ! -d "$SITE_DIR" ]; then
    echo -e "${RED}✗ پوشه سایت یافت نشد!${NC}"
    echo -e "${YELLOW}! ابتدا نصب را انجام دهید: ./install_website.sh${NC}"
    exit 1
fi

cd "$SITE_DIR"

if [ ! -f "composer.json" ]; then
    echo -e "${RED}✗ فایل composer.json یافت نشد${NC}"
    exit 1
fi

echo -e "${GREEN}✓ فایل‌های پروژه موجود است${NC}"

echo -e "${BLUE}[2/6]${NC} گرفتن آخرین تغییرات از Git..."

cd "$PROJECT_ROOT"

if [ -d ".git" ]; then
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo -e "${YELLOW}! Git pull انجام نشد${NC}"
    echo -e "${GREEN}✓ تغییرات Git دریافت شد${NC}"
else
    echo -e "${YELLOW}! این پروژه از Git استفاده نمی‌کند${NC}"
fi

cd "$SITE_DIR"

echo -e "${BLUE}[3/6]${NC} به‌روزرسانی dependencies..."

composer install --optimize-autoloader --no-interaction

echo -e "${GREEN}✓ Dependencies به‌روزرسانی شد${NC}"

echo -e "${BLUE}[4/6]${NC} پاک‌سازی کش‌ها..."

php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear

echo -e "${GREEN}✓ کش‌ها پاک شد${NC}"

echo -e "${BLUE}[5/6]${NC} بهینه‌سازی..."

# Optimize for production
if [ -f ".env" ] && grep -q "APP_ENV=production" ".env"; then
    echo -e "${YELLOW}  محیط Production شناسایی شد، در حال بهینه‌سازی...${NC}"
    php artisan config:cache
    php artisan route:cache
    php artisan view:cache
    echo -e "${GREEN}✓ بهینه‌سازی Production انجام شد${NC}"
else
    echo -e "${YELLOW}  محیط Development - بهینه‌سازی انجام نشد${NC}"
fi

echo -e "${BLUE}[6/6]${NC} بررسی سلامت..."

# Check database connection
cd "$PROJECT_ROOT"
if [ -f "vpn_bot.db" ]; then
    echo -e "${GREEN}✓ دیتابیس ربات موجود است${NC}"
else
    echo -e "${RED}✗ دیتابیس ربات یافت نشد!${NC}"
fi

# Final message
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║             به‌روزرسانی با موفقیت انجام شد! ✓            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${YELLOW}📌 مرحله بعد:${NC}"
echo ""
echo -e "  اگر پنل در حال اجراست، لطفاً آن را ری‌استارت کنید:"
echo ""
echo -e "  ${BLUE}./stop_website.sh${NC}"
echo -e "  ${BLUE}./start_website.sh${NC}"
echo ""
echo -e "  یا فقط ${BLUE}Ctrl+C${NC} و دوباره ${BLUE}./start_website.sh${NC}"
echo ""

