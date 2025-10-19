#!/bin/bash

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  تست Virtual Environment${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# 1. نصب python3-venv
echo -e "${YELLOW}▶ نصب python3-venv...${NC}"
sudo apt update -qq
sudo apt install -y python3-venv python3-full python3-dev
echo -e "${GREEN}✓ نصب شد${NC}"
echo ""

# 2. حذف venv قدیمی
if [ -d "venv" ]; then
    echo -e "${YELLOW}▶ حذف venv قدیمی...${NC}"
    rm -rf venv
    echo -e "${GREEN}✓ حذف شد${NC}"
    echo ""
fi

# 3. ساخت venv جدید
echo -e "${YELLOW}▶ ساخت venv جدید...${NC}"
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ venv ساخته شد${NC}"
else
    echo -e "${RED}✗ خطا در ساخت venv${NC}"
    exit 1
fi
echo ""

# 4. چک فایل‌های venv
echo -e "${YELLOW}▶ چک فایل‌های venv...${NC}"
ls -lh venv/bin/ | head -15
echo ""

# 5. یافتن python
if [ -f "venv/bin/python3" ]; then
    PYTHON_EXE="venv/bin/python3"
    echo -e "${GREEN}✓ Python3 یافت شد: $PYTHON_EXE${NC}"
elif [ -f "venv/bin/python" ]; then
    PYTHON_EXE="venv/bin/python"
    echo -e "${GREEN}✓ Python یافت شد: $PYTHON_EXE${NC}"
else
    echo -e "${RED}✗ Python در venv یافت نشد!${NC}"
    exit 1
fi
echo ""

# 6. تست python
echo -e "${YELLOW}▶ تست python...${NC}"
$PYTHON_EXE --version
echo -e "${GREEN}✓ Python کار می‌کنه${NC}"
echo ""

# 7. تست pip
echo -e "${YELLOW}▶ تست pip...${NC}"
$PYTHON_EXE -m pip --version
echo -e "${GREEN}✓ pip کار می‌کنه${NC}"
echo ""

# 8. ارتقا pip
echo -e "${YELLOW}▶ ارتقا pip...${NC}"
$PYTHON_EXE -m pip install --upgrade pip setuptools wheel -q
echo -e "${GREEN}✓ pip ارتقا یافت${NC}"
echo ""

# 9. نصب یک package تست
echo -e "${YELLOW}▶ تست نصب package (requests)...${NC}"
$PYTHON_EXE -m pip install requests -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ نصب موفق بود${NC}"
else
    echo -e "${RED}✗ خطا در نصب${NC}"
    exit 1
fi
echo ""

# 10. تست import
echo -e "${YELLOW}▶ تست import...${NC}"
$PYTHON_EXE -c "import requests; print('requests version:', requests.__version__)"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Import موفق بود${NC}"
else
    echo -e "${RED}✗ خطا در import${NC}"
    exit 1
fi
echo ""

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ همه تست‌ها موفق بود!${NC}"
echo -e "${GREEN}  venv کاملاً سالم است!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}حالا می‌تونی install.sh رو اجرا کنی:${NC}"
echo -e "  sudo ./install.sh"

