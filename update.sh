#!/bin/bash
# به‌روزرسانی خودکار
set -e

# تشخیص مسیر پروژه
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# اگر در /root هستیم، مسیر را به /var/www تغییر بده
if [[ "$PROJECT_ROOT" == /root/* ]]; then
    if [ -d "/var/www/meowvpnbot" ]; then
        PROJECT_ROOT="/var/www/meowvpnbot"
        cd "$PROJECT_ROOT"
        print_info "استفاده از مسیر: $PROJECT_ROOT"
    fi
fi

SITE_DIR="$PROJECT_ROOT/site"

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# توابع
print_header() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║                                                   ║"
    echo "║    🔄 MeowVPN Bot + Website Updater 🔄          ║"
    echo "║       به‌روزرسانی ربات و پنل وب                 ║"
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

# شروع
print_header

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
SITE_DIR="$PROJECT_ROOT/site"

echo -e "${CYAN}"
echo "این اسکریپت موارد زیر را انجام می‌دهد:"
echo "  1. پشتیبان‌گیری از دیتابیس"
echo "  2. دریافت آخرین تغییرات (git pull)"
echo "  3. به‌روزرسانی dependencies (Bot & Website)"
echo "  4. اجرای migrations جدید"
echo "  5. ریستارت ربات و پنل وب"
echo ""
echo -e "${NC}"

read -p "آیا می‌خواهید ادامه دهید؟ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "به‌روزرسانی لغو شد."
    exit 1
fi

# بررسی وجود ربات در حال اجرا
print_step "بررسی وضعیت ربات..."
BOT_RUNNING=false
if systemctl is-active --quiet meowvpn-bot.service 2>/dev/null; then
    BOT_RUNNING=true
    print_info "ربات در حال اجرا با systemd است"
elif pgrep -f "python.*main.py" > /dev/null; then
    BOT_RUNNING=true
    print_info "ربات در حال اجرا است"
else
    print_info "ربات در حال اجرا نیست"
fi

# توقف ربات
if [ "$BOT_RUNNING" = true ]; then
    print_step "توقف ربات..."
    if systemctl is-active --quiet meowvpn-bot.service 2>/dev/null; then
        sudo systemctl stop meowvpn-bot
        print_success "ربات متوقف شد (systemd)"
    else
        pkill -f "python.*main.py" || true
        sleep 2
        print_success "ربات متوقف شد"
    fi
fi

# پشتیبان‌گیری از دیتابیس
print_step "پشتیبان‌گیری از دیتابیس..."

BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# تشخیص نوع دیتابیس از .env
if [ -f ".env" ]; then
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2-)
    
    if [[ $DB_URL == sqlite* ]]; then
        # SQLite backup
        DB_FILE=$(echo $DB_URL | sed 's/sqlite:\/\/\///')
        if [ -f "$DB_FILE" ]; then
            cp "$DB_FILE" "$BACKUP_DIR/backup_${BACKUP_DATE}.db"
            print_success "پشتیبان SQLite ایجاد شد: $BACKUP_DIR/backup_${BACKUP_DATE}.db"
        fi
    elif [[ $DB_URL == postgresql* ]]; then
        # PostgreSQL backup
        print_info "برای PostgreSQL، لطفاً دستی پشتیبان‌گیری کنید:"
        echo "  pg_dump dbname > $BACKUP_DIR/backup_${BACKUP_DATE}.sql"
    fi
else
    print_warning "فایل .env یافت نشد - پشتیبان‌گیری انجام نشد"
fi

# دریافت آخرین تغییرات
print_step "دریافت آخرین تغییرات از Git..."
if [ -d ".git" ]; then
    if [[ -n $(git status -s) ]]; then
        git stash
    fi
    git pull origin main || git pull origin master
    if git stash list | grep -q "stash@{0}"; then
        git stash pop || true
    fi
    print_success "آخرین نسخه دریافت شد"
else
    print_warning "Git repository یافت نشد"
fi

# فعال‌سازی virtual environment (اگر غیرفعال شده)
if [ -d "venv" ]; then
    print_step "فعال‌سازی virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment فعال شد"
fi

# به‌روزرسانی dependencies
print_step "به‌روزرسانی dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install --upgrade -r requirements.txt
print_success "Dependencies به‌روزرسانی شدند"

# اجرای migrations جدید
print_step "اجرای migrations جدید..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
    print_success "Migrations اجرا شدند"
else
    print_warning "Alembic یافت نشد"
fi

# پاک‌سازی فایل‌های cache
print_step "پاک‌سازی cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
print_success "Cache پاک شد"

# به‌روزرسانی پنل وب
echo ""
if [ -d "$SITE_DIR" ] && command -v composer &> /dev/null; then
    print_step "به‌روزرسانی پنل وب..."
    cd "$SITE_DIR"
    
    composer install --optimize-autoloader --no-interaction
    print_success "Dependencies پنل وب به‌روزرسانی شد"
    
    php artisan config:clear
    php artisan cache:clear
    php artisan view:clear
    php artisan route:clear
    print_success "Cache پنل وب پاک شد"
    
    cd "$PROJECT_ROOT"
else
    print_warning "پنل وب یافت نشد یا Composer نصب نیست"
fi

# راه‌اندازی مجدد ربات
print_step "راه‌اندازی ربات..."
if systemctl list-unit-files | grep -q "meowvpn-bot.service"; then
    sudo systemctl restart meowvpn-bot
    sleep 2
    systemctl is-active --quiet meowvpn-bot && print_success "ربات راه‌اندازی شد" || print_warning "ربات راه‌اندازی نشد"
else
    cd "$PROJECT_ROOT"
    source venv/bin/activate 2>/dev/null || true
    nohup python main.py > bot.log 2>&1 &
    sleep 2
    pgrep -f "python.*main.py" > /dev/null && print_success "ربات راه‌اندازی شد" || print_warning "ربات راه‌اندازی نشد"
fi

# Reset Setup Wizard اگر لازم باشه
if [ -f "$SITE_DIR/.env" ]; then
    SITE_ENV="$SITE_DIR/.env"
    if grep -q "SETUP_WIZARD_ENABLED=false" "$SITE_ENV" && grep -q "BOT_INSTALLED=false" "$SITE_ENV"; then
        print_info "Reset Setup Wizard..."
        sed -i 's/SETUP_WIZARD_ENABLED=false/SETUP_WIZARD_ENABLED=true/g' "$SITE_ENV" || true
        cd "$SITE_DIR"
        php artisan config:clear 2>/dev/null || true
        php artisan cache:clear 2>/dev/null || true
    fi
fi

echo ""
print_success "✅ به‌روزرسانی کامل شد!"

