"""
Database models package.
This module exports all database models for use throughout the application.
"""
# Export all models so they can be imported easily
from database.models.user import User, UserRole
from database.models.plan import Plan, PlanCategory
from database.models.service import Service
from database.models.transaction import Transaction, TransactionType, TransactionStatus
from database.models.commission import Commission
from database.models.gift_card import GiftCard
from database.models.panel import Panel, PanelType
from database.models.setting import Setting
from database.models.card_account import CardAccount

# Also export as module-level names for Alembic compatibility
from database.models import user
from database.models import plan
from database.models import service
from database.models import transaction
from database.models import commission
from database.models import gift_card
from database.models import panel
from database.models import setting
from database.models import card_account

__all__ = [
    # Model classes
    'User',
    'UserRole',
    'Plan',
    'PlanCategory',
    'Service',
    'Transaction',
    'TransactionType',
    'TransactionStatus',
    'Commission',
    'GiftCard',
    'Panel',
    'PanelType',
    'Setting',
    'CardAccount',
    # Modules (for Alembic)
    'user',
    'plan',
    'service',
    'transaction',
    'commission',
    'gift_card',
    'panel',
    'setting',
    'card_account',
]

