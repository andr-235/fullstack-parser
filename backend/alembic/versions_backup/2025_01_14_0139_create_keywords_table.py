"""Create keywords table

Revision ID: 0139_create_keywords_table
Revises: 0138_create_groups_table
Create Date: 2025-01-14 01:39:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0139_create_keywords_table'
down_revision = '0138_create_groups_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create keywords table"""
    
    # Create keywords table
    op.create_table('keywords',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('word', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_name', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('match_count', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word')
    )
    
    # Create indexes for keywords table
    op.create_index(op.f('ix_keywords_id'), 'keywords', ['id'], unique=False)
    op.create_index(op.f('ix_keywords_word'), 'keywords', ['word'], unique=True)
    op.create_index(op.f('ix_keywords_category_name'), 'keywords', ['category_name'], unique=False)
    op.create_index(op.f('ix_keywords_is_active'), 'keywords', ['is_active'], unique=False)
    op.create_index(op.f('ix_keywords_is_archived'), 'keywords', ['is_archived'], unique=False)


def downgrade() -> None:
    """Drop keywords table"""
    
    # Drop indexes
    op.drop_index(op.f('ix_keywords_is_archived'), table_name='keywords')
    op.drop_index(op.f('ix_keywords_is_active'), table_name='keywords')
    op.drop_index(op.f('ix_keywords_category_name'), table_name='keywords')
    op.drop_index(op.f('ix_keywords_word'), table_name='keywords')
    op.drop_index(op.f('ix_keywords_id'), table_name='keywords')
    
    # Drop table
    op.drop_table('keywords')
