"""Create authors table

Revision ID: 0136_create_authors_table
Revises: 0134_merge_all_heads
Create Date: 2025-01-14 01:36:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0136_create_authors_table'
down_revision = '0134_merge_all_heads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create authors table"""
    
    # Create authors table
    op.create_table('authors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vk_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('screen_name', sa.String(length=100), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_closed', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('followers_count', sa.Integer(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('author_metadata', sa.Text(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vk_id')
    )
    
    # Create indexes for authors table
    op.create_index(op.f('ix_authors_id'), 'authors', ['id'], unique=False)
    op.create_index(op.f('ix_authors_vk_id'), 'authors', ['vk_id'], unique=True)
    op.create_index(op.f('ix_authors_screen_name'), 'authors', ['screen_name'], unique=False)
    op.create_index('idx_authors_vk_id', 'authors', ['vk_id'], unique=False)
    op.create_index('idx_authors_screen_name', 'authors', ['screen_name'], unique=False)
    op.create_index('idx_authors_status', 'authors', ['status'], unique=False)
    op.create_index('idx_authors_created_at', 'authors', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop authors table"""
    
    # Drop indexes
    op.drop_index('idx_authors_created_at', table_name='authors')
    op.drop_index('idx_authors_status', table_name='authors')
    op.drop_index('idx_authors_screen_name', table_name='authors')
    op.drop_index('idx_authors_vk_id', table_name='authors')
    op.drop_index(op.f('ix_authors_screen_name'), table_name='authors')
    op.drop_index(op.f('ix_authors_vk_id'), table_name='authors')
    op.drop_index(op.f('ix_authors_id'), table_name='authors')
    
    # Drop table
    op.drop_table('authors')
