#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  🔍 Debug 404 Error${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# 1. چک PHP-FPM Socket
echo -e "${YELLOW}▶ چک PHP-FPM Socket...${NC}"
if [ -S "/var/run/php/php-fpm.sock" ]; then
    echo -e "${GREEN}✓ Socket موجود است${NC}"
    ls -lh /var/run/php/php-fpm.sock
else
    echo -e "${RED}✗ Socket یافت نشد!${NC}"
    echo ""
    echo -e "${YELLOW}Socket های موجود:${NC}"
    ls -lh /var/run/php/*.sock 2>/dev/null || echo "  هیچ socket یافت نشد"
fi
echo ""

# 2. چک PHP-FPM Service
echo -e "${YELLOW}▶ وضعیت PHP-FPM...${NC}"
if systemctl is-active --quiet php8.2-fpm; then
    echo -e "${GREEN}✓ php8.2-fpm در حال اجرا${NC}"
    systemctl status php8.2-fpm --no-pager -l | grep Active
elif systemctl is-active --quiet php-fpm; then
    echo -e "${GREEN}✓ php-fpm در حال اجرا${NC}"
    systemctl status php-fpm --no-pager -l | grep Active
else
    echo -e "${RED}✗ PHP-FPM در حال اجرا نیست!${NC}"
    echo ""
    echo -e "${YELLOW}سعی در start کردن...${NC}"
    sudo systemctl start php8.2-fpm 2>/dev/null || sudo systemctl start php-fpm 2>/dev/null
    sleep 2
fi
echo ""

# 3. تست دسترسی به فایل
echo -e "${YELLOW}▶ تست دسترسی به public/index.php...${NC}"
if [ -f "/root/meowvpnbot/site/public/index.php" ]; then
    echo -e "${GREEN}✓ فایل موجود است${NC}"
    ls -lh /root/meowvpnbot/site/public/index.php
    echo ""
    echo -e "${YELLOW}محتویات اول فایل:${NC}"
    head -5 /root/meowvpnbot/site/public/index.php
else
    echo -e "${RED}✗ فایل یافت نشد!${NC}"
fi
echo ""

# 4. چک مجوزها
echo -e "${YELLOW}▶ چک مجوزها...${NC}"
ls -la /root/meowvpnbot/site/ | grep -E "public|storage|bootstrap"
echo ""

# 5. لاگ‌های Nginx
echo -e "${YELLOW}▶ آخرین خطاهای Nginx...${NC}"
if [ -f "/var/log/nginx/dashboard_error.log" ]; then
    tail -20 /var/log/nginx/dashboard_error.log
else
    echo "  لاگ خطا یافت نشد"
fi
echo ""

# 6. لاگ‌های access
echo -e "${YELLOW}▶ آخرین درخواست‌ها...${NC}"
if [ -f "/var/log/nginx/dashboard_access.log" ]; then
    tail -10 /var/log/nginx/dashboard_access.log
else
    echo "  لاگ access یافت نشد"
fi
echo ""

# 7. تست curl
echo -e "${YELLOW}▶ تست curl به localhost...${NC}"
echo -e "${BLUE}curl -I http://localhost/setup${NC}"
curl -I http://localhost/setup -H "Host: dashboard.meowbile.ir" 2>&1 | head -10
echo ""

# 8. تست با HTTPS
echo -e "${YELLOW}▶ تست HTTPS...${NC}"
echo -e "${BLUE}curl -Ik https://dashboard.meowbile.ir/setup${NC}"
curl -Ik https://dashboard.meowbile.ir/setup 2>&1 | head -15
echo ""

# 9. چک Laravel .env
echo -e "${YELLOW}▶ چک Laravel .env...${NC}"
if [ -f "/root/meowvpnbot/site/.env" ]; then
    echo -e "${GREEN}✓ .env موجود است${NC}"
    grep -E "APP_URL|APP_DEBUG" /root/meowvpnbot/site/.env
else
    echo -e "${RED}✗ .env یافت نشد!${NC}"
fi
echo ""

# 10. پیشنهادات
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  💡 پیشنهادات:${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

if [ ! -S "/var/run/php/php-fpm.sock" ]; then
    echo -e "${YELLOW}1. PHP-FPM socket یافت نشد:${NC}"
    echo "   sudo systemctl start php8.2-fpm"
    echo "   sudo systemctl restart nginx"
    echo ""
fi

echo -e "${YELLOW}2. اگر مشکل ادامه داشت:${NC}"
echo "   cd /root/meowvpnbot/site"
echo "   sudo chmod -R 755 ."
echo "   sudo chmod -R 775 storage bootstrap/cache"
echo ""

echo -e "${YELLOW}3. ریستارت همه چیز:${NC}"
echo "   sudo systemctl restart php8.2-fpm nginx"
echo ""

echo -e "${YELLOW}4. چک مستقیم PHP:${NC}"
echo "   cd /root/meowvpnbot/site/public"
echo "   php -S localhost:8000"
echo "   # بعد برو به: http://IP:8000/setup"
echo ""

