# 🎁 اسکریپت‌های جانبی مفید

## 🚀 اسکریپت‌های اضافه شده

### 1. Installer (install.sh) ⭐
نصب کامل با یک دستور!

```bash
bash install.sh
```

### 2. Updater (update.sh) ⭐
به‌روزرسانی با یک دستور!

```bash
bash update.sh
```

---

## 💡 اسکریپت‌های اضافی پیشنهادی

### 3. Backup Script

ایجاد کنید: `backup.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Backup Script

BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
if [ -f "meowvpn.db" ]; then
    cp meowvpn.db "$BACKUP_DIR/db_backup_$DATE.db"
    echo "✓ Database backup: $BACKUP_DIR/db_backup_$DATE.db"
fi

# Backup .env
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/env_backup_$DATE"
    echo "✓ .env backup: $BACKUP_DIR/env_backup_$DATE"
fi

# حذف backup های قدیمی (بیشتر از 30 روز)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "env_backup_*" -mtime +30 -delete

echo "✅ Backup کامل شد!"
```

**استفاده:**
```bash
chmod +x backup.sh
bash backup.sh
```

**Automation:**
```bash
# اضافه به crontab (روزانه ساعت 3 صبح)
0 3 * * * cd /path/to/meowvpnbot && bash backup.sh
```

---

### 4. Status Checker Script

ایجاد کنید: `status.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Status Checker

echo "🔍 بررسی وضعیت ربات..."
echo ""

# بررسی process
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ ربات در حال اجرا است"
    PID=$(pgrep -f "python.*main.py")
    echo "   PID: $PID"
    
    # Memory usage
    MEM=$(ps -p $PID -o rss= | awk '{print $1/1024}')
    echo "   حافظه: ${MEM}MB"
else
    echo "❌ ربات در حال اجرا نیست"
fi

echo ""

# بررسی systemd service
if systemctl is-active --quiet meowvpnbot.service 2>/dev/null; then
    echo "✅ Systemd service فعال است"
    systemctl status meowvpnbot.service --no-pager | head -5
else
    echo "ℹ Systemd service یافت نشد یا غیرفعال است"
fi

echo ""

# بررسی database
if [ -f "meowvpn.db" ]; then
    SIZE=$(du -h meowvpn.db | cut -f1)
    echo "✅ Database: $SIZE"
else
    echo "⚠ Database یافت نشد"
fi

echo ""

# بررسی .env
if [ -f ".env" ]; then
    echo "✅ فایل .env موجود است"
    
    # بررسی تنظیمات مهم
    if grep -q "^TELEGRAM_BOT_TOKEN=" .env; then
        echo "   ✓ BOT_TOKEN تنظیم شده"
    else
        echo "   ✗ BOT_TOKEN تنظیم نشده"
    fi
    
    if grep -q "^ADMIN_ID=" .env; then
        echo "   ✓ ADMIN_ID تنظیم شده"
    else
        echo "   ✗ ADMIN_ID تنظیم نشده"
    fi
else
    echo "❌ فایل .env یافت نشد!"
fi

echo ""

# نمایش آخرین خطاها (اگر وجود دارد)
if [ -f "bot.log" ]; then
    ERRORS=$(grep -i "error\|exception" bot.log | tail -3)
    if [ -n "$ERRORS" ]; then
        echo "⚠ آخرین خطاها:"
        echo "$ERRORS"
    else
        echo "✅ هیچ خطای اخیری یافت نشد"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ بررسی کامل شد"
```

**استفاده:**
```bash
chmod +x status.sh
bash status.sh
```

---

### 5. Quick Restart Script

ایجاد کنید: `restart.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Quick Restart

echo "🔄 در حال ریستارت ربات..."

if systemctl is-active --quiet meowvpnbot.service 2>/dev/null; then
    sudo systemctl restart meowvpnbot
    sleep 2
    
    if systemctl is-active --quiet meowvpnbot.service; then
        echo "✅ ربات ریستارت شد (systemd)"
        echo "📊 وضعیت:"
        sudo systemctl status meowvpnbot --no-pager | head -10
    else
        echo "❌ خطا در ریستارت!"
        sudo journalctl -u meowvpnbot -n 20
    fi
else
    # Manual restart
    echo "⏸ توقف..."
    pkill -f "python.*main.py" || true
    sleep 2
    
    echo "▶️ شروع..."
    source venv/bin/activate
    nohup python main.py > bot.log 2>&1 &
    sleep 3
    
    if pgrep -f "python.*main.py" > /dev/null; then
        echo "✅ ربات ریستارت شد"
        PID=$(pgrep -f "python.*main.py")
        echo "   PID: $PID"
    else
        echo "❌ خطا در ریستارت!"
        tail -20 bot.log
    fi
fi
```

**استفاده:**
```bash
chmod +x restart.sh
bash restart.sh
```

---

### 6. Logs Viewer Script

ایجاد کنید: `logs.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Logs Viewer

echo "📜 نمایش لاگ‌های ربات..."
echo ""

if systemctl is-active --quiet meowvpnbot.service 2>/dev/null; then
    echo "📊 لاگ‌های Systemd (Ctrl+C برای خروج):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sudo journalctl -u meowvpnbot -f
elif [ -f "bot.log" ]; then
    echo "📊 لاگ‌های فایل (Ctrl+C برای خروج):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    tail -f bot.log
else
    echo "❌ هیچ لاگی یافت نشد!"
    echo ""
    echo "💡 برای ایجاد لاگ:"
    echo "   python main.py > bot.log 2>&1"
fi
```

**استفاده:**
```bash
chmod +x logs.sh
bash logs.sh
```

---

### 7. Database Info Script

ایجاد کنید: `dbinfo.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Database Info

source venv/bin/activate

python << 'EOF'
from database.engine import SessionLocal
from database.models.user import User, UserRole
from database.models.service import Service
from database.models.transaction import Transaction
from database.models.card_account import CardAccount

db = SessionLocal()

print("📊 اطلاعات دیتابیس:")
print("━━━━━━━━━━━━━━━━━━━━━━━━")

# Users
total_users = db.query(User).count()
customers = db.query(User).filter(User.role == UserRole.customer).count()
marketers = db.query(User).filter(User.role == UserRole.marketer).count()
admins = db.query(User).filter(User.role == UserRole.admin).count()

print(f"👥 کاربران:")
print(f"   کل: {total_users}")
print(f"   مشتریان: {customers}")
print(f"   بازاریاب‌ها: {marketers}")
print(f"   ادمین‌ها: {admins}")
print()

# Services
active_services = db.query(Service).filter(Service.is_active == True).count()
total_services = db.query(Service).count()

print(f"🔧 سرویس‌ها:")
print(f"   فعال: {active_services}")
print(f"   کل: {total_services}")
print()

# Transactions
total_tx = db.query(Transaction).count()

print(f"💳 تراکنش‌ها:")
print(f"   کل: {total_tx}")
print()

# Cards
cards = db.query(CardAccount).all()
active_cards = db.query(CardAccount).filter(CardAccount.is_active == True).count()

print(f"💳 کارت‌های بانکی:")
print(f"   کل: {len(cards)}")
print(f"   فعال: {active_cards}")

if cards:
    print()
    print("   جزئیات:")
    for card in cards:
        status = "✅" if card.is_active else "❌"
        limit_text = "نامحدود" if card.daily_limit == 0 else f"{card.daily_limit:,}"
        print(f"   {status} #{card.priority} - {limit_text} - {card.current_amount:,} دریافتی")

db.close()

print()
print("✅ اطلاعات نمایش داده شد")
EOF
```

**استفاده:**
```bash
chmod +x dbinfo.sh
bash dbinfo.sh
```

---

## 🎯 استفاده ترکیبی

### Workflow توصیه شده:

```bash
# هر روز صبح
bash status.sh        # بررسی وضعیت

# هر هفته
bash update.sh        # به‌روزرسانی
bash backup.sh        # پشتیبان‌گیری

# در صورت مشکل
bash logs.sh          # بررسی لاگ‌ها
bash restart.sh       # ریستارت سریع

# برای بررسی آمار
bash dbinfo.sh        # اطلاعات دیتابیس
```

---

## 📦 All-in-One Management Script

ایجاد کنید: `manage.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Management Script

show_menu() {
    clear
    echo "╔═══════════════════════════════════════╗"
    echo "║    🐱 MeowVPN Bot Manager 🐱        ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    echo "  1) 🚀 شروع ربات"
    echo "  2) ⏸  توقف ربات"
    echo "  3) 🔄 ریستارت ربات"
    echo "  4) 📊 نمایش وضعیت"
    echo "  5) 📜 نمایش لاگ‌ها"
    echo "  6) 🔄 به‌روزرسانی"
    echo "  7) 💾 پشتیبان‌گیری"
    echo "  8) 📊 اطلاعات دیتابیس"
    echo "  9) ❌ خروج"
    echo ""
    echo -n "انتخاب کنید [1-9]: "
}

while true; do
    show_menu
    read choice
    
    case $choice in
        1) bash restart.sh ;;
        2) 
            if systemctl is-active --quiet meowvpnbot.service; then
                sudo systemctl stop meowvpnbot
            else
                pkill -f "python.*main.py"
            fi
            echo "✓ ربات متوقف شد"
            read -p "Enter برای ادامه..."
            ;;
        3) bash restart.sh; read -p "Enter برای ادامه..." ;;
        4) bash status.sh; read -p "Enter برای ادامه..." ;;
        5) bash logs.sh ;;
        6) bash update.sh; read -p "Enter برای ادامه..." ;;
        7) bash backup.sh; read -p "Enter برای ادامه..." ;;
        8) bash dbinfo.sh; read -p "Enter برای ادامه..." ;;
        9) echo "خداحافظ! 👋"; exit 0 ;;
        *) echo "انتخاب نامعتبر!"; sleep 1 ;;
    esac
done
```

**استفاده:**
```bash
chmod +x manage.sh
bash manage.sh
```

یک منوی تعاملی برای مدیریت کامل ربات!

---

## 🎯 Cron Jobs پیشنهادی

افزودن به crontab:

```bash
crontab -e
```

محتوا:
```cron
# پشتیبان‌گیری روزانه (ساعت 3 صبح)
0 3 * * * cd /path/to/meowvpnbot && bash backup.sh

# به‌روزرسانی هفتگی (شنبه‌ها ساعت 4 صبح)  
0 4 * * 6 cd /path/to/meowvpnbot && bash update.sh

# بررسی وضعیت (هر 6 ساعت)
0 */6 * * * cd /path/to/meowvpnbot && bash status.sh > /tmp/meowvpn_status.log

# حذف لاگ‌های قدیمی (هر هفته)
0 5 * * 0 find /path/to/meowvpnbot/backups -name "*.db" -mtime +30 -delete
```

---

## 📊 Monitoring Script

ایجاد کنید: `monitor.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Simple Monitor

while true; do
    clear
    echo "🔍 Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Bot status
    if pgrep -f "python.*main.py" > /dev/null; then
        PID=$(pgrep -f "python.*main.py")
        MEM=$(ps -p $PID -o rss= | awk '{print $1/1024}')
        CPU=$(ps -p $PID -o %cpu= | awk '{print $1}')
        
        echo "✅ ربات: در حال اجرا"
        echo "   PID: $PID"
        echo "   RAM: ${MEM}MB"
        echo "   CPU: ${CPU}%"
    else
        echo "❌ ربات: متوقف"
    fi
    
    echo ""
    
    # Recent errors
    if [ -f "bot.log" ]; then
        ERROR_COUNT=$(grep -i "error\|exception" bot.log | wc -l)
        echo "📊 خطاها: $ERROR_COUNT"
        
        if [ $ERROR_COUNT -gt 0 ]; then
            echo "   آخرین خطا:"
            grep -i "error\|exception" bot.log | tail -1 | cut -c1-60
        fi
    fi
    
    echo ""
    echo "Press Ctrl+C to exit"
    
    sleep 10
done
```

---

## 🎁 همه اسکریپت‌ها در یک نگاه

| اسکریپت | عملکرد | وضعیت |
|---------|--------|-------|
| `install.sh` | نصب کامل | ✅ آماده |
| `update.sh` | به‌روزرسانی | ✅ آماده |
| `backup.sh` | پشتیبان‌گیری | 💡 پیشنهادی |
| `status.sh` | بررسی وضعیت | 💡 پیشنهادی |
| `restart.sh` | ریستارت سریع | 💡 پیشنهادی |
| `logs.sh` | نمایش لاگ | 💡 پیشنهادی |
| `dbinfo.sh` | اطلاعات DB | 💡 پیشنهادی |
| `monitor.sh` | مانیتورینگ | 💡 پیشنهادی |
| `manage.sh` | منوی مدیریت | 💡 پیشنهادی |

---

## 🚀 یک اسکریپت برای همه! (Ultimate Script)

ایجاد کنید: `bot.sh`

```bash
#!/bin/bash

# MeowVPN Bot - Ultimate Management Tool

case "$1" in
    install)
        bash install.sh
        ;;
    update)
        bash update.sh
        ;;
    start)
        sudo systemctl start meowvpnbot 2>/dev/null || (source venv/bin/activate && nohup python main.py > bot.log 2>&1 &)
        echo "✅ ربات شروع شد"
        ;;
    stop)
        sudo systemctl stop meowvpnbot 2>/dev/null || pkill -f "python.*main.py"
        echo "✅ ربات متوقف شد"
        ;;
    restart)
        bash restart.sh
        ;;
    status)
        bash status.sh
        ;;
    logs)
        bash logs.sh
        ;;
    backup)
        bash backup.sh
        ;;
    *)
        echo "استفاده: $0 {install|update|start|stop|restart|status|logs|backup}"
        echo ""
        echo "مثال:"
        echo "  $0 install   - نصب ربات"
        echo "  $0 update    - به‌روزرسانی"
        echo "  $0 start     - شروع ربات"
        echo "  $0 stop      - توقف ربات"
        echo "  $0 restart   - ریستارت"
        echo "  $0 status    - نمایش وضعیت"
        echo "  $0 logs      - نمایش لاگ‌ها"
        echo "  $0 backup    - پشتیبان‌گیری"
        exit 1
        ;;
esac
```

**استفاده:**
```bash
chmod +x bot.sh

./bot.sh install    # نصب
./bot.sh start      # شروع
./bot.sh stop       # توقف
./bot.sh restart    # ریستارت
./bot.sh status     # وضعیت
./bot.sh logs       # لاگ‌ها
./bot.sh update     # به‌روزرسانی
./bot.sh backup     # پشتیبان
```

---

<div align="center">

**با این اسکریپت‌ها، مدیریت ربات به سادگی آب خوردن است! 🎉**

نسخه: 2.5.0+ | تاریخ: 2025-10-16

</div>

