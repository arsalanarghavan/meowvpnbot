#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  اعمال تغییرات و پاک کردن cache${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# 1. رفتن به پوشه سایت
cd /var/www/meowvpnbot/site || cd /root/meowvpnbot/site

echo -e "${YELLOW}▶ پاک کردن همه cache ها...${NC}"

# 2. پاک کردن cache های Laravel
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan route:clear

# 3. پاک کردن cache های compiled
rm -rf bootstrap/cache/*.php
rm -rf storage/framework/views/*.php
rm -rf storage/framework/cache/data/*

echo -e "${GREEN}✓ Cache ها پاک شدند${NC}"
echo ""

# 4. ساخت cache جدید
echo -e "${YELLOW}▶ ساخت cache جدید...${NC}"
php artisan config:cache
php artisan route:cache

echo -e "${GREEN}✓ Cache جدید ساخته شد${NC}"
echo ""

# 5. تنظیم مجوزها
echo -e "${YELLOW}▶ تنظیم مجوزها...${NC}"
sudo chown -R www-data:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

echo -e "${GREEN}✓ مجوزها تنظیم شدند${NC}"
echo ""

# 6. ریستارت سرویس‌ها
echo -e "${YELLOW}▶ ریستارت سرویس‌ها...${NC}"
sudo systemctl restart php8.2-fpm 2>/dev/null || sudo systemctl restart php-fpm 2>/dev/null
sudo systemctl restart nginx

echo -e "${GREEN}✓ سرویس‌ها ریستارت شدند${NC}"
echo ""

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ تمام!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}حالا سایت رو refresh کن:${NC}"
echo -e "  ${GREEN}https://dashboard.meowbile.ir${NC}"
echo ""
echo -e "${YELLOW}اگر هنوز تغییرات رو نمی‌بینی:${NC}"
echo -e "  1. Ctrl+Shift+R (Hard Refresh)"
echo -e "  2. Clear کردن Browser Cache"
echo -e "  3. باز کردن در Incognito/Private"
echo ""

