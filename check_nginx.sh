#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  بررسی وضعیت Nginx${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# 1. چک نصب Nginx
echo -e "${YELLOW}▶ بررسی نصب Nginx...${NC}"
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | cut -d "/" -f 2)
    echo -e "${GREEN}✓ Nginx نصب است: $NGINX_VERSION${NC}"
else
    echo -e "${RED}✗ Nginx نصب نیست${NC}"
    exit 1
fi
echo ""

# 2. چک PHP-FPM
echo -e "${YELLOW}▶ بررسی PHP-FPM...${NC}"
PHP_FPM_SOCK=$(find /var/run/php/ -name "php*-fpm.sock" 2>/dev/null | head -n 1)

if [ -z "$PHP_FPM_SOCK" ]; then
    echo -e "${RED}✗ PHP-FPM socket یافت نشد${NC}"
    echo -e "${YELLOW}سرویس‌های PHP-FPM:${NC}"
    systemctl list-units --type=service | grep php
    echo ""
    echo -e "${YELLOW}برای نصب:${NC}"
    echo "  sudo apt install php8.2-fpm"
else
    echo -e "${GREEN}✓ PHP-FPM socket: $PHP_FPM_SOCK${NC}"
    
    # چک اینکه socket فعال است یا نه
    if [ -S "$PHP_FPM_SOCK" ]; then
        echo -e "${GREEN}✓ Socket فعال است${NC}"
    else
        echo -e "${RED}✗ Socket فعال نیست${NC}"
    fi
fi
echo ""

# 3. چک کانفیگ Nginx
echo -e "${YELLOW}▶ تست کانفیگ Nginx...${NC}"
if sudo nginx -t 2>&1; then
    echo -e "${GREEN}✓ کانفیگ صحیح است${NC}"
else
    echo -e "${RED}✗ خطا در کانفیگ${NC}"
fi
echo ""

# 4. وضعیت سرویس Nginx
echo -e "${YELLOW}▶ وضعیت سرویس Nginx...${NC}"
sudo systemctl status nginx --no-pager -l || true
echo ""

# 5. پورت‌های در حال استفاده
echo -e "${YELLOW}▶ پورت‌های در حال استفاده...${NC}"
echo -e "${BLUE}پورت 80:${NC}"
sudo ss -tulpn | grep :80 || echo "  پورت 80 آزاد است"
echo ""
echo -e "${BLUE}پورت 443:${NC}"
sudo ss -tulpn | grep :443 || echo "  پورت 443 آزاد است"
echo ""

# 6. لاگ‌های اخیر Nginx
echo -e "${YELLOW}▶ لاگ‌های اخیر Nginx...${NC}"
sudo journalctl -xeu nginx.service --no-pager | tail -20
echo ""

# 7. لیست سایت‌های فعال
echo -e "${YELLOW}▶ سایت‌های فعال در Nginx...${NC}"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "  پوشه وجود ندارد"
echo ""

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  پایان بررسی${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

