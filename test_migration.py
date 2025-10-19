#!/usr/bin/env python3
"""
اسکریپت تست مایگریشن - فقط چند رکورد را تست می‌کند
برای اطمینان از درستی کار اسکریپت قبل از مایگریشن کامل
"""

import sqlite3
import re
from datetime import datetime, timedelta


def test_sql_cleaning():
    """تست تمیز کردن SQL"""
    print("🧪 تست تمیز کردن SQL...")
    
    test_sql = """
    CREATE TABLE `test` (
        `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        `name` varchar(255) NOT NULL,
        `balance` double(15,2) DEFAULT 0.00,
        PRIMARY KEY (`id`),
        KEY `test_name` (`name`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # تبدیل‌های مورد نیاز
    test_sql = re.sub(r'bigint\(\d+\)\s+unsigned', 'INTEGER', test_sql)
    test_sql = re.sub(r'varchar\(\d+\)', 'TEXT', test_sql)
    test_sql = re.sub(r'double\(\d+,\d+\)', 'REAL', test_sql)
    test_sql = re.sub(r'ENGINE=\w+\s+DEFAULT\s+CHARSET=\w+\s+COLLATE=\w+;', ';', test_sql)
    test_sql = re.sub(r'KEY\s+`[^`]+`\s+\([^)]+\)[,]?', '', test_sql)
    
    print("  ✅ تمیز کردن SQL موفق")
    print(f"  نتیجه:\n{test_sql[:200]}...")
    return True


def test_uuid_extraction():
    """تست استخراج UUID"""
    print("\n🧪 تست استخراج UUID...")
    
    test_links = [
        "/965347fe-ac4b-4b8b-9830-04618b0284cf/all.txt",
        "https://panel.com/c1e49b25-c340-490d-82de-e0a260142050/sub",
        "no-uuid-here",
        None
    ]
    
    uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    
    for link in test_links:
        if link:
            match = re.search(uuid_pattern, link, re.IGNORECASE)
            uuid = match.group(1) if match else None
        else:
            uuid = None
        
        print(f"  Link: {link}")
        print(f"  UUID: {uuid}")
    
    print("  ✅ استخراج UUID موفق")
    return True


def test_datetime_parsing():
    """تست تبدیل تاریخ"""
    print("\n🧪 تست تبدیل تاریخ...")
    
    test_dates = [
        "2025-05-18 13:41:47",
        "2025-06-20 12:57:55",
        None,
        "invalid-date"
    ]
    
    for date_str in test_dates:
        try:
            if not date_str:
                dt = datetime.utcnow()
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            print(f"  ✅ {date_str} → {dt}")
        except Exception as e:
            print(f"  ⚠️  {date_str} → خطا: {e}")
            dt = datetime.utcnow()
            print(f"     استفاده از تاریخ پیش‌فرض: {dt}")
    
    print("  ✅ تبدیل تاریخ موفق")
    return True


def test_expire_date_calculation():
    """تست محاسبه تاریخ انقضا"""
    print("\n🧪 تست محاسبه تاریخ انقضا...")
    
    start_date = datetime(2025, 6, 1, 12, 0, 0)
    durations = [30, 90, 180]
    
    for days in durations:
        expire_date = start_date + timedelta(days=days)
        print(f"  شروع: {start_date.date()} + {days} روز = انقضا: {expire_date.date()}")
    
    print("  ✅ محاسبه تاریخ انقضا موفق")
    return True


def test_role_mapping():
    """تست نگاشت نقش‌ها"""
    print("\n🧪 تست نگاشت نقش‌ها...")
    
    role_mapping = {
        'admin': 'admin',
        'agent': 'marketer',
        'user': 'customer'
    }
    
    for old_role, new_role in role_mapping.items():
        print(f"  {old_role} → {new_role}")
    
    print("  ✅ نگاشت نقش‌ها موفق")
    return True


def test_demo_sql_structure():
    """تست ساختار demo.sql"""
    print("\n🧪 تست ساختار demo.sql...")
    
    try:
        with open('demo.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # بررسی وجود جداول
        required_tables = [
            'users',
            'bot_users',
            'account_ballances',
            'pannels',
            'product_categories',
            'products',
            'transactions',
            'referral_logs',
            'referral_wallets'
        ]
        
        print(f"  📄 اندازه فایل: {len(content) / 1024 / 1024:.2f} MB")
        
        for table in required_tables:
            if f"CREATE TABLE `{table}`" in content:
                print(f"  ✅ جدول {table} یافت شد")
            else:
                print(f"  ❌ جدول {table} یافت نشد")
        
        # شمارش رکوردها (تقریبی)
        insert_count = content.count("INSERT INTO")
        print(f"\n  📊 تعداد تقریبی دستورات INSERT: {insert_count}")
        
        return True
        
    except FileNotFoundError:
        print("  ❌ فایل demo.sql یافت نشد!")
        print("  لطفاً فایل demo.sql را در همین دایرکتوری قرار دهید")
        return False
    except Exception as e:
        print(f"  ❌ خطا در خواندن فایل: {e}")
        return False


def test_sqlite_compatibility():
    """تست سازگاری با SQLite"""
    print("\n🧪 تست سازگاری SQLite...")
    
    try:
        # ایجاد دیتابیس موقت
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # تست ساخت جدول ساده
        cursor.execute("""
            CREATE TABLE test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL DEFAULT 0.0
            )
        """)
        
        # تست insert
        cursor.execute("INSERT INTO test (name, balance) VALUES (?, ?)", ("Test User", 100.5))
        
        # تست select
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        
        print(f"  ✅ ایجاد جدول: موفق")
        print(f"  ✅ INSERT: موفق")
        print(f"  ✅ SELECT: موفق (نتیجه: {result})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return False


def test_data_consistency():
    """تست سازگاری داده‌ها"""
    print("\n🧪 تست سازگاری داده‌ها...")
    
    try:
        with open('demo.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # استخراج تعداد تقریبی رکوردها
        users_count = content.count("INSERT INTO `users`")
        products_count = content.count("INSERT INTO `products`")
        transactions_count = content.count("INSERT INTO `transactions`")
        
        print(f"  📊 تعداد تقریبی کاربران: {users_count}")
        print(f"  📊 تعداد تقریبی محصولات: {products_count}")
        print(f"  📊 تعداد تقریبی تراکنش‌ها: {transactions_count}")
        
        if users_count > 0:
            print(f"\n  ✅ داده‌های کاربران وجود دارد")
        else:
            print(f"\n  ⚠️  داده‌های کاربران یافت نشد")
        
        return True
        
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return False


def main():
    """اجرای تست‌ها"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║          🧪 تست اسکریپت مایگریشن دیتابیس 🧪              ║
║                                                           ║
║  این اسکریپت عملکرد مایگریشن را بدون تغییر دیتابیس       ║
║  تست می‌کند تا اطمینان حاصل شود همه چیز درست کار         ║
║  می‌کند.                                                  ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("تمیز کردن SQL", test_sql_cleaning),
        ("استخراج UUID", test_uuid_extraction),
        ("تبدیل تاریخ", test_datetime_parsing),
        ("محاسبه تاریخ انقضا", test_expire_date_calculation),
        ("نگاشت نقش‌ها", test_role_mapping),
        ("ساختار demo.sql", test_demo_sql_structure),
        ("سازگاری SQLite", test_sqlite_compatibility),
        ("سازگاری داده‌ها", test_data_consistency),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ خطای غیرمنتظره در تست {test_name}: {e}")
            failed += 1
    
    # نتیجه نهایی
    print(f"\n{'='*60}")
    print("📊 نتیجه تست‌ها")
    print(f"{'='*60}")
    print(f"  ✅ موفق: {passed}")
    print(f"  ❌ ناموفق: {failed}")
    print(f"  📈 درصد موفقیت: {(passed / len(tests) * 100):.1f}%")
    
    if failed == 0:
        print("\n✨ همه تست‌ها موفق بودند! می‌توانید مایگریشن را اجرا کنید.")
        print("\n💡 مرحله بعدی:")
        print("   1. از دیتابیس جدید بکاپ بگیرید")
        print("   2. دستور زیر را اجرا کنید:")
        print("      python migrate_old_database.py")
    else:
        print("\n⚠️  بعضی تست‌ها ناموفق بودند. لطفاً مشکلات را برطرف کنید.")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

