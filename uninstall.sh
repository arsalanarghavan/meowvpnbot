#!/bin/bash

# ==========================================
# MeowVPN Bot - Complete Uninstaller
# حذف کامل ربات و وب سایت
# ==========================================

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# توابع
print_header() {
    echo -e "${RED}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║           ⚠️  UNINSTALL - حذف کامل  ⚠️          ║"
    echo "║                                                   ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# شروع
print_header

echo -e "${RED}این اسکریپت همه چیز را حذف می‌کند:${NC}"
echo "  • ربات تلگرام"
echo "  • پنل وب مدیریت"
echo "  • Systemd services"
echo "  • Nginx configuration"
echo "  • دیتابیس (اختیاری)"
echo ""
echo -e "${YELLOW}⚠️  این عملیات غیرقابل برگشت است!${NC}"
echo ""

read -p "آیا مطمئن هستید؟ (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "لغو شد."
    exit 0
fi

echo ""
print_warning "شروع فرآیند حذف..."
echo ""

# 1. پشتیبان‌گیری
echo -e "${PURPLE}═══ پشتیبان‌گیری ═══${NC}"
echo ""

read -p "آیا می‌خواهید از دیتابیس بکاپ بگیرید؟ (y/n): " BACKUP_DB

if [[ $BACKUP_DB =~ ^[Yy]$ ]]; then
    BACKUP_DIR="$HOME/meowvpn_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "/var/www/meowvpnbot/bot.db" ]; then
        cp /var/www/meowvpnbot/bot.db "$BACKUP_DIR/"
        print_success "دیتابیس: $BACKUP_DIR/bot.db"
    fi
    
    if [ -f "/var/www/meowvpnbot/.env" ]; then
        cp /var/www/meowvpnbot/.env "$BACKUP_DIR/bot.env"
        print_success "تنظیمات ربات: $BACKUP_DIR/bot.env"
    fi
    
    if [ -f "/var/www/meowvpnbot/site/.env" ]; then
        cp /var/www/meowvpnbot/site/.env "$BACKUP_DIR/site.env"
        print_success "تنظیمات سایت: $BACKUP_DIR/site.env"
    fi
    
    echo ""
    print_info "بکاپ در: $BACKUP_DIR"
fi

echo ""

# 2. متوقف کردن سرویس‌ها
echo -e "${PURPLE}═══ متوقف کردن سرویس‌ها ═══${NC}"
echo ""

if systemctl is-active --quiet meowvpn-bot; then
    sudo systemctl stop meowvpn-bot
    print_success "ربات متوقف شد"
else
    print_info "ربات در حال اجرا نبود"
fi

# 3. حذف Systemd service
if [ -f "/etc/systemd/system/meowvpn-bot.service" ]; then
    sudo systemctl disable meowvpn-bot 2>/dev/null
    sudo rm /etc/systemd/system/meowvpn-bot.service
    sudo systemctl daemon-reload
    print_success "Systemd service حذف شد"
fi

echo ""

# 4. حذف Nginx configuration
echo -e "${PURPLE}═══ حذف Nginx Configuration ═══${NC}"
echo ""

# پیدا کردن تمام config های مربوطه
NGINX_CONFIGS=$(find /etc/nginx/sites-available/ -name "*meow*" -o -name "*dashboard*" 2>/dev/null)

if [ -n "$NGINX_CONFIGS" ]; then
    echo "Config های یافت شده:"
    echo "$NGINX_CONFIGS"
    echo ""
    
    for config in $NGINX_CONFIGS; do
        config_name=$(basename "$config")
        sudo rm -f "/etc/nginx/sites-enabled/$config_name"
        sudo rm -f "/etc/nginx/sites-available/$config_name"
        print_success "حذف: $config_name"
    done
    
    # تست و reload nginx
    if sudo nginx -t 2>/dev/null; then
        sudo systemctl reload nginx
        print_success "Nginx reload شد"
    fi
else
    print_info "هیچ Nginx config یافت نشد"
fi

echo ""

# 5. حذف SSL certificates
echo -e "${PURPLE}═══ حذف SSL Certificates ═══${NC}"
echo ""

read -p "آیا می‌خواهید SSL certificates را هم حذف کنید؟ (y/n): " REMOVE_SSL

if [[ $REMOVE_SSL =~ ^[Yy]$ ]]; then
    CERT_DIRS=$(find /etc/letsencrypt/live/ -name "*meow*" -o -name "*dashboard*" 2>/dev/null)
    
    if [ -n "$CERT_DIRS" ]; then
        for cert_dir in $CERT_DIRS; do
            domain=$(basename "$cert_dir")
            sudo certbot delete --cert-name "$domain" --non-interactive 2>/dev/null
            print_success "حذف SSL: $domain"
        done
    else
        print_info "هیچ SSL certificate یافت نشد"
    fi
fi

echo ""

# 6. حذف فایل‌های پروژه
echo -e "${PURPLE}═══ حذف فایل‌های پروژه ═══${NC}"
echo ""

# حذف از /var/www
if [ -d "/var/www/meowvpnbot" ]; then
    sudo rm -rf /var/www/meowvpnbot
    print_success "حذف: /var/www/meowvpnbot"
fi

# حذف از /root (اگر وجود داشت)
if [ -d "/root/meowvpnbot" ]; then
    read -p "آیا می‌خواهید /root/meowvpnbot را هم حذف کنید؟ (y/n): " REMOVE_ROOT
    if [[ $REMOVE_ROOT =~ ^[Yy]$ ]]; then
        sudo rm -rf /root/meowvpnbot
        print_success "حذف: /root/meowvpnbot"
    fi
fi

echo ""

# 7. حذف cron jobs
echo -e "${PURPLE}═══ حذف Cron Jobs ═══${NC}"
echo ""

CRON_BACKUP="/tmp/cron_backup_$(date +%Y%m%d_%H%M%S)"
crontab -l > "$CRON_BACKUP" 2>/dev/null

if grep -q "meowvpn" "$CRON_BACKUP" 2>/dev/null; then
    grep -v "meowvpn" "$CRON_BACKUP" | crontab -
    print_success "Cron jobs حذف شدند"
else
    print_info "هیچ cron job یافت نشد"
fi

rm -f "$CRON_BACKUP"

echo ""

# 8. حذف لاگ‌ها
echo -e "${PURPLE}═══ حذف Log Files ═══${NC}"
echo ""

read -p "آیا می‌خواهید log files را هم حذف کنید؟ (y/n): " REMOVE_LOGS

if [[ $REMOVE_LOGS =~ ^[Yy]$ ]]; then
    sudo rm -f /var/log/nginx/*meow* 2>/dev/null
    sudo rm -f /var/log/nginx/*dashboard* 2>/dev/null
    sudo rm -f /var/log/meowvpn* 2>/dev/null
    print_success "Log files حذف شدند"
fi

echo ""

# 9. پاک کردن user/group (اختیاری)
echo -e "${PURPLE}═══ تمیزکاری نهایی ═══${NC}"
echo ""

# پاک کردن cache های PHP
if command -v php &> /dev/null; then
    sudo systemctl restart php8.2-fpm 2>/dev/null || sudo systemctl restart php-fpm 2>/dev/null
    print_success "PHP-FPM cache پاک شد"
fi

echo ""

# خلاصه
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}║            ✅ حذف با موفقیت انجام شد            ║${NC}"
echo -e "${GREEN}║                                                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

if [ -n "$BACKUP_DIR" ]; then
    echo -e "${BLUE}📦 بکاپ شما:${NC}"
    echo "   $BACKUP_DIR"
    echo ""
fi

echo -e "${YELLOW}چیزهایی که حذف شد:${NC}"
echo "  ✓ ربات تلگرام و فایل‌ها"
echo "  ✓ پنل وب مدیریت"
echo "  ✓ Systemd services"
echo "  ✓ Nginx configuration"
if [[ $REMOVE_SSL =~ ^[Yy]$ ]]; then
    echo "  ✓ SSL certificates"
fi
if [[ $REMOVE_LOGS =~ ^[Yy]$ ]]; then
    echo "  ✓ Log files"
fi
echo ""

echo -e "${BLUE}چیزهایی که باقی ماندند:${NC}"
echo "  • Python (سیستمی)"
echo "  • PHP (سیستمی)"
echo "  • Nginx (سرویس)"
echo "  • Composer (سیستمی)"
echo ""

echo -e "${GREEN}برای نصب مجدد:${NC}"
echo "  git clone https://github.com/yourusername/meowvpnbot.git"
echo "  cd meowvpnbot"
echo "  sudo ./install.sh"
echo ""

print_success "تمام! 🎉"

