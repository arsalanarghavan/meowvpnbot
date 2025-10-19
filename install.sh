#!/bin/bash

# ==========================================
# MeowVPN Bot + Website - Wizard Installer
# نصب خودکار با Setup Wizard
# ==========================================

set -e  # Exit on any error

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# مسیرها
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
SITE_DIR="$PROJECT_ROOT/site"

# متغیرهای نصب
INSTALL_MODE="wizard"  # wizard or manual

# توابع کمکی
print_header() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║      🐱 MeowVPN - Setup Wizard Installer 🐱     ║"
    echo "║        نصب هوشمند با Setup Wizard                ║"
    echo "║                                                   ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

get_server_ip() {
    # دریافت IP سرور
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "localhost")
    echo "$SERVER_IP"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ خطا: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# شروع نصب
print_header

echo -e "${CYAN}"
echo "این نصب کننده موارد زیر را نصب می‌کند:"
echo "  • پنل وب مدیریت (با Setup Wizard)"
echo "  • ربات تلگرام (از طریق Wizard)"
echo "  • Nginx و SSL (برای subdomain)"
echo "  • Systemd service (اجرای خودکار)"
echo ""
echo -e "${NC}"

# دریافت اطلاعات subdomain
echo -e "${YELLOW}═══ تنظیمات Subdomain ═══${NC}"
echo ""
read -p "دامنه اصلی شما (مثال: mysite.com): " MAIN_DOMAIN

if [ -z "$MAIN_DOMAIN" ]; then
    print_error "دامنه نمی‌تواند خالی باشد!"
    exit 1
fi

read -p "ساب‌دامین پنل مدیریت (مثال: dashboard) [dashboard]: " PANEL_SUBDOMAIN
PANEL_SUBDOMAIN=${PANEL_SUBDOMAIN:-dashboard}

PANEL_DOMAIN="${PANEL_SUBDOMAIN}.${MAIN_DOMAIN}"

echo ""
print_info "پنل در این آدرس نصب می‌شود: ${GREEN}https://$PANEL_DOMAIN${NC}"
echo ""
print_warning "اطلاعات ادمین (یوزر و پسورد) در Setup Wizard از شما گرفته خواهد شد."
echo ""

read -p "آیا می‌خواهید ادامه دهید؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "نصب لغو شد."
    exit 1
fi

INSTALL_MODE="wizard"

# بررسی Python
print_step "بررسی Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 یافت نشد! لطفاً ابتدا Python 3.9+ را نصب کنید."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION یافت شد"

# بررسی pip
print_step "بررسی pip..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip یافت نشد! در حال نصب..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
print_success "pip آماده است"

# ایجاد virtual environment
print_step "ایجاد virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment ایجاد شد"
else
    print_info "Virtual environment از قبل وجود دارد"
fi

# فعال‌سازی virtual environment
print_step "فعال‌سازی virtual environment..."
source venv/bin/activate
print_success "Virtual environment فعال شد"

# نصب dependencies
print_step "نصب dependencies (ممکن است چند دقیقه طول بکشد)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "همه dependencies نصب شدند"

# بررسی فایل .env
print_step "بررسی فایل .env..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "فایل .env از .env.example کپی شد"
        echo ""
        print_info "🔧 لطفاً فایل .env را ویرایش کنید و اطلاعات زیر را وارد کنید:"
        echo "  • TELEGRAM_BOT_TOKEN"
        echo "  • TELEGRAM_BOT_USERNAME"
        echo "  • ADMIN_ID"
        echo "  • DATABASE_URL"
        echo ""
        read -p "آیا می‌خواهید الان فایل .env را ویرایش کنید؟ (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        else
            print_warning "بعداً فایل .env را ویرایش کنید: nano .env"
        fi
    else
        print_error "فایل .env.example یافت نشد!"
        exit 1
    fi
else
    print_success "فایل .env موجود است"
fi

# اجرای migrations
print_step "اجرای database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
    print_success "Migrations با موفقیت اجرا شدند"
else
    print_warning "Alembic یافت نشد - migrations اجرا نشد"
fi

echo ""
echo -e "${PURPLE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║         نصب پنل وب مدیریت (Website Panel)        ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# بررسی PHP
print_step "بررسی PHP..."
if ! command -v php &> /dev/null; then
    print_warning "PHP نصب نشده است!"
    read -p "آیا می‌خواهید PHP نصب شود؟ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "نصب PHP..."
        sudo apt update
        sudo apt install -y php php-cli php-mbstring php-xml php-curl php-zip php-sqlite3
        print_success "PHP نصب شد"
    else
        print_warning "نصب پنل وب رد شد - فقط ربات نصب می‌شود"
        SKIP_WEBSITE=true
    fi
else
    PHP_VERSION=$(php -v | head -n 1 | cut -d " " -f 2 | cut -d "." -f 1,2)
    print_success "PHP $PHP_VERSION یافت شد"
fi

# بررسی Composer
if [ "$SKIP_WEBSITE" != "true" ]; then
    print_step "بررسی Composer..."
    if ! command -v composer &> /dev/null; then
        print_warning "Composer نصب نشده است!"
        read -p "آیا می‌خواهید Composer نصب شود؟ (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "نصب Composer..."
            cd /tmp
            php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
            php composer-setup.php
            sudo mv composer.phar /usr/local/bin/composer
            php -r "unlink('composer-setup.php');"
            cd "$PROJECT_ROOT"
            print_success "Composer نصب شد"
        else
            print_warning "نصب پنل وب رد شد"
            SKIP_WEBSITE=true
        fi
    else
        print_success "Composer یافت شد"
    fi
fi

# نصب پنل وب
if [ "$SKIP_WEBSITE" != "true" ] && [ -d "$SITE_DIR" ]; then
    print_step "نصب dependencies پنل وب..."
    cd "$SITE_DIR"
    
    composer install --optimize-autoloader --no-interaction
    print_success "Dependencies پنل وب نصب شد"
    
    # تنظیم .env
    if [ ! -f ".env" ]; then
        # تولید random secret
        WIZARD_SECRET=$(openssl rand -hex 32)
        
        cat > .env << ENVFILE
APP_NAME="MeowVPN Panel"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=https://$PANEL_DOMAIN

LOG_CHANNEL=daily
LOG_LEVEL=warning

SESSION_DRIVER=file
CACHE_DRIVER=file

# Admin Credentials (خالی - در Setup Wizard تنظیم می‌شود)
ADMIN_USERNAME=
ADMIN_PASSWORD=

# Setup Wizard
SETUP_WIZARD_ENABLED=true
SETUP_WIZARD_SECRET=${WIZARD_SECRET}
BOT_INSTALLED=false
FIRST_RUN=true
ENVFILE
        print_success "فایل .env پنل وب ایجاد شد"
        print_info "اطلاعات ادمین در Setup Wizard تنظیم خواهد شد"
    fi
    
    # تولید APP_KEY
    php artisan key:generate --force
    print_success "کلید برنامه تولید شد"
    
    # تنظیم مجوزها
    mkdir -p storage/framework/{sessions,views,cache} storage/logs bootstrap/cache
    chmod -R 775 storage bootstrap/cache
    
    # پاک‌سازی کش
    php artisan config:clear
    php artisan cache:clear
    php artisan view:clear
    php artisan route:clear
    
    print_success "پنل وب با موفقیت نصب شد"
    
    cd "$PROJECT_ROOT"
    WEBSITE_INSTALLED=true
    
    # نصب و تنظیم Nginx
    echo ""
    print_step "نصب و تنظیم Nginx..."
    
    if ! command -v nginx &> /dev/null; then
        print_info "نصب Nginx..."
        sudo apt update
        sudo apt install -y nginx certbot python3-certbot-nginx
        print_success "Nginx نصب شد"
    else
        print_success "Nginx از قبل نصب شده است"
    fi
    
    # ایجاد کانفیگ Nginx
    print_step "ایجاد کانفیگ Nginx..."
    
    sudo tee /etc/nginx/sites-available/$PANEL_DOMAIN > /dev/null <<NGINXCONF
server {
    listen 80;
    server_name $PANEL_DOMAIN;
    
    root $SITE_DIR/public;
    index index.php;

    access_log /var/log/nginx/${PANEL_SUBDOMAIN}_access.log;
    error_log /var/log/nginx/${PANEL_SUBDOMAIN}_error.log;

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
NGINXCONF
    
    # فعال‌سازی سایت
    sudo ln -sf /etc/nginx/sites-available/$PANEL_DOMAIN /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # تست کانفیگ
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_success "Nginx تنظیم شد"
    
    # نصب SSL
    echo ""
    print_step "نصب SSL Certificate..."
    print_warning "توجه: DNS باید به IP سرور شما اشاره کند!"
    echo ""
    read -p "آیا DNS تنظیم شده است؟ (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "دریافت SSL Certificate..."
        sudo certbot --nginx -d $PANEL_DOMAIN --non-interactive --agree-tos --email admin@$MAIN_DOMAIN --redirect
        
        if [ $? -eq 0 ]; then
            print_success "SSL Certificate نصب شد"
            PANEL_URL="https://$PANEL_DOMAIN"
        else
            print_warning "SSL نصب نشد - از HTTP استفاده می‌شود"
            PANEL_URL="http://$PANEL_DOMAIN"
        fi
    else
        print_warning "SSL رد شد - بعداً با certbot نصب کنید"
        PANEL_URL="http://$PANEL_DOMAIN"
    fi
    
    # تنظیم مجوزها برای www-data
    sudo chown -R www-data:www-data "$SITE_DIR/storage" "$SITE_DIR/bootstrap/cache"
    
    print_success "سرور وب آماده است"
    
else
    print_warning "نصب پنل وب رد شد یا پوشه site یافت نشد"
    WEBSITE_INSTALLED=false
fi

# ایجاد فایل systemd service (اختیاری)
echo ""
read -p "آیا می‌خواهید systemd service ایجاد شود؟ (برای اجرای خودکار) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "ایجاد systemd service..."
    
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    VENV_PYTHON="$CURRENT_DIR/venv/bin/python"
    
    sudo tee /etc/systemd/system/meowvpnbot.service > /dev/null <<EOF
[Unit]
Description=MeowVPN Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$VENV_PYTHON main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable meowvpnbot.service
    print_success "Systemd service ایجاد و فعال شد"
    
    echo ""
    print_info "برای کنترل service از دستورات زیر استفاده کنید:"
    echo "  • شروع:    sudo systemctl start meowvpnbot"
    echo "  • توقف:     sudo systemctl stop meowvpnbot"
    echo "  • ریستارت: sudo systemctl restart meowvpnbot"
    echo "  • وضعیت:   sudo systemctl status meowvpnbot"
    echo "  • لاگ‌ها:   sudo journalctl -u meowvpnbot -f"
fi

# تست نصب
echo ""
print_step "تست نصب..."

# بررسی فایل‌های ضروری
REQUIRED_FILES=("main.py" "bot/" "database/" "core/" "locales/fa.json")
ALL_OK=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
        print_error "فایل ضروری یافت نشد: $file"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = true ]; then
    print_success "تمام فایل‌های ضروری موجود هستند"
fi

# نمایش خلاصه
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}║            ✅ نصب با موفقیت انجام شد! ✅          ║${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

print_info "📋 مرحله نهایی - Setup Wizard"
echo ""

if [ "$WEBSITE_INSTALLED" = "true" ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✨ نصب با موفقیت انجام شد! ✨            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # نمایش اطلاعات دسترسی
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🌐 آدرس پنل مدیریت:${NC}"
    echo ""
    echo -e "   ${GREEN}$PANEL_URL${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}👤 اطلاعات ورود:${NC}"
    echo ""
    echo -e "   Username: ${YELLOW}$ADMIN_USER${NC}"
    echo -e "   Password: ${YELLOW}(همان رمزی که وارد کردید)${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # راهنمای مرحله بعد
    echo -e "${YELLOW}📌 مرحله بعدی - Setup Wizard:${NC}"
    echo ""
    echo -e "  ${GREEN}1.${NC} مرورگر را باز کنید"
    echo -e "  ${GREEN}2.${NC} به این آدرس بروید:"
    echo ""
    echo -e "     ${BLUE}$PANEL_URL/setup${NC}"
    echo ""
    echo -e "  ${GREEN}3.${NC} ایجاد حساب ادمین:"
    echo -e "     ▸ یوزرنیم دلخواه شما"
    echo -e "     ▸ پسورد امن (حداقل 6 کاراکتر)"
    echo ""
    echo -e "  ${GREEN}4.${NC} انتخاب کنید:"
    echo -e "     📦 بازیابی از بکاپ قدیمی (demo.sql)"
    echo -e "     🚀 نصب جدید (از ابتدا)"
    echo ""
    echo -e "  ${GREEN}5.${NC} تکمیل Setup Wizard (4 مرحله):"
    echo -e "     ✓ تنظیمات ربات تلگرام"
    echo -e "     ✓ اطلاعات پنل VPN"
    echo -e "     ✓ تنظیمات پرداخت"
    echo -e "     ✓ نصب خودکار ربات"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # کپی لینک مستقیم
    SETUP_URL="$PANEL_URL/setup"
    
    echo -e "${GREEN}🎯 لینک Setup Wizard (کلیک کنید):${NC}"
    echo ""
    echo -e "   ${BLUE}$SETUP_URL${NC}"
    echo ""
    
    # نمایش QR Code (اگر qrencode نصب باشد)
    if command -v qrencode &> /dev/null; then
        echo -e "${CYAN}📱 QR Code برای دسترسی سریع:${NC}"
        qrencode -t ANSIUTF8 "$SETUP_URL"
        echo ""
    fi
    
    echo -e "${YELLOW}⚠️  نکات مهم:${NC}"
    echo ""
    echo "  • یوزر و پسورد در Setup Wizard از شما گرفته می‌شود"
    echo "  • هیچ رمز پیش‌فرضی وجود ندارد (امنیت 100%)"
    echo "  • Setup Wizard فقط یک بار قابل اجراست"
    echo "  • می‌توانید demo.sql را Import کنید"
    echo "  • بعد از Wizard، ربات خودکار راه‌اندازی می‌شود"
    echo ""
else
    echo "  ${CYAN}1. ربات را اجرا کنید:${NC}"
    echo "     ${GREEN}source venv/bin/activate${NC}"
    echo "     ${GREEN}python main.py${NC}"
    echo ""
fi

print_info "📚 فایل‌های مهم:"
echo "  • START_HERE.md - شروع از اینجا ⭐"
echo "  • QUICK_START.md - راهنمای سریع"
echo "  • DEPLOYMENT_GUIDE.md - راهنمای کامل"
echo "  • CARD_MANAGEMENT_GUIDE.md - راهنمای کارت‌ها 🆕"
echo ""

echo -e "${PURPLE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       🎉 از استفاده از MeowVPN Bot              ║${NC}"
echo -e "${PURPLE}║            لذت ببرید! 🚀                          ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# نمایش لوگو نهایی
echo -e "${CYAN}"
cat << "EOF"
     /\_/\  
    ( o.o ) 
     > ^ <   MeowVPN Bot v2.5.0
    /|   |\  Ready to meow! 🐱
   (_|   |_)
EOF
echo -e "${NC}"

print_success "نصب کامل شد! موفق باشید! 🎊"

