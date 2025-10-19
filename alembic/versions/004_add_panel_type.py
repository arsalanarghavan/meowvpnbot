"""add panel_type to panels table

Revision ID: 004_add_panel_type
Revises: 003_add_card_accounts
Create Date: 2025-10-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_panel_type'
down_revision = '003_add_card_accounts'
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type for panel_type
    panel_type_enum = sa.Enum('MARZBAN', 'HIDDIFY', name='paneltype')
    panel_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Add panel_type column with default value of 'MARZBAN' for existing records
    op.add_column('panels', 
        sa.Column('panel_type', panel_type_enum, nullable=False, server_default='MARZBAN')
    )


def downgrade():
    # Remove panel_type column
    op.drop_column('panels', 'panel_type')
    
    # Drop the enum type
    panel_type_enum = sa.Enum('MARZBAN', 'HIDDIFY', name='paneltype')
    panel_type_enum.drop(op.get_bind(), checkfirst=True)

