"""Create parsing_tasks table

Revision ID: 0140_create_parsing_tasks_table
Revises: 0139_create_keywords_table
Create Date: 2025-01-14 01:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0140_create_parsing_tasks_table'
down_revision = '0139_create_keywords_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create parsing_tasks table"""
    
    # Create parsing_tasks table
    op.create_table('parsing_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('group_ids', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('current_group', sa.Integer(), nullable=True),
        sa.Column('groups_completed', sa.Integer(), nullable=True),
        sa.Column('groups_total', sa.Integer(), nullable=False),
        sa.Column('posts_found', sa.Integer(), nullable=True),
        sa.Column('comments_found', sa.Integer(), nullable=True),
        sa.Column('errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop parsing_tasks table"""
    
    # Drop table
    op.drop_table('parsing_tasks')
