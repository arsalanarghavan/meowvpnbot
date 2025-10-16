"""add connection_alerts to service

Revision ID: 002_add_connection_alerts
Revises: 001_initial
Create Date: 2025-10-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_connection_alerts'
down_revision = '001_initial'  # Update this to your last migration
branch_labels = None
depends_on = None


def upgrade():
    # Add connection_alerts column to services table
    op.add_column('services', sa.Column('connection_alerts', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    # Remove connection_alerts column from services table
    op.drop_column('services', 'connection_alerts')

