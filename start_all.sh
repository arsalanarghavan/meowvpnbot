#!/bin/bash

##############################################
# MeowVPN - Start All Services
# راه‌اندازی ربات و پنل وب
##############################################

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   🚀 MeowVPN - Starting Services      ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${YELLOW}[1/2]${NC} راه‌اندازی ربات تلگرام..."
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
    nohup python main.py > bot.log 2>&1 &
    BOT_PID=$!
    echo -e "${GREEN}✓ ربات شروع شد (PID: $BOT_PID)${NC}"
    echo -e "  لاگ: tail -f bot.log"
else
    echo -e "${YELLOW}⚠ Virtual environment یافت نشد${NC}"
fi

echo ""
echo -e "${YELLOW}[2/2]${NC} راه‌اندازی پنل وب..."
cd "$SCRIPT_DIR/site"

if [ -f "artisan" ]; then
    echo -e "${GREEN}✓ پنل وب در حال اجرا...${NC}"
    echo -e "${BLUE}📍 آدرس: http://localhost:8000${NC}"
    echo -e "${BLUE}👤 ادمین: admin / admin123${NC}"
    echo -e "${BLUE}👤 بازاریاب: marketer / marketer123${NC}"
    echo ""
    echo -e "${YELLOW}⏹️  برای توقف: Ctrl+C${NC}"
    echo ""
    php artisan serve --host=0.0.0.0 --port=8000
else
    echo -e "${YELLOW}⚠ پنل وب یافت نشد${NC}"
fi

