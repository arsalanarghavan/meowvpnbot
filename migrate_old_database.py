#!/usr/bin/env python3
"""
اسکریپت مایگریشن دیتابیس قدیمی به دیتابیس جدید
این اسکریپت دیتا را از demo.sql به دیتابیس جدید منتقل می‌کند

نکات مهم:
- قبل از اجرا حتما از دیتابیس جدید بکاپ بگیرید
- این اسکریپت فقط INSERT می‌کند و دیتای قدیمی رو پاک نمی‌کند
- برای تست، ابتدا با تعداد کمی رکورد امتحان کنید
"""

import sqlite3
import pymysql
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.engine import Base, engine as db_engine
from database.models.user import User, UserRole
from database.models.panel import Panel, PanelType
from database.models.plan import Plan, PlanCategory
from database.models.service import Service
from database.models.transaction import Transaction, TransactionStatus, TransactionType
from database.models.commission import Commission


class DatabaseMigrator:
    """کلاس اصلی برای مایگریشن دیتابیس"""
    
    def __init__(self, old_db_path: str = "demo.sql", new_db_session=None):
        """
        راه‌اندازی اتصالات دیتابیس
        
        Args:
            old_db_path: مسیر فایل SQL قدیمی
            new_db_session: Session دیتابیس جدید
        """
        self.old_db_path = old_db_path
        self.old_conn = None
        self.new_session = new_db_session
        
        # نقشه‌های mapping برای تبدیل
        self.user_id_mapping = {}  # account_id (old) -> user_id (new)
        self.plan_id_mapping = {}  # product_categories_id (old) -> plan_id (new)
        self.panel_id_mapping = {}  # pannel_id (old) -> panel_id (new)
        
        # آمار مایگریشن
        self.stats = {
            'users': {'success': 0, 'failed': 0},
            'panels': {'success': 0, 'failed': 0},
            'plans': {'success': 0, 'failed': 0},
            'services': {'success': 0, 'failed': 0},
            'transactions': {'success': 0, 'failed': 0},
            'commissions': {'success': 0, 'failed': 0},
        }
        
        # لیست خطاها
        self.errors = []
    
    def connect_old_db(self):
        """اتصال به دیتابیس قدیمی از طریق فایل SQL"""
        print("📂 در حال بارگذاری دیتابیس قدیمی...")
        
        # ایجاد یک دیتابیس SQLite موقت و لود کردن SQL
        self.old_conn = sqlite3.connect(':memory:')
        self.old_conn.row_factory = sqlite3.Row
        
        try:
            # خواندن و اجرای فایل SQL
            with open(self.old_db_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # حذف دستورات MySQL-specific که SQLite نمی‌فهمه
            sql_script = self._clean_sql_for_sqlite(sql_script)
            
            # اجرای اسکریپت
            self.old_conn.executescript(sql_script)
            print("✅ دیتابیس قدیمی بارگذاری شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری دیتابیس قدیمی: {e}")
            self.errors.append(f"Database connection error: {e}")
            return False
    
    def _clean_sql_for_sqlite(self, sql: str) -> str:
        """تمیز کردن SQL برای SQLite"""
        # حذف ENGINE و CHARSET
        sql = re.sub(r'ENGINE=\w+\s+DEFAULT\s+CHARSET=\w+\s+COLLATE=\w+;', ';', sql)
        sql = re.sub(r'ENGINE=\w+;', ';', sql)
        
        # تبدیل bigint به INTEGER
        sql = re.sub(r'bigint\(\d+\)\s+unsigned', 'INTEGER', sql)
        sql = re.sub(r'bigint\(\d+\)', 'INTEGER', sql)
        
        # تبدیل int به INTEGER
        sql = re.sub(r'int\(\d+\)\s+unsigned', 'INTEGER', sql)
        sql = re.sub(r'int\(\d+\)', 'INTEGER', sql)
        
        # تبدیل double به REAL
        sql = re.sub(r'double\(\d+,\d+\)', 'REAL', sql)
        
        # تبدیل varchar به TEXT
        sql = re.sub(r'varchar\(\d+\)', 'TEXT', sql)
        
        # حذف ON DELETE CASCADE/ON UPDATE CASCADE از SQLite
        # (SQLite پشتیبانی می‌کنه ولی نیاز به فعال‌سازی PRAGMA داره)
        
        # حذف UNIQUE KEY و KEY
        sql = re.sub(r'UNIQUE KEY\s+`[^`]+`\s+\([^)]+\)[,]?', '', sql)
        sql = re.sub(r'KEY\s+`[^`]+`\s+\([^)]+\)[,]?', '', sql)
        
        # حذف CONSTRAINT
        sql = re.sub(r'CONSTRAINT\s+`[^`]+`\s+FOREIGN KEY[^,]+,', '', sql)
        
        # حذف SET FOREIGN_KEY_CHECKS
        sql = re.sub(r'SET FOREIGN_KEY_CHECKS=\d+;', '', sql)
        
        # حذف DROP TABLE IF EXISTS (برای جلوگیری از خطا)
        # sql = re.sub(r'DROP TABLE IF EXISTS.*?;', '', sql)
        
        return sql
    
    def migrate_users(self) -> bool:
        """مایگریشن کاربران"""
        print("\n👤 مایگریشن کاربران...")
        
        try:
            cursor = self.old_conn.cursor()
            
            # خواندن اطلاعات کاربران از جداول مختلف
            query = """
                SELECT 
                    u.account_id,
                    u.name,
                    u.role,
                    u.created_at,
                    ab.ballance as wallet_balance,
                    rw.amount as commission_balance,
                    bu.username as telegram_username,
                    bu.first_name,
                    bu.last_name
                FROM users u
                LEFT JOIN account_ballances ab ON u.account_id = ab.account_id
                LEFT JOIN referral_wallets rw ON u.id = rw.referral_user_id
                LEFT JOIN bot_users bu ON u.account_id = bu.account_id
            """
            
            cursor.execute(query)
            users = cursor.fetchall()
            
            for user_row in users:
                try:
                    account_id = user_row['account_id']
                    
                    # تبدیل نقش
                    role_mapping = {
                        'admin': UserRole.admin,
                        'agent': UserRole.marketer,
                        'user': UserRole.customer
                    }
                    role = role_mapping.get(user_row['role'], UserRole.customer)
                    
                    # ایجاد کاربر جدید
                    new_user = User(
                        user_id=account_id,
                        role=role,
                        wallet_balance=user_row['wallet_balance'] or 0,
                        commission_balance=user_row['commission_balance'] or 0,
                        referrer_id=None,  # این رو بعدا از referral_logs می‌گیریم
                        created_at=self._parse_datetime(user_row['created_at']),
                        is_active=True,
                        received_test_account=False
                    )
                    
                    self.new_session.add(new_user)
                    self.user_id_mapping[account_id] = account_id
                    self.stats['users']['success'] += 1
                    
                except Exception as e:
                    self.stats['users']['failed'] += 1
                    self.errors.append(f"User {account_id}: {str(e)}")
                    print(f"  ⚠️  خطا در مایگریشن کاربر {account_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['users']['success']} کاربر مایگریت شد")
            
            if self.stats['users']['failed'] > 0:
                print(f"⚠️  {self.stats['users']['failed']} کاربر با خطا مواجه شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطای کلی در مایگریشن کاربران: {e}")
            return False
    
    def migrate_panels(self) -> bool:
        """مایگریشن پنل‌ها"""
        print("\n🖥️  مایگریشن پنل‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM pannels")
            panels = cursor.fetchall()
            
            for panel_row in panels:
                try:
                    old_panel_id = panel_row['id']
                    
                    # استخراج نام پنل از location
                    location = panel_row['location']
                    panel_name = location.replace('🇳🇱', '').replace('🇬🇧', '').replace('🇫🇷', '') \
                                        .replace('🇸🇪', '').replace('🇩🇪', '').replace('🇹🇷', '').strip()
                    
                    # تمام پنل‌های قدیمی Hiddify هستند
                    new_panel = Panel(
                        name=panel_name,
                        panel_type=PanelType.HIDDIFY,
                        api_base_url=panel_row['url_port'] or '',
                        username=panel_row['username'] or 'admin',
                        password=panel_row['password'] or '',
                        is_active=True
                    )
                    
                    self.new_session.add(new_panel)
                    self.new_session.flush()  # برای گرفتن ID
                    
                    self.panel_id_mapping[old_panel_id] = new_panel.id
                    self.stats['panels']['success'] += 1
                    
                except Exception as e:
                    self.stats['panels']['failed'] += 1
                    self.errors.append(f"Panel {old_panel_id}: {str(e)}")
                    print(f"  ⚠️  خطا در مایگریشن پنل {old_panel_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['panels']['success']} پنل مایگریت شد")
            
            if self.stats['panels']['failed'] > 0:
                print(f"⚠️  {self.stats['panels']['failed']} پنل با خطا مواجه شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطای کلی در مایگریشن پنل‌ها: {e}")
            return False
    
    def migrate_plans(self) -> bool:
        """مایگریشن پلن‌ها (product_categories -> plans)"""
        print("\n📋 مایگریشن پلن‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM product_categories WHERE is_active = 1")
            categories = cursor.fetchall()
            
            for cat_row in categories:
                try:
                    old_cat_id = cat_row['id']
                    
                    # تعیین category از نام
                    category_name = cat_row['category_name']
                    if 'ویژه' in category_name or 'special' in category_name.lower():
                        category = PlanCategory.SPECIAL
                    elif 'گیمینگ' in category_name or 'gaming' in category_name.lower():
                        category = PlanCategory.GAMING
                    elif 'ترید' in category_name or 'trade' in category_name.lower():
                        category = PlanCategory.TRADE
                    else:
                        category = PlanCategory.NORMAL
                    
                    # تبدیل حجم از GB به GB (volume در قدیمی به صورت double هست)
                    traffic_gb = int(cat_row['volume']) if cat_row['volume'] else 0
                    
                    new_plan = Plan(
                        name=category_name,
                        category=category,
                        duration_days=cat_row['expire_day'],
                        traffic_gb=traffic_gb,
                        price=cat_row['price'],
                        device_limit=1,  # پیش‌فرض
                        is_test_plan=False
                    )
                    
                    self.new_session.add(new_plan)
                    self.new_session.flush()
                    
                    self.plan_id_mapping[old_cat_id] = new_plan.id
                    self.stats['plans']['success'] += 1
                    
                except Exception as e:
                    self.stats['plans']['failed'] += 1
                    self.errors.append(f"Plan {old_cat_id}: {str(e)}")
                    print(f"  ⚠️  خطا در مایگریشن پلن {old_cat_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['plans']['success']} پلن مایگریت شد")
            
            if self.stats['plans']['failed'] > 0:
                print(f"⚠️  {self.stats['plans']['failed']} پلن با خطا مواجه شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطای کلی در مایگریشن پلن‌ها: {e}")
            return False
    
    def migrate_services(self) -> bool:
        """مایگریشن سرویس‌ها (products -> services)"""
        print("\n🔧 مایگریشن سرویس‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("""
                SELECT p.*, pc.expire_day 
                FROM products p
                JOIN product_categories pc ON p.product_categories_id = pc.id
                LIMIT 100
            """)  # محدود کردم برای تست - حذفش کنید برای مایگریشن کامل
            products = cursor.fetchall()
            
            for prod_row in products:
                try:
                    account_id = prod_row['account_id']
                    plan_id_old = prod_row['product_categories_id']
                    
                    # بررسی وجود user و plan
                    if account_id not in self.user_id_mapping:
                        print(f"  ⚠️  کاربر {account_id} یافت نشد")
                        continue
                    
                    if plan_id_old not in self.plan_id_mapping:
                        print(f"  ⚠️  پلن {plan_id_old} یافت نشد")
                        continue
                    
                    # استخراج username از subscription_link (UUID)
                    subscription_link = prod_row['subscription_link']
                    username = self._extract_username_from_link(subscription_link)
                    
                    if not username:
                        # اگه username نداشت، از remark یا id استفاده کن
                        username = prod_row['remark'] or f"user_{account_id}_{prod_row['id']}"
                        username = username[:100]  # محدود کردن طول
                    
                    # محاسبه expire_date
                    created_at = self._parse_datetime(prod_row['created_at'])
                    expire_days = prod_row['expire_day']
                    expire_date = created_at + timedelta(days=expire_days)
                    
                    new_service = Service(
                        user_id=account_id,
                        plan_id=self.plan_id_mapping[plan_id_old],
                        username_in_panel=username,
                        note=prod_row['remark'][:100] if prod_row['remark'] else None,
                        start_date=created_at,
                        expire_date=expire_date,
                        auto_renew=False,
                        connection_alerts=True,
                        is_active=bool(prod_row['isActive'])
                    )
                    
                    self.new_session.add(new_service)
                    self.stats['services']['success'] += 1
                    
                except Exception as e:
                    self.stats['services']['failed'] += 1
                    self.errors.append(f"Service {prod_row['id']}: {str(e)}")
                    print(f"  ⚠️  خطا در مایگریشن سرویس {prod_row['id']}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['services']['success']} سرویس مایگریت شد")
            
            if self.stats['services']['failed'] > 0:
                print(f"⚠️  {self.stats['services']['failed']} سرویس با خطا مواجه شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطای کلی در مایگریشن سرویس‌ها: {e}")
            return False
    
    def migrate_transactions(self) -> bool:
        """مایگریشن تراکنش‌ها"""
        print("\n💰 مایگریشن تراکنش‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM transactions LIMIT 200")  # محدود برای تست
            transactions = cursor.fetchall()
            
            for trans_row in transactions:
                try:
                    account_id = trans_row['account_id']
                    
                    if account_id not in self.user_id_mapping:
                        continue
                    
                    # تعیین وضعیت
                    confirmed = trans_row['confirmed']
                    if confirmed == 1:
                        status = TransactionStatus.COMPLETED
                    else:
                        status = TransactionStatus.PENDING
                    
                    # تعیین نوع (از payment_type_id)
                    # payment_type_id == 1 معمولا درگاه پرداخت است
                    # payment_type_id == 3 معمولا کارت به کارت است
                    trans_type = TransactionType.WALLET_CHARGE
                    
                    new_transaction = Transaction(
                        user_id=account_id,
                        plan_id=None,  # در دیتابیس قدیمی نیست
                        amount=trans_row['amount'],
                        type=trans_type,
                        status=status,
                        tracking_code=trans_row['recipe_number'] if trans_row['recipe_number'] != '000' else None,
                        created_at=self._parse_datetime(trans_row['created_at'])
                    )
                    
                    self.new_session.add(new_transaction)
                    self.stats['transactions']['success'] += 1
                    
                except Exception as e:
                    self.stats['transactions']['failed'] += 1
                    self.errors.append(f"Transaction {trans_row['id']}: {str(e)}")
                    print(f"  ⚠️  خطا در مایگریشن تراکنش {trans_row['id']}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['transactions']['success']} تراکنش مایگریت شد")
            
            if self.stats['transactions']['failed'] > 0:
                print(f"⚠️  {self.stats['transactions']['failed']} تراکنش با خطا مواجه شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطای کلی در مایگریشن تراکنش‌ها: {e}")
            return False
    
    def _extract_username_from_link(self, link: str) -> Optional[str]:
        """استخراج UUID از لینک subscription"""
        if not link:
            return None
        
        # الگوی UUID: 8-4-4-4-12
        uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
        match = re.search(uuid_pattern, link, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        """تبدیل string به datetime"""
        if not dt_str:
            return datetime.utcnow()
        
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.utcnow()
    
    def print_summary(self):
        """نمایش خلاصه مایگریشن"""
        print("\n" + "="*60)
        print("📊 خلاصه مایگریشن")
        print("="*60)
        
        total_success = sum(s['success'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())
        
        for entity, counts in self.stats.items():
            print(f"  {entity.capitalize()}: ✅ {counts['success']} | ❌ {counts['failed']}")
        
        print(f"\n  کل موفق: {total_success}")
        print(f"  کل ناموفق: {total_failed}")
        
        if self.errors:
            print(f"\n⚠️  تعداد خطاها: {len(self.errors)}")
            print("  برای مشاهده جزئیات خطاها، لاگ را بررسی کنید")
    
    def run(self) -> bool:
        """اجرای کامل مایگریشن"""
        print("🚀 شروع مایگریشن دیتابیس...")
        print("="*60)
        
        # اتصال به دیتابیس قدیمی
        if not self.connect_old_db():
            return False
        
        # مراحل مایگریشن
        steps = [
            ("کاربران", self.migrate_users),
            ("پنل‌ها", self.migrate_panels),
            ("پلن‌ها", self.migrate_plans),
            ("سرویس‌ها", self.migrate_services),
            ("تراکنش‌ها", self.migrate_transactions),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            try:
                if not step_func():
                    print(f"❌ مایگریشن {step_name} ناموفق بود")
                    # ادامه به مراحل بعدی
            except Exception as e:
                print(f"❌ خطای غیرمنتظره در {step_name}: {e}")
        
        # نمایش خلاصه
        self.print_summary()
        
        # بستن اتصال
        if self.old_conn:
            self.old_conn.close()
        
        print("\n✨ مایگریشن به پایان رسید")
        return True


def main():
    """تابع اصلی"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║         🐈 مایگریشن دیتابیس MeowVPN Bot 🐈               ║
║                                                           ║
║  این اسکریپت دیتا را از ربات قدیمی (Hiddify فقط)        ║
║  به ربات جدید (Hiddify + Marzban) منتقل می‌کند          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # هشدار
    print("⚠️  هشدار: قبل از اجرا از دیتابیس جدید بکاپ بگیرید!")
    print("⚠️  این اسکریپت فقط INSERT می‌کند و دیتای قبلی را پاک نمی‌کند")
    print()
    
    response = input("آیا می‌خواهید ادامه دهید؟ (yes/no): ")
    if response.lower() not in ['yes', 'y', 'بله']:
        print("❌ عملیات لغو شد")
        return
    
    # ایجاد session برای دیتابیس جدید
    Session = sessionmaker(bind=db_engine)
    session = Session()
    
    try:
        # اجرای مایگریشن
        migrator = DatabaseMigrator(old_db_path="demo.sql", new_db_session=session)
        success = migrator.run()
        
        if success:
            print("\n✅ مایگریشن با موفقیت انجام شد!")
        else:
            print("\n⚠️  مایگریشن با مشکلات انجام شد. لاگ را بررسی کنید.")
        
        # ذخیره خطاها در فایل
        if migrator.errors:
            with open('migration_errors.log', 'w', encoding='utf-8') as f:
                for error in migrator.errors:
                    f.write(f"{error}\n")
            print(f"\n📄 {len(migrator.errors)} خطا در فایل migration_errors.log ذخیره شد")
    
    except Exception as e:
        print(f"\n❌ خطای کلی: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()


if __name__ == "__main__":
    main()

