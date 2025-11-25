#!/bin/bash

# ==========================================
# Fresh Install - پاک کردن کامل و نصب مجدد
# ==========================================

set -e

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║        🔄 Fresh Install - نصب مجدد کامل 🔄       ║"
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

print_header

echo -e "${RED}این اسکریپت:${NC}"
echo "  1. همه چیز را پاک می‌کند (ربات، سایت، سرویس‌ها)"
echo "  2. از GitHub دوباره clone می‌کند"
echo "  3. نصب کامل انجام می‌دهد"
echo ""
echo -e "${YELLOW}⚠️  این عملیات غیرقابل برگشت است!${NC}"
echo ""

read -p "آیا مطمئن هستید؟ (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "لغو شد."
    exit 0
fi

echo ""
print_warning "شروع فرآیند پاک‌سازی و نصب مجدد..."
echo ""

# تشخیص مسیر پروژه
if [ -d "/var/www/meowvpnbot" ]; then
    PROJECT_DIR="/var/www/meowvpnbot"
elif [ -d "/root/meowvpnbot" ]; then
    PROJECT_DIR="/root/meowvpnbot"
else
    print_error "پروژه یافت نشد!"
    exit 1
fi

print_info "مسیر پروژه: $PROJECT_DIR"

# 1. بکاپ از دیتابیس
echo ""
echo -e "${PURPLE}═══ پشتیبان‌گیری ═══${NC}"
echo ""

BACKUP_DIR="$HOME/meowvpn_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$PROJECT_DIR/vpn_bot.db" ]; then
    cp "$PROJECT_DIR/vpn_bot.db" "$BACKUP_DIR/vpn_bot.db"
    print_success "بکاپ دیتابیس: $BACKUP_DIR/vpn_bot.db"
fi

if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$BACKUP_DIR/bot.env"
    print_success "بکاپ تنظیمات ربات: $BACKUP_DIR/bot.env"
fi

if [ -f "$PROJECT_DIR/site/.env" ]; then
    cp "$PROJECT_DIR/site/.env" "$BACKUP_DIR/site.env"
    print_success "بکاپ تنظیمات سایت: $BACKUP_DIR/site.env"
fi

print_info "بکاپ در: $BACKUP_DIR"
echo ""

# 2. متوقف کردن سرویس‌ها
echo -e "${PURPLE}═══ متوقف کردن سرویس‌ها ═══${NC}"
echo ""

if systemctl is-active --quiet meowvpn-bot 2>/dev/null; then
    sudo systemctl stop meowvpn-bot
    print_success "ربات متوقف شد"
fi

# 3. حذف Systemd service
if [ -f "/etc/systemd/system/meowvpn-bot.service" ]; then
    sudo systemctl disable meowvpn-bot 2>/dev/null
    sudo rm -f /etc/systemd/system/meowvpn-bot.service
    sudo systemctl daemon-reload
    print_success "Systemd service حذف شد"
fi

# 4. حذف Nginx configs
echo ""
echo -e "${PURPLE}═══ حذف Nginx Configuration ═══${NC}"
echo ""

NGINX_CONFIGS=$(find /etc/nginx/sites-available/ -name "*meow*" -o -name "*dashboard*" 2>/dev/null || true)

if [ -n "$NGINX_CONFIGS" ]; then
    for config in $NGINX_CONFIGS; do
        config_name=$(basename "$config")
        sudo rm -f "/etc/nginx/sites-enabled/$config_name"
        sudo rm -f "/etc/nginx/sites-available/$config_name"
        print_success "حذف: $config_name"
    done
    
    if sudo nginx -t 2>/dev/null; then
        sudo systemctl reload nginx
    fi
fi

# 5. حذف فایل‌های پروژه
echo ""
echo -e "${PURPLE}═══ حذف فایل‌های پروژه ═══${NC}"
echo ""

if [ -d "$PROJECT_DIR" ]; then
    sudo rm -rf "$PROJECT_DIR"
    print_success "حذف: $PROJECT_DIR"
fi

# 6. Clone مجدد
echo ""
echo -e "${PURPLE}═══ Clone از GitHub ═══${NC}"
echo ""

# تشخیص مسیر مناسب برای clone
if [ "$PROJECT_DIR" == "/var/www/meowvpnbot" ]; then
    NEW_PROJECT_DIR="/var/www/meowvpnbot"
    sudo mkdir -p /var/www
    cd /var/www
    sudo git clone https://github.com/arsalanarghavan/meowvpnbot.git
    sudo chown -R $USER:$USER meowvpnbot
    cd meowvpnbot
else
    cd /root
    git clone https://github.com/arsalanarghavan/meowvpnbot.git
    cd meowvpnbot
fi

print_success "Clone انجام شد"
echo ""

# 7. نصب
echo -e "${PURPLE}═══ شروع نصب ═══${NC}"
echo ""

print_info "اجرای install.sh..."
sudo ./install.sh

echo ""
print_success "╔═══════════════════════════════════════════════════╗"
print_success "║                                                   ║"
print_success "║         ✅ نصب مجدد با موفقیت انجام شد          ║"
print_success "║                                                   ║"
print_success "╚═══════════════════════════════════════════════════╝"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    print_info "📦 بکاپ شما در: $BACKUP_DIR"
    echo ""
    print_info "اگر می‌خواهید دیتابیس قدیمی را restore کنید:"
    echo "  cp $BACKUP_DIR/vpn_bot.db $(pwd)/vpn_bot.db"
    echo ""
fi

print_success "تمام! 🎉"

