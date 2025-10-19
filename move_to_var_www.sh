#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  انتقال پروژه به /var/www${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# 1. چک کردن پروژه فعلی
if [ ! -d "/root/meowvpnbot" ]; then
    echo -e "${RED}✗ پروژه در /root/meowvpnbot یافت نشد!${NC}"
    exit 1
fi

echo -e "${YELLOW}▶ پروژه فعلی: /root/meowvpnbot${NC}"
echo -e "${YELLOW}▶ مقصد: /var/www/meowvpnbot${NC}"
echo ""

# 2. پشتیبان‌گیری از دیتابیس
echo -e "${YELLOW}▶ پشتیبان‌گیری از دیتابیس...${NC}"
if [ -f "/root/meowvpnbot/bot.db" ]; then
    cp /root/meowvpnbot/bot.db /root/bot_backup_$(date +%Y%m%d_%H%M%S).db
    echo -e "${GREEN}✓ بکاپ: /root/bot_backup_*.db${NC}"
fi

if [ -f "/root/meowvpnbot/.env" ]; then
    cp /root/meowvpnbot/.env /root/env_backup_$(date +%Y%m%d_%H%M%S).txt
    echo -e "${GREEN}✓ بکاپ: /root/env_backup_*.txt${NC}"
fi

if [ -f "/root/meowvpnbot/site/.env" ]; then
    cp /root/meowvpnbot/site/.env /root/site_env_backup_$(date +%Y%m%d_%H%M%S).txt
    echo -e "${GREEN}✓ بکاپ: /root/site_env_backup_*.txt${NC}"
fi
echo ""

# 3. متوقف کردن سرویس‌ها
echo -e "${YELLOW}▶ متوقف کردن سرویس‌ها...${NC}"
sudo systemctl stop meowvpn-bot 2>/dev/null || echo "  ربات در حال اجرا نبود"
echo -e "${GREEN}✓ سرویس‌ها متوقف شدند${NC}"
echo ""

# 4. انتقال پروژه
echo -e "${YELLOW}▶ انتقال پروژه...${NC}"
if [ -d "/var/www/meowvpnbot" ]; then
    echo -e "${YELLOW}! پوشه مقصد وجود دارد، در حال حذف...${NC}"
    sudo rm -rf /var/www/meowvpnbot
fi

sudo mv /root/meowvpnbot /var/www/meowvpnbot
echo -e "${GREEN}✓ پروژه منتقل شد${NC}"
echo ""

# 5. تنظیم مجوزها
echo -e "${YELLOW}▶ تنظیم مجوزها...${NC}"
sudo chown -R www-data:www-data /var/www/meowvpnbot
sudo chmod -R 755 /var/www/meowvpnbot
sudo chmod -R 775 /var/www/meowvpnbot/site/storage
sudo chmod -R 775 /var/www/meowvpnbot/site/bootstrap/cache
echo -e "${GREEN}✓ مجوزها تنظیم شدند${NC}"
echo ""

# 6. به‌روزرسانی Nginx config
echo -e "${YELLOW}▶ به‌روزرسانی Nginx config...${NC}"
NGINX_CONFIG="/etc/nginx/sites-available/dashboard.meowbile.ir"

if [ -f "$NGINX_CONFIG" ]; then
    # بکاپ از config
    sudo cp $NGINX_CONFIG ${NGINX_CONFIG}.backup
    
    # تغییر مسیر
    sudo sed -i 's|/root/meowvpnbot|/var/www/meowvpnbot|g' $NGINX_CONFIG
    
    echo -e "${GREEN}✓ Nginx config به‌روز شد${NC}"
    echo -e "${BLUE}  بکاپ: ${NGINX_CONFIG}.backup${NC}"
else
    echo -e "${RED}✗ Nginx config یافت نشد!${NC}"
fi
echo ""

# 7. به‌روزرسانی systemd service
echo -e "${YELLOW}▶ به‌روزرسانی systemd service...${NC}"
SERVICE_FILE="/etc/systemd/system/meowvpn-bot.service"

if [ -f "$SERVICE_FILE" ]; then
    # بکاپ
    sudo cp $SERVICE_FILE ${SERVICE_FILE}.backup
    
    # تغییر مسیر
    sudo sed -i 's|/root/meowvpnbot|/var/www/meowvpnbot|g' $SERVICE_FILE
    
    # reload daemon
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✓ Systemd service به‌روز شد${NC}"
    echo -e "${BLUE}  بکاپ: ${SERVICE_FILE}.backup${NC}"
else
    echo -e "${YELLOW}! Service file یافت نشد (نرمال است اگر هنوز نصب نکرده‌ای)${NC}"
fi
echo ""

# 8. تست Nginx config
echo -e "${YELLOW}▶ تست Nginx config...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx config صحیح است${NC}"
else
    echo -e "${RED}✗ خطا در Nginx config!${NC}"
    echo -e "${YELLOW}بازگردانی config قدیمی...${NC}"
    sudo cp ${NGINX_CONFIG}.backup $NGINX_CONFIG
    sudo mv /var/www/meowvpnbot /root/meowvpnbot
    exit 1
fi
echo ""

# 9. پاکسازی Laravel cache
echo -e "${YELLOW}▶ پاکسازی Laravel cache...${NC}"
cd /var/www/meowvpnbot/site
php artisan config:clear
php artisan cache:clear
php artisan route:clear
php artisan view:clear
php artisan config:cache
php artisan route:cache
echo -e "${GREEN}✓ Cache پاک شد${NC}"
echo ""

# 10. ریستارت سرویس‌ها
echo -e "${YELLOW}▶ ریستارت سرویس‌ها...${NC}"
sudo systemctl restart php8.2-fpm 2>/dev/null || sudo systemctl restart php-fpm 2>/dev/null
sudo systemctl restart nginx
sudo systemctl start meowvpn-bot 2>/dev/null || echo "  ربات هنوز نصب نشده"
echo -e "${GREEN}✓ سرویس‌ها ریستارت شدند${NC}"
echo ""

# 11. چک وضعیت
echo -e "${YELLOW}▶ چک وضعیت نهایی...${NC}"
sleep 2

if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx: Running${NC}"
else
    echo -e "${RED}✗ Nginx: Stopped${NC}"
fi

if sudo systemctl is-active --quiet php8.2-fpm || sudo systemctl is-active --quiet php-fpm; then
    echo -e "${GREEN}✓ PHP-FPM: Running${NC}"
else
    echo -e "${RED}✗ PHP-FPM: Stopped${NC}"
fi

if sudo systemctl is-active --quiet meowvpn-bot; then
    echo -e "${GREEN}✓ Bot: Running${NC}"
else
    echo -e "${YELLOW}! Bot: Not started (نرمال است)${NC}"
fi
echo ""

# 12. تست دسترسی
echo -e "${YELLOW}▶ تست دسترسی...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/setup -H "Host: dashboard.meowbile.ir")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✓ سایت در دسترس است! (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${YELLOW}! هنوز 404 (ممکنه به Laravel cache نیاز داشته باشه)${NC}"
else
    echo -e "${RED}✗ HTTP Code: $HTTP_CODE${NC}"
fi
echo ""

# 13. نتیجه نهایی
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ انتقال با موفقیت انجام شد!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📁 مسیر جدید:${NC}"
echo -e "   /var/www/meowvpnbot"
echo ""
echo -e "${BLUE}💾 بکاپ‌ها:${NC}"
ls -1 /root/*backup* 2>/dev/null | sed 's/^/   /'
echo ""
echo -e "${BLUE}🌐 تست سایت:${NC}"
echo -e "   ${GREEN}https://dashboard.meowbile.ir/setup${NC}"
echo ""
echo -e "${BLUE}📝 لاگ‌ها:${NC}"
echo -e "   tail -f /var/log/nginx/dashboard_error.log"
echo ""
echo -e "${YELLOW}اگر هنوز 404 میده:${NC}"
echo -e "   cd /var/www/meowvpnbot"
echo -e "   bash fix_laravel.sh"
echo ""

