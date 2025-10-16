#!/bin/bash

# ==========================================
# MeowVPN Bot - Automatic Installer
# نصب خودکار ربات MeowVPN
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

# توابع کمکی
print_header() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║         🐱 MeowVPN Bot Installer 🐱             ║"
    echo "║              نصب خودکار ربات                    ║"
    echo "║                                                   ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
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
echo "این اسکریپت موارد زیر را نصب می‌کند:"
echo "  • Python dependencies"
echo "  • Database setup"
echo "  • Configuration files"
echo "  • Systemd service (optional)"
echo ""
echo -e "${NC}"

read -p "آیا می‌خواهید ادامه دهید؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "نصب لغو شد."
    exit 1
fi

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

print_info "📋 مراحل بعدی:"
echo "  1. فایل .env را ویرایش کنید (اگر هنوز نکرده‌اید):"
echo "     ${CYAN}nano .env${NC}"
echo ""
echo "  2. ربات را اجرا کنید:"
echo "     ${CYAN}source venv/bin/activate${NC}"
echo "     ${CYAN}python main.py${NC}"
echo ""
echo "     یا با systemd:"
echo "     ${CYAN}sudo systemctl start meowvpnbot${NC}"
echo ""
echo "  3. مستندات را بخوانید:"
echo "     ${CYAN}cat START_HERE.md${NC}"
echo ""

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

