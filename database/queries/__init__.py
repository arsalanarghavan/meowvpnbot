"""
Wrapper module for database queries.
This module re-exports all query modules from database.models.queries
to maintain backward compatibility with existing imports.
"""
# Re-export all query modules from database.models.queries
from database.models.queries import (
    card_queries,
    commission_queries,
    gift_card_queries,
    panel_queries,
    plan_queries,
    service_queries,
    setting_queries,
    transaction_queries,
    user_queries,
)

__all__ = [
    'card_queries',
    'commission_queries',
    'gift_card_queries',
    'panel_queries',
    'plan_queries',
    'service_queries',
    'setting_queries',
    'transaction_queries',
    'user_queries',
]

