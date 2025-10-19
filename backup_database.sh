#!/bin/bash

###############################################################################
# اسکریپت بکاپ دیتابیس
# این اسکریپت قبل از مایگریشن از دیتابیس بکاپ می‌گیرد
###############################################################################

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🔒 بکاپ دیتابیس MeowVPN Bot 🔒                  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# مشخص کردن نوع دیتابیس
echo -e "${YELLOW}نوع دیتابیس خود را انتخاب کنید:${NC}"
echo "  1) SQLite"
echo "  2) MySQL/MariaDB"
echo "  3) PostgreSQL"
echo ""
read -p "انتخاب (1-3): " db_type

# دایرکتوری بکاپ
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ایجاد دایرکتوری بکاپ اگر وجود نداشت
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    echo -e "${GREEN}✅ دایرکتوری بکاپ ساخته شد${NC}"
fi

case $db_type in
    1)
        # SQLite Backup
        echo -e "\n${BLUE}📂 بکاپ از SQLite...${NC}"
        
        # پیدا کردن فایل دیتابیس
        if [ -f "bot_database.db" ]; then
            DB_FILE="bot_database.db"
        elif [ -f "database.db" ]; then
            DB_FILE="database.db"
        else
            echo -e "${RED}❌ فایل دیتابیس یافت نشد!${NC}"
            echo -e "${YELLOW}لطفاً نام فایل دیتابیس را وارد کنید:${NC}"
            read -p "نام فایل: " DB_FILE
            
            if [ ! -f "$DB_FILE" ]; then
                echo -e "${RED}❌ فایل $DB_FILE یافت نشد!${NC}"
                exit 1
            fi
        fi
        
        BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.db"
        
        # کپی فایل دیتابیس
        cp "$DB_FILE" "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            # فشرده‌سازی بکاپ
            gzip "$BACKUP_FILE"
            
            BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
            echo -e "${GREEN}✅ بکاپ با موفقیت انجام شد${NC}"
            echo -e "${GREEN}   فایل: ${BACKUP_FILE}.gz${NC}"
            echo -e "${GREEN}   حجم: ${BACKUP_SIZE}${NC}"
        else
            echo -e "${RED}❌ خطا در ایجاد بکاپ${NC}"
            exit 1
        fi
        ;;
        
    2)
        # MySQL Backup
        echo -e "\n${BLUE}📂 بکاپ از MySQL/MariaDB...${NC}"
        
        read -p "نام دیتابیس: " DB_NAME
        read -p "نام کاربری: " DB_USER
        read -sp "رمز عبور: " DB_PASS
        echo ""
        read -p "هاست (پیش‌فرض: localhost): " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
        
        BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"
        
        # بکاپ با mysqldump
        mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            # فشرده‌سازی بکاپ
            gzip "$BACKUP_FILE"
            
            BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
            echo -e "${GREEN}✅ بکاپ با موفقیت انجام شد${NC}"
            echo -e "${GREEN}   فایل: ${BACKUP_FILE}.gz${NC}"
            echo -e "${GREEN}   حجم: ${BACKUP_SIZE}${NC}"
        else
            echo -e "${RED}❌ خطا در ایجاد بکاپ${NC}"
            exit 1
        fi
        ;;
        
    3)
        # PostgreSQL Backup
        echo -e "\n${BLUE}📂 بکاپ از PostgreSQL...${NC}"
        
        read -p "نام دیتابیس: " DB_NAME
        read -p "نام کاربری: " DB_USER
        read -p "هاست (پیش‌فرض: localhost): " DB_HOST
        DB_HOST=${DB_HOST:-localhost}
        read -p "پورت (پیش‌فرض: 5432): " DB_PORT
        DB_PORT=${DB_PORT:-5432}
        
        BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"
        
        # بکاپ با pg_dump
        PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            # فشرده‌سازی بکاپ
            gzip "$BACKUP_FILE"
            
            BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
            echo -e "${GREEN}✅ بکاپ با موفقیت انجام شد${NC}"
            echo -e "${GREEN}   فایل: ${BACKUP_FILE}.gz${NC}"
            echo -e "${GREEN}   حجم: ${BACKUP_SIZE}${NC}"
        else
            echo -e "${RED}❌ خطا در ایجاد بکاپ${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}❌ انتخاب نامعتبر${NC}"
        exit 1
        ;;
esac

# نمایش لیست بکاپ‌ها
echo -e "\n${BLUE}📚 لیست بکاپ‌ها:${NC}"
ls -lh "$BACKUP_DIR"

echo -e "\n${GREEN}💡 نکته: این بکاپ را در مکان امنی ذخیره کنید${NC}"
echo -e "${YELLOW}⚠️  قبل از اجرای مایگریشن، حتماً از موفقیت بکاپ اطمینان حاصل کنید${NC}"
echo ""

