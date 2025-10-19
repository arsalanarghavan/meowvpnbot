"""initial migration with all core tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.Enum('customer', 'marketer', 'admin', name='userrole'), nullable=False),
        sa.Column('wallet_balance', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('commission_balance', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('referrer_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('received_test_account', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # Create plans table
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.Enum('عادی', 'ویژه', 'گیمینگ', 'ترید', name='plancategory'), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('traffic_gb', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('price', sa.BigInteger(), nullable=False),
        sa.Column('device_limit', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_test_plan', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create panels table
    op.create_table(
        'panels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('api_base_url', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_base_url')
    )

    # Create services table
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('username_in_panel', sa.String(length=100), nullable=False),
        sa.Column('note', sa.String(length=100), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('expire_date', sa.DateTime(), nullable=False),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username_in_panel')
    )
    op.create_index(op.f('ix_services_user_id'), 'services', ['user_id'], unique=False)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.Enum('شارژ کیف پول', 'خرید سرویس', 'کارت هدیه', name='transactiontype'), nullable=False),
        sa.Column('status', sa.Enum('در انتظار', 'موفق', 'ناموفق', name='transactionstatus'), nullable=False),
        sa.Column('tracking_code', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)

    # Create commissions table
    op.create_table(
        'commissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('marketer_id', sa.BigInteger(), nullable=False),
        sa.Column('referred_user_id', sa.BigInteger(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('commission_amount', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_paid_out', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['marketer_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['referred_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_commissions_marketer_id'), 'commissions', ['marketer_id'], unique=False)

    # Create gift_cards table
    op.create_table(
        'gift_cards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.BigInteger(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('used_by_user_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['used_by_user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_gift_cards_code'), 'gift_cards', ['code'], unique=False)

    # Create settings table
    op.create_table(
        'settings',
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    op.drop_table('settings')
    
    op.drop_index(op.f('ix_gift_cards_code'), table_name='gift_cards')
    op.drop_table('gift_cards')
    
    op.drop_index(op.f('ix_commissions_marketer_id'), table_name='commissions')
    op.drop_table('commissions')
    
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_table('transactions')
    
    op.drop_index(op.f('ix_services_user_id'), table_name='services')
    op.drop_table('services')
    
    op.drop_table('panels')
    op.drop_table('plans')
    
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')

