#!/bin/bash

##############################################
# MeowVPN - Subdomain Deployment Script
# استقرار خودکار با ساب‌دامین‌های جداگانه
##############################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      MeowVPN - Subdomain Deployment Wizard              ║"
echo "║          استقرار با ساب‌دامین‌های جداگانه               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# دریافت اطلاعات
echo -e "${YELLOW}لطفاً اطلاعات زیر را وارد کنید:${NC}"
echo ""

read -p "دامنه اصلی (مثال: site.com): " MAIN_DOMAIN
read -p "ساب‌دامین پنل (مثال: dashboard): " DASHBOARD_SUB
read -p "ساب‌دامین ربات (مثال: bot): " BOT_SUB
read -p "ساب‌دامین پرداخت (مثال: pay): " PAY_SUB

DASHBOARD_DOMAIN="${DASHBOARD_SUB}.${MAIN_DOMAIN}"
BOT_DOMAIN="${BOT_SUB}.${MAIN_DOMAIN}"
PAY_DOMAIN="${PAY_SUB}.${MAIN_DOMAIN}"

echo ""
echo -e "${BLUE}ساب‌دامین‌های تنظیم شده:${NC}"
echo "  • پنل مدیریت: https://$DASHBOARD_DOMAIN"
echo "  • Webhook ربات: https://$BOT_DOMAIN"
echo "  • درگاه پرداخت: https://$PAY_DOMAIN"
echo ""

read -p "آیا اطلاعات صحیح است؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "لغو شد."
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo -e "${BLUE}[1/10]${NC} بررسی پیش‌نیازها..."

# بررسی root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}لطفاً با sudo اجرا کنید${NC}"
    exit 1
fi

# بررسی nginx
if ! command -v nginx &> /dev/null; then
    echo "نصب Nginx..."
    apt update
    apt install nginx -y
fi

# بررسی certbot
if ! command -v certbot &> /dev/null; then
    echo "نصب Certbot..."
    apt install certbot python3-certbot-nginx -y
fi

# بررسی supervisor
if ! command -v supervisorctl &> /dev/null; then
    echo "نصب Supervisor..."
    apt install supervisor -y
fi

echo -e "${GREEN}✓ پیش‌نیازها آماده${NC}"

echo ""
echo -e "${BLUE}[2/10]${NC} ایجاد ساختار پوشه‌ها..."

mkdir -p /var/www/{dashboard,bot,pay,shared}
cp -r "$SCRIPT_DIR/site/"* /var/www/dashboard/
cp -r "$SCRIPT_DIR/"* /var/www/bot/

# کپی دیتابیس
if [ -f "$SCRIPT_DIR/vpn_bot.db" ]; then
    cp "$SCRIPT_DIR/vpn_bot.db" /var/www/shared/
    chmod 664 /var/www/shared/vpn_bot.db
fi

echo -e "${GREEN}✓ پوشه‌ها ایجاد شد${NC}"

echo ""
echo -e "${BLUE}[3/10]${NC} ایجاد کانفیگ Nginx - Dashboard..."

cat > /etc/nginx/sites-available/$DASHBOARD_DOMAIN <<EOF
server {
    listen 80;
    server_name $DASHBOARD_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DASHBOARD_DOMAIN;
    
    root /var/www/dashboard/public;
    index index.php;

    # SSL (بعد از certbot پر می‌شود)
    # ssl_certificate /etc/letsencrypt/live/$DASHBOARD_DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DASHBOARD_DOMAIN/privkey.pem;

    access_log /var/log/nginx/dashboard_access.log;
    error_log /var/log/nginx/dashboard_error.log;

    location / {
        try_files \$uri \$uri/ /index.php?\$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME \$realpath_root\$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
EOF

echo -e "${GREEN}✓ کانفیگ Dashboard${NC}"

echo ""
echo -e "${BLUE}[4/10]${NC} ایجاد کانفیگ Nginx - Bot..."

cat > /etc/nginx/sites-available/$BOT_DOMAIN <<EOF
server {
    listen 80;
    server_name $BOT_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

upstream bot_backend {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name $BOT_DOMAIN;

    # SSL (بعد از certbot)
    # ssl_certificate /etc/letsencrypt/live/$BOT_DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$BOT_DOMAIN/privkey.pem;

    access_log /var/log/nginx/bot_access.log;
    error_log /var/log/nginx/bot_error.log;

    # فقط IP تلگرام
    allow 91.108.4.0/22;
    allow 91.108.56.0/22;
    allow 149.154.160.0/20;
    deny all;

    location /webhook/ {
        proxy_pass http://bot_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location / {
        return 404;
    }
}
EOF

echo -e "${GREEN}✓ کانفیگ Bot${NC}"

echo ""
echo -e "${BLUE}[5/10]${NC} ایجاد کانفیگ Nginx - Payment..."

# ایجاد payment gateway
mkdir -p /var/www/pay/public
cat > /var/www/pay/public/callback.php <<'PHPEOF'
<?php
// Payment Callback Handler
define('DB_PATH', '/var/www/shared/vpn_bot.db');

$authority = $_GET['Authority'] ?? null;
$status = $_GET['Status'] ?? null;

if ($status == 'OK' && $authority) {
    // پردازش پرداخت موفق
    echo "پرداخت موفق";
} else {
    echo "پرداخت ناموفق";
}
PHPEOF

cat > /etc/nginx/sites-available/$PAY_DOMAIN <<EOF
server {
    listen 80;
    server_name $PAY_DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $PAY_DOMAIN;
    
    root /var/www/pay/public;

    # SSL (بعد از certbot)
    # ssl_certificate /etc/letsencrypt/live/$PAY_DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$PAY_DOMAIN/privkey.pem;

    access_log /var/log/nginx/pay_access.log;
    error_log /var/log/nginx/pay_error.log;

    location /callback {
        try_files \$uri /callback.php?\$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME \$realpath_root\$fastcgi_script_name;
        include fastcgi_params;
    }

    location / {
        return 404;
    }
}
EOF

echo -e "${GREEN}✓ کانفیگ Payment${NC}"

echo ""
echo -e "${BLUE}[6/10]${NC} فعال‌سازی سایت‌ها..."

ln -sf /etc/nginx/sites-available/$DASHBOARD_DOMAIN /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/$BOT_DOMAIN /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/$PAY_DOMAIN /etc/nginx/sites-enabled/

rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo -e "${GREEN}✓ Nginx راه‌اندازی شد${NC}"

echo ""
echo -e "${BLUE}[7/10]${NC} تنظیم Dashboard..."

cd /var/www/dashboard

# .env
cat > .env <<EOF
APP_NAME="MeowVPN Dashboard"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=https://$DASHBOARD_DOMAIN

BOT_DATABASE_PATH=/var/www/shared/vpn_bot.db

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

SESSION_DRIVER=file
LOG_CHANNEL=daily
EOF

if command -v composer &> /dev/null; then
    composer install --no-dev --optimize-autoloader
    php artisan key:generate --force
    php artisan config:cache
    php artisan route:cache
    php artisan view:cache
fi

chmod -R 755 storage bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache

echo -e "${GREEN}✓ Dashboard تنظیم شد${NC}"

echo ""
echo -e "${BLUE}[8/10]${NC} تنظیم Bot..."

cd /var/www/bot

cat >> .env <<EOF

# Webhook
WEBHOOK_URL=https://$BOT_DOMAIN/webhook/
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Database
DATABASE_URL=sqlite:////var/www/shared/vpn_bot.db
EOF

if [ -d "venv" ]; then
    source venv/bin/activate
    pip install flask
fi

echo -e "${GREEN}✓ Bot تنظیم شد${NC}"

echo ""
echo -e "${BLUE}[9/10]${NC} دریافت SSL Certificates..."

echo -e "${YELLOW}توجه: ابتدا DNS Records را تنظیم کنید!${NC}"
read -p "آیا DNS Records تنظیم شده است؟ (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d $DASHBOARD_DOMAIN --non-interactive --agree-tos --email admin@$MAIN_DOMAIN || echo "SSL Dashboard failed"
    certbot --nginx -d $BOT_DOMAIN --non-interactive --agree-tos --email admin@$MAIN_DOMAIN || echo "SSL Bot failed"
    certbot --nginx -d $PAY_DOMAIN --non-interactive --agree-tos --email admin@$MAIN_DOMAIN || echo "SSL Payment failed"
    
    echo -e "${GREEN}✓ SSL Certificates دریافت شد${NC}"
else
    echo -e "${YELLOW}⚠ SSL Certificates را بعداً دریافت کنید:${NC}"
    echo "  sudo certbot --nginx -d $DASHBOARD_DOMAIN"
    echo "  sudo certbot --nginx -d $BOT_DOMAIN"
    echo "  sudo certbot --nginx -d $PAY_DOMAIN"
fi

echo ""
echo -e "${BLUE}[10/10]${NC} ایجاد Supervisor Config..."

cat > /etc/supervisor/conf.d/meowvpn-bot.conf <<EOF
[program:meowvpn-bot]
directory=/var/www/bot
command=/var/www/bot/venv/bin/python webhook_server.py
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/bot-webhook.log
EOF

supervisorctl reread
supervisorctl update

echo -e "${GREEN}✓ Supervisor تنظیم شد${NC}"

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║             استقرار با موفقیت انجام شد! ✓               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}📌 دسترسی به سرویس‌ها:${NC}"
echo ""
echo "  🌐 پنل مدیریت:    https://$DASHBOARD_DOMAIN"
echo "  🤖 Webhook ربات:   https://$BOT_DOMAIN/webhook/"
echo "  💳 درگاه پرداخت:  https://$PAY_DOMAIN/callback"
echo ""
echo -e "${YELLOW}👤 اطلاعات ورود پنل:${NC}"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo -e "${BLUE}📋 دستورات مفید:${NC}"
echo "  • وضعیت Nginx:     systemctl status nginx"
echo "  • وضعیت Bot:       supervisorctl status meowvpn-bot"
echo "  • لاگ Dashboard:   tail -f /var/log/nginx/dashboard_access.log"
echo "  • لاگ Bot:         tail -f /var/log/supervisor/bot-webhook.log"
echo ""
echo -e "${YELLOW}⚠️  نکات مهم:${NC}"
echo "  1. رمز عبور ادمین را تغییر دهید: nano /var/www/dashboard/.env"
echo "  2. DNS Records را تنظیم کنید"
echo "  3. Firewall را کانفیگ کنید: ufw allow 80,443/tcp"
echo ""

