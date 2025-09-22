"""Merge all heads

Revision ID: 0134_merge_all_heads
Revises: 0132_create_users_table,0133_create_comments_table
Create Date: 2025-01-14 01:34:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0134_merge_all_heads'
down_revision = ('0132_create_users_table', '0133_create_comments_table')
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Merge all heads - no changes needed as tables already exist"""
    pass


def downgrade() -> None:
    """Merge all heads - no changes needed"""
    pass
