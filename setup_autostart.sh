#!/bin/bash

##############################################
# MeowVPN - Auto-Restart & Monitoring Setup
# راه‌اندازی خودکار و بازیابی خودکار
##############################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    MeowVPN - Auto-Restart & Monitoring Setup            ║${NC}"
echo -e "${BLUE}║         نصب سیستم بازیابی خودکار                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# بررسی root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}لطفاً با sudo اجرا کنید${NC}"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo -e "${YELLOW}[1/5]${NC} نصب Supervisor..."

# نصب Supervisor
if ! command -v supervisorctl &> /dev/null; then
    apt update
    apt install -y supervisor
    echo -e "${GREEN}✓ Supervisor نصب شد${NC}"
else
    echo -e "${GREEN}✓ Supervisor موجود است${NC}"
fi

echo -e "${YELLOW}[2/5]${NC} ایجاد Systemd Service برای ربات..."

# Systemd Service برای ربات
cat > /etc/systemd/system/meowvpn-bot.service << EOF
[Unit]
Description=MeowVPN Telegram Bot
After=network.target
Documentation=https://github.com/yourusername/meowvpnbot

[Service]
Type=simple
User=www-data
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$PROJECT_ROOT/venv/bin"
ExecStart=$PROJECT_ROOT/venv/bin/python main.py

# Auto-restart settings
Restart=always
RestartSec=10
StartLimitInterval=0

# Logging
StandardOutput=append:/var/log/meowvpn-bot.log
StandardError=append:/var/log/meowvpn-bot-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Systemd service ایجاد شد${NC}"

echo -e "${YELLOW}[3/5]${NC} ایجاد Supervisor Config برای پنل وب..."

# Supervisor برای Laravel Queue Worker (اختیاری)
cat > /etc/supervisor/conf.d/meowvpn-panel.conf << EOF
[program:meowvpn-panel]
process_name=%(program_name)s_%(process_num)02d
command=php $PROJECT_ROOT/site/artisan serve --host=127.0.0.1 --port=8000
autostart=false
autorestart=false
user=www-data
numprocs=1
redirect_stderr=true
stdout_logfile=/var/log/supervisor/meowvpn-panel.log
stopwaitsecs=3600
EOF

echo -e "${GREEN}✓ Supervisor config ایجاد شد${NC}"

echo -e "${YELLOW}[4/5]${NC} ایجاد Health Check Script..."

# اسکریپت بررسی سلامت
cat > $PROJECT_ROOT/health_check.sh << 'HEALTHEOF'
#!/bin/bash

# Health Check Script
LOG_FILE="/var/log/meowvpn-health.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# بررسی ربات
if ! systemctl is-active --quiet meowvpn-bot.service; then
    log_message "⚠️  ربات متوقف شده - در حال ریستارت..."
    systemctl restart meowvpn-bot.service
    log_message "✓ ربات ریستارت شد"
fi

# بررسی Nginx
if ! systemctl is-active --quiet nginx; then
    log_message "⚠️  Nginx متوقف شده - در حال ریستارت..."
    systemctl restart nginx
    log_message "✓ Nginx ریستارت شد"
fi

# بررسی PHP-FPM
if ! systemctl is-active --quiet php8.1-fpm; then
    log_message "⚠️  PHP-FPM متوقف شده - در حال ریستارت..."
    systemctl restart php8.1-fpm
    log_message "✓ PHP-FPM ریستارت شد"
fi

# بررسی دیسک
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log_message "⚠️  فضای دیسک کم است: ${DISK_USAGE}%"
fi

# بررسی RAM
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEM_USAGE" -gt 90 ]; then
    log_message "⚠️  مصرف RAM بالاست: ${MEM_USAGE}%"
fi

log_message "✓ Health check انجام شد"
HEALTHEOF

chmod +x $PROJECT_ROOT/health_check.sh

echo -e "${GREEN}✓ Health check script ایجاد شد${NC}"

echo -e "${YELLOW}[5/5]${NC} تنظیم Cron Job برای Health Check..."

# اضافه کردن به crontab
CRON_CMD="*/5 * * * * $PROJECT_ROOT/health_check.sh"

# بررسی وجود
if ! crontab -l 2>/dev/null | grep -q "health_check.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo -e "${GREEN}✓ Cron job اضافه شد (هر 5 دقیقه)${NC}"
else
    echo -e "${GREEN}✓ Cron job از قبل موجود است${NC}"
fi

# فعال‌سازی و شروع سرویس‌ها
echo ""
echo -e "${YELLOW}راه‌اندازی سرویس‌ها...${NC}"

systemctl daemon-reload
systemctl enable meowvpn-bot.service
systemctl start meowvpn-bot.service

supervisorctl reread
supervisorctl update

echo -e "${GREEN}✓ سرویس‌ها راه‌اندازی شدند${NC}"

# نمایش وضعیت
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ سیستم Auto-Restart نصب شد!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📊 وضعیت سرویس‌ها:${NC}"
echo ""

# ربات
if systemctl is-active --quiet meowvpn-bot.service; then
    echo -e "  🤖 ربات تلگرام: ${GREEN}✓ Running${NC}"
else
    echo -e "  🤖 ربات تلگرام: ${RED}✗ Stopped${NC}"
fi

# Nginx
if systemctl is-active --quiet nginx; then
    echo -e "  🌐 Nginx: ${GREEN}✓ Running${NC}"
else
    echo -e "  🌐 Nginx: ${RED}✗ Stopped${NC}"
fi

# PHP-FPM
if systemctl is-active --quiet php8.1-fpm; then
    echo -e "  🐘 PHP-FPM: ${GREEN}✓ Running${NC}"
else
    echo -e "  🐘 PHP-FPM: ${RED}✗ Stopped${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}📋 قابلیت‌های فعال شده:${NC}"
echo ""
echo "  ✅ Auto-restart اگر ربات کرش کرد"
echo "  ✅ Auto-restart اگر Nginx قطع شد"
echo "  ✅ Auto-restart اگر PHP-FPM مشکل داشت"
echo "  ✅ Health check هر 5 دقیقه یکبار"
echo "  ✅ Monitoring فضای دیسک"
echo "  ✅ Monitoring مصرف RAM"
echo "  ✅ Logging کامل"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}🔧 دستورات مفید:${NC}"
echo ""
echo "  • وضعیت ربات:     ${GREEN}systemctl status meowvpn-bot${NC}"
echo "  • ریستارت ربات:   ${GREEN}systemctl restart meowvpn-bot${NC}"
echo "  • لاگ ربات:        ${GREEN}journalctl -u meowvpn-bot -f${NC}"
echo ""
echo "  • لاگ Health Check: ${GREEN}tail -f /var/log/meowvpn-health.log${NC}"
echo "  • لاگ خطاها:       ${GREEN}tail -f /var/log/meowvpn-bot-error.log${NC}"
echo ""
echo "  • توقف موقت:       ${GREEN}systemctl stop meowvpn-bot${NC}"
echo "  • غیرفعال کردن:    ${GREEN}systemctl disable meowvpn-bot${NC}"
echo ""

echo -e "${GREEN}🎉 سیستم Auto-Restart آماده است!${NC}"
echo ""
echo -e "${YELLOW}💡 توصیه:${NC} این اسکریپت به صورت خودکار در install.sh اجرا می‌شود."
echo ""

