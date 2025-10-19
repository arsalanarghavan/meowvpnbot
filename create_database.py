#!/usr/bin/env python3
"""
اسکریپت ساخت دیتابیس و جداول
"""

from database.engine import engine, Base
from database.models.user import User
from database.models.panel import Panel
from database.models.plan import Plan
from database.models.service import Service
from database.models.transaction import Transaction
from database.models.commission import Commission
from database.models.gift_card import GiftCard
from database.models.card_account import CardAccount
from database.models.setting import Setting

print("🔧 در حال ساخت دیتابیس و جداول...")

try:
    # ساخت تمام جداول
    Base.metadata.create_all(bind=engine)
    print("✅ دیتابیس و جداول با موفقیت ساخته شدند!")
    
    # نمایش جداول ساخته شده
    tables = Base.metadata.tables.keys()
    print(f"\n📋 جداول ساخته شده ({len(tables)} جدول):")
    for table in tables:
        print(f"  • {table}")
    
except Exception as e:
    print(f"❌ خطا در ساخت دیتابیس: {e}")
    import traceback
    traceback.print_exc()

