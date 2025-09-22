"""Merge final heads

Revision ID: merge_final_heads
Revises: add_fulltext_search_indexes,0140_create_parsing_tasks_table
Create Date: 2025-09-16 13:47:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_final_heads'
down_revision = ('add_fulltext_search_indexes', '0140_create_parsing_tasks_table')
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Merge final heads - no changes needed as tables already exist"""
    pass


def downgrade() -> None:
    """Merge final heads - no changes needed"""
    pass
