"""add card_accounts table

Revision ID: 003_add_card_accounts
Revises: 002_add_connection_alerts
Create Date: 2025-10-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_card_accounts'
down_revision = '002_add_connection_alerts'
branch_labels = None
depends_on = None


def upgrade():
    # Create card_accounts table
    op.create_table(
        'card_accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('card_number', sa.String(length=16), nullable=False),
        sa.Column('card_holder', sa.String(length=100), nullable=False),
        sa.Column('daily_limit', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('current_amount', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_reset_date', sa.DateTime(), nullable=True),
        sa.Column('note', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('card_number')
    )
    
    # Create index on card_number for faster lookups
    op.create_index('ix_card_accounts_card_number', 'card_accounts', ['card_number'])


def downgrade():
    # Drop index first
    op.drop_index('ix_card_accounts_card_number', table_name='card_accounts')
    
    # Drop table
    op.drop_table('card_accounts')

