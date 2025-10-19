#!/usr/bin/env python3
"""
اسکریپت مایگریشن از MySQL به SQLite
این اسکریپت مستقیماً از MySQL قدیمی می‌خونه و به دیتابیس جدید منتقل می‌کنه

مراحل:
1. Import فایل demo.sql به MySQL:
   mysql -u root -p -e "CREATE DATABASE old_bot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -p old_bot_db < demo.sql

2. اجرای این اسکریپت:
   python migrate_from_mysql.py
"""

import pymysql
from datetime import datetime, timedelta
from typing import Optional, Dict
import re
from sqlalchemy.orm import sessionmaker
from database.engine import Base, engine as db_engine
from database.models.user import User, UserRole
from database.models.panel import Panel, PanelType
from database.models.plan import Plan, PlanCategory
from database.models.service import Service
from database.models.transaction import Transaction, TransactionStatus, TransactionType
from database.models.commission import Commission


class MySQLMigrator:
    """کلاس مایگریشن از MySQL"""
    
    def __init__(self):
        """راه‌اندازی"""
        self.old_conn = None
        self.new_session = None
        
        # نقشه‌های mapping
        self.user_id_mapping = {}
        self.plan_id_mapping = {}
        self.panel_id_mapping = {}
        
        # آمار
        self.stats = {
            'users': {'success': 0, 'failed': 0},
            'panels': {'success': 0, 'failed': 0},
            'plans': {'success': 0, 'failed': 0},
            'services': {'success': 0, 'failed': 0},
            'transactions': {'success': 0, 'failed': 0},
        }
        
        self.errors = []
    
    def connect_old_mysql(self, host='localhost', user='root', password='', database='old_bot_db'):
        """اتصال به MySQL قدیمی"""
        print(f"🔌 اتصال به MySQL ({database})...")
        
        try:
            self.old_conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✅ اتصال به MySQL موفق")
            return True
        except Exception as e:
            print(f"❌ خطا در اتصال به MySQL: {e}")
            print("\n💡 ابتدا فایل SQL رو import کنید:")
            print(f"   mysql -u {user} -p -e \"CREATE DATABASE {database} CHARACTER SET utf8mb4;\"")
            print(f"   mysql -u {user} -p {database} < demo.sql")
            return False
    
    def connect_new_db(self):
        """اتصال به دیتابیس جدید"""
        print("🔌 اتصال به دیتابیس جدید...")
        
        try:
            Session = sessionmaker(bind=db_engine)
            self.new_session = Session()
            print("✅ اتصال به دیتابیس جدید موفق")
            return True
        except Exception as e:
            print(f"❌ خطا در اتصال: {e}")
            return False
    
    def migrate_users(self) -> bool:
        """مایگریشن کاربران"""
        print("\n👤 مایگریشن کاربران...")
        
        try:
            cursor = self.old_conn.cursor()
            
            # Query برای گرفتن اطلاعات کامل کاربران
            query = """
                SELECT 
                    u.account_id,
                    u.name,
                    u.role,
                    u.created_at,
                    COALESCE(ab.ballance, 0) as wallet_balance,
                    COALESCE(rw.amount, 0) as commission_balance
                FROM users u
                LEFT JOIN account_ballances ab ON u.account_id = ab.account_id
                LEFT JOIN referral_wallets rw ON u.id = rw.referral_user_id
            """
            
            cursor.execute(query)
            users = cursor.fetchall()
            
            print(f"  📊 تعداد کاربران: {len(users)}")
            
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
                        referrer_id=None,
                        created_at=user_row['created_at'] or datetime.utcnow(),
                        is_active=True,
                        received_test_account=False
                    )
                    
                    self.new_session.add(new_user)
                    self.user_id_mapping[account_id] = account_id
                    self.stats['users']['success'] += 1
                    
                except Exception as e:
                    self.stats['users']['failed'] += 1
                    self.errors.append(f"User {account_id}: {str(e)}")
                    print(f"  ⚠️  خطا در کاربر {account_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['users']['success']} کاربر مایگریت شد")
            
            if self.stats['users']['failed'] > 0:
                print(f"⚠️  {self.stats['users']['failed']} کاربر با خطا")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطا در مایگریشن کاربران: {e}")
            return False
    
    def migrate_panels(self) -> bool:
        """مایگریشن پنل‌ها"""
        print("\n🖥️  مایگریشن پنل‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM pannels")
            panels = cursor.fetchall()
            
            print(f"  📊 تعداد پنل‌ها: {len(panels)}")
            
            for panel_row in panels:
                try:
                    old_panel_id = panel_row['id']
                    
                    # استخراج نام از location
                    location = panel_row['location'] or 'Unknown'
                    panel_name = location.replace('🇳🇱', '').replace('🇬🇧', '').replace('🇫🇷', '') \
                                        .replace('🇸🇪', '').replace('🇩🇪', '').replace('🇹🇷', '').strip()
                    
                    # همه پنل‌ها Hiddify هستند
                    new_panel = Panel(
                        name=panel_name or f"Panel {old_panel_id}",
                        panel_type=PanelType.HIDDIFY,
                        api_base_url=panel_row['url_port'] or '',
                        username=panel_row['username'] or 'admin',
                        password=str(panel_row['password']) or '',
                        is_active=True
                    )
                    
                    self.new_session.add(new_panel)
                    self.new_session.flush()
                    
                    self.panel_id_mapping[old_panel_id] = new_panel.id
                    self.stats['panels']['success'] += 1
                    
                except Exception as e:
                    self.stats['panels']['failed'] += 1
                    self.errors.append(f"Panel {old_panel_id}: {str(e)}")
                    print(f"  ⚠️  خطا در پنل {old_panel_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['panels']['success']} پنل مایگریت شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطا در مایگریشن پنل‌ها: {e}")
            return False
    
    def migrate_plans(self) -> bool:
        """مایگریشن پلن‌ها"""
        print("\n📋 مایگریشن پلن‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM product_categories WHERE is_active = 1")
            categories = cursor.fetchall()
            
            print(f"  📊 تعداد پلن‌ها: {len(categories)}")
            
            for cat_row in categories:
                try:
                    old_cat_id = cat_row['id']
                    
                    # تعیین category
                    category_name = cat_row['category_name']
                    if 'ویژه' in category_name or 'special' in category_name.lower():
                        category = PlanCategory.SPECIAL
                    elif 'گیمینگ' in category_name or 'gaming' in category_name.lower():
                        category = PlanCategory.GAMING
                    elif 'ترید' in category_name or 'trade' in category_name.lower():
                        category = PlanCategory.TRADE
                    else:
                        category = PlanCategory.NORMAL
                    
                    # تبدیل حجم
                    traffic_gb = int(cat_row['volume']) if cat_row['volume'] else 0
                    
                    new_plan = Plan(
                        name=category_name,
                        category=category,
                        duration_days=cat_row['expire_day'],
                        traffic_gb=traffic_gb,
                        price=cat_row['price'],
                        device_limit=1,
                        is_test_plan=False
                    )
                    
                    self.new_session.add(new_plan)
                    self.new_session.flush()
                    
                    self.plan_id_mapping[old_cat_id] = new_plan.id
                    self.stats['plans']['success'] += 1
                    
                except Exception as e:
                    self.stats['plans']['failed'] += 1
                    self.errors.append(f"Plan {old_cat_id}: {str(e)}")
                    print(f"  ⚠️  خطا در پلن {old_cat_id}: {e}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['plans']['success']} پلن مایگریت شد")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطا در مایگریشن پلن‌ها: {e}")
            return False
    
    def migrate_services(self) -> bool:
        """مایگریشن سرویس‌ها"""
        print("\n🔧 مایگریشن سرویس‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            query = """
                SELECT p.*, pc.expire_day 
                FROM products p
                JOIN product_categories pc ON p.product_categories_id = pc.id
            """
            cursor.execute(query)
            products = cursor.fetchall()
            
            print(f"  📊 تعداد سرویس‌ها: {len(products)}")
            
            for prod_row in products:
                try:
                    account_id = prod_row['account_id']
                    plan_id_old = prod_row['product_categories_id']
                    
                    # بررسی وجود
                    if account_id not in self.user_id_mapping:
                        continue
                    if plan_id_old not in self.plan_id_mapping:
                        continue
                    
                    # استخراج username
                    subscription_link = prod_row['subscription_link']
                    username = self._extract_username(subscription_link)
                    
                    if not username:
                        username = prod_row['remark'] or f"user_{account_id}_{prod_row['id']}"
                        username = username[:100]
                    
                    # محاسبه expire_date
                    created_at = prod_row['created_at'] or datetime.utcnow()
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
            
            self.new_session.commit()
            print(f"✅ {self.stats['services']['success']} سرویس مایگریت شد")
            
            if self.stats['services']['failed'] > 0:
                print(f"⚠️  {self.stats['services']['failed']} سرویس با خطا")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطا در مایگریشن سرویس‌ها: {e}")
            return False
    
    def migrate_transactions(self) -> bool:
        """مایگریشن تراکنش‌ها"""
        print("\n💰 مایگریشن تراکنش‌ها...")
        
        try:
            cursor = self.old_conn.cursor()
            cursor.execute("SELECT * FROM transactions")
            transactions = cursor.fetchall()
            
            print(f"  📊 تعداد تراکنش‌ها: {len(transactions)}")
            
            for trans_row in transactions:
                try:
                    account_id = trans_row['account_id']
                    
                    if account_id not in self.user_id_mapping:
                        continue
                    
                    # تعیین وضعیت
                    confirmed = trans_row['confirmed']
                    status = TransactionStatus.COMPLETED if confirmed == 1 else TransactionStatus.PENDING
                    
                    # تعیین نوع
                    trans_type = TransactionType.WALLET_CHARGE
                    
                    new_transaction = Transaction(
                        user_id=account_id,
                        plan_id=None,
                        amount=trans_row['amount'],
                        type=trans_type,
                        status=status,
                        tracking_code=trans_row['recipe_number'] if trans_row['recipe_number'] != '000' else None,
                        created_at=trans_row['created_at'] or datetime.utcnow()
                    )
                    
                    self.new_session.add(new_transaction)
                    self.stats['transactions']['success'] += 1
                    
                except Exception as e:
                    self.stats['transactions']['failed'] += 1
                    self.errors.append(f"Transaction {trans_row['id']}: {str(e)}")
            
            self.new_session.commit()
            print(f"✅ {self.stats['transactions']['success']} تراکنش مایگریت شد")
            
            if self.stats['transactions']['failed'] > 0:
                print(f"⚠️  {self.stats['transactions']['failed']} تراکنش با خطا")
            
            return True
            
        except Exception as e:
            self.new_session.rollback()
            print(f"❌ خطا در مایگریشن تراکنش‌ها: {e}")
            return False
    
    def _extract_username(self, link: str) -> Optional[str]:
        """استخراج UUID از لینک"""
        if not link:
            return None
        
        uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
        match = re.search(uuid_pattern, link, re.IGNORECASE)
        
        return match.group(1) if match else None
    
    def print_summary(self):
        """نمایش خلاصه"""
        print("\n" + "="*60)
        print("📊 خلاصه مایگریشن")
        print("="*60)
        
        for entity, counts in self.stats.items():
            print(f"  {entity.capitalize()}: ✅ {counts['success']} | ❌ {counts['failed']}")
        
        total_success = sum(s['success'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())
        
        print(f"\n  کل موفق: {total_success}")
        print(f"  کل ناموفق: {total_failed}")
        
        if self.errors:
            print(f"\n⚠️  {len(self.errors)} خطا - ذخیره شده در migration_errors.log")
    
    def run(self):
        """اجرای مایگریشن"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║      🐈 مایگریشن از MySQL به SQLite 🐈                    ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        # دریافت اطلاعات MySQL
        print("📝 لطفاً اطلاعات MySQL قدیمی را وارد کنید:\n")
        
        host = input("  Host (پیش‌فرض: localhost): ").strip() or 'localhost'
        user = input("  Username (پیش‌فرض: root): ").strip() or 'root'
        password = input("  Password: ").strip()
        database = input("  Database (پیش‌فرض: old_bot_db): ").strip() or 'old_bot_db'
        
        print()
        
        # اتصالات
        if not self.connect_old_mysql(host, user, password, database):
            return False
        
        if not self.connect_new_db():
            return False
        
        # مایگریشن
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
                step_func()
            except Exception as e:
                print(f"❌ خطا در {step_name}: {e}")
        
        # خلاصه
        self.print_summary()
        
        # ذخیره خطاها
        if self.errors:
            with open('migration_errors.log', 'w', encoding='utf-8') as f:
                for error in self.errors:
                    f.write(f"{error}\n")
        
        # بستن اتصالات
        if self.old_conn:
            self.old_conn.close()
        if self.new_session:
            self.new_session.close()
        
        print("\n✨ مایگریشن به پایان رسید\n")
        return True


if __name__ == "__main__":
    migrator = MySQLMigrator()
    migrator.run()

