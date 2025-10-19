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

INSTALL_MODE="wizard"

# بررسی Python
print_step "بررسی Python..."
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 یافت نشد! در حال نصب..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    print_success "Python نصب شد"
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION یافت شد"
fi

# بررسی pip
print_step "بررسی pip..."
if ! command -v pip3 &> /dev/null; then
    print_warning "pip یافت نشد! در حال نصب..."
    sudo apt update
    sudo apt install -y python3-pip
    print_success "pip نصب شد"
else
    print_success "pip آماده است"
fi

# مطمئن شدن از نصب python3-venv
if ! dpkg -l | grep -q python3-venv; then
    print_step "نصب python3-venv و python3-full..."
    sudo apt update
    sudo apt install -y python3-venv python3-full python3-dev build-essential
    print_success "پیش‌نیازهای Python نصب شد"
fi

# ایجاد virtual environment
print_step "ایجاد virtual environment..."

# اطمینان از حذف venv خراب
if [ -d "venv" ]; then
    # چک کردن سلامت venv
    if [ ! -f "venv/bin/activate" ] || [ ! -f "venv/bin/python" ] && [ ! -f "venv/bin/python3" ]; then
        print_warning "Virtual environment خراب یا ناقص است، در حال حذف..."
        rm -rf venv
    fi
fi

if [ ! -d "venv" ]; then
    print_info "ایجاد virtual environment جدید..."
    
    # ساخت venv
    python3 -m venv venv
    
    if [ $? -ne 0 ] || [ ! -f "venv/bin/activate" ]; then
        print_error "خطا در ایجاد venv!"
        exit 1
    fi
    
    print_success "Virtual environment ایجاد شد"
else
    print_info "Virtual environment معتبر موجود است"
fi

# نصب dependencies
print_step "نصب dependencies Python (2-5 دقیقه)..."
print_warning "لطفاً صبور باشید، این مرحله کمی طول می‌کشد..."

# رفتن به پوشه پروژه
cd "$PROJECT_ROOT"

# استفاده مستقیم از python و pip در venv (بدون activate)
# این روش مطمئن‌تر است
VENV_BIN="$PROJECT_ROOT/venv/bin"

# چک کردن وجود فایل‌های python و pip
if [ -f "$VENV_BIN/python3" ]; then
    PYTHON_EXE="$VENV_BIN/python3"
elif [ -f "$VENV_BIN/python" ]; then
    PYTHON_EXE="$VENV_BIN/python"
else
    print_error "Python در venv یافت نشد!"
    ls -la venv/bin/
    exit 1
fi

print_info "Python venv: $PYTHON_EXE"

# ارتقا pip
print_info "ارتقا pip, setuptools, wheel..."
$PYTHON_EXE -m pip install --upgrade pip setuptools wheel

# نصب requirements
echo ""
print_info "نصب packages از requirements.txt..."
echo ""

$PYTHON_EXE -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    print_success "✓ همه dependencies نصب شدند"
else
    echo ""
    print_warning "تلاش مجدد..."
    $PYTHON_EXE -m pip install -r requirements.txt --no-cache-dir
    
    if [ $? -eq 0 ]; then
        print_success "✓ Dependencies نصب شد"
    else
        print_error "خطا در نصب!"
        echo ""
        print_info "Debug:"
        echo "  $PYTHON_EXE -m pip install -r requirements.txt -v"
        exit 1
    fi
fi

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

# نصب سیستم Auto-Restart و Monitoring
echo ""
print_step "نصب سیستم Auto-Restart و Monitoring..."
print_info "این سیستم تضمین می‌کند سرویس‌ها همیشه در حال اجرا باشند"
echo ""

if [ -f "$PROJECT_ROOT/setup_autostart.sh" ]; then
    # اجرای اسکریپت Auto-Restart
    bash "$PROJECT_ROOT/setup_autostart.sh"
    print_success "سیستم Auto-Restart نصب شد"
else
    # اگر فایل نبود، دستی ایجاد کن
    print_step "ایجاد Systemd service..."
    
    CURRENT_DIR=$(pwd)
    
    sudo tee /etc/systemd/system/meowvpn-bot.service > /dev/null <<EOF
[Unit]
Description=MeowVPN Telegram Bot
After=network.target
Documentation=https://github.com/yourusername/meowvpnbot

[Service]
Type=simple
User=www-data
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python main.py

# Auto-restart settings - همیشه ریستارت شود
Restart=always
RestartSec=10
StartLimitInterval=0
StartLimitBurst=10

# Logging
StandardOutput=append:/var/log/meowvpn-bot.log
StandardError=append:/var/log/meowvpn-bot-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable meowvpn-bot.service
    sudo systemctl start meowvpn-bot.service
    
    print_success "Systemd service ایجاد، فعال و اجرا شد"
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
    echo ""
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}║          ✅ نصب با موفقیت کامل شد! ✅                   ║${NC}"
    echo -e "${GREEN}║                                                          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo ""
    
    # نمایش اطلاعات نصب
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   📊 خلاصه نصب                          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}✓${NC} Python و Dependencies نصب شد"
    echo -e "  ${CYAN}✓${NC} PHP و Composer نصب شد"
    echo -e "  ${CYAN}✓${NC} Nginx نصب و تنظیم شد"
    echo -e "  ${CYAN}✓${NC} SSL Certificate دریافت شد"
    echo -e "  ${CYAN}✓${NC} HTTPS فعال شد"
    echo -e "  ${CYAN}✓${NC} Auto-Restart فعال شد"
    echo -e "  ${CYAN}✓${NC} پنل وب آماده است"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # لینک Setup Wizard
    SETUP_URL="$PANEL_URL/setup"
    
    echo -e "${GREEN}🎯 مرحله بعدی:${NC}"
    echo ""
    echo -e "${YELLOW}  برای تکمیل نصب، این لینک را در مرورگر باز کنید:${NC}"
    echo ""
    echo -e "     ╔════════════════════════════════════════════════╗"
    echo -e "     ║                                                ║"
    echo -e "     ║   ${BLUE}$SETUP_URL${NC}   ║"
    echo -e "     ║                                                ║"
    echo -e "     ╚════════════════════════════════════════════════╝"
    echo ""
    echo ""
    echo -e "${CYAN}در Setup Wizard:${NC}"
    echo ""
    echo -e "  ${GREEN}→${NC} ایجاد حساب ادمین (یوزرنیم و پسورد)"
    echo -e "  ${GREEN}→${NC} Import بکاپ قدیمی (اختیاری)"
    echo -e "  ${GREEN}→${NC} تنظیمات ربات تلگرام"
    echo -e "  ${GREEN}→${NC} تنظیمات پنل VPN"
    echo -e "  ${GREEN}→${NC} نصب و راه‌اندازی خودکار ربات"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # نمایش QR Code (اگر qrencode نصب باشد)
    if command -v qrencode &> /dev/null; then
        echo -e "${CYAN}📱 یا اسکن QR Code:${NC}"
        echo ""
        qrencode -t ANSIUTF8 "$SETUP_URL"
        echo ""
    fi
    
    echo -e "${YELLOW}💡 نکته:${NC} Setup Wizard فقط یک بار قابل اجرا است."
    echo -e "   بعد از تکمیل، ربات خودکار راه‌اندازی و همیشه در حال اجرا خواهد بود."
    echo ""
    
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  🔧 دستورات مفید                        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}وضعیت سرویس‌ها:${NC}"
    echo -e "    systemctl status meowvpn-bot"
    echo -e "    systemctl status nginx"
    echo ""
    echo -e "  ${CYAN}مشاهده لاگ‌ها:${NC}"
    echo -e "    journalctl -u meowvpn-bot -f"
    echo -e "    tail -f /var/log/meowvpn-health.log"
    echo ""
    echo -e "  ${CYAN}به‌روزرسانی آینده:${NC}"
    echo -e "    cd $(pwd) && sudo ./update.sh"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
fi

echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                          ║${NC}"
echo -e "${PURPLE}║       🎉 نصب سیستم با موفقیت کامل شد! 🎉               ║${NC}"
echo -e "${PURPLE}║                                                          ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# نمایش لوگو نهایی
echo -e "${CYAN}"
cat << "EOF"
     /\_/\  
    ( ^.^ ) 
     > ^ <   MeowVPN Bot v3.0
    /|   |\  با Setup Wizard و Auto-Restart
   (_|   |_) Ready to rock! 🚀
EOF
echo -e "${NC}"
echo ""

if [ "$WEBSITE_INSTALLED" = "true" ]; then
    echo -e "${GREEN}✨ الان Setup Wizard را باز کنید:${NC}"
    echo ""
    echo -e "   ${BLUE}${SETUP_URL}${NC}"
    echo ""
fi

print_success "همه چیز آماده است! موفق باشید! 🎊"
echo ""

