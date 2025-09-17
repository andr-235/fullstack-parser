"""Create posts table

Revision ID: 0137_create_posts_table
Revises: 0136_create_authors_table
Create Date: 2025-01-14 01:37:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0137_create_posts_table'
down_revision = '0136_create_authors_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create posts table"""
    
    # Create posts table
    op.create_table('posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vk_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('post_type', sa.String(length=20), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('comments_count', sa.Integer(), nullable=True),
        sa.Column('reposts_count', sa.Integer(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for posts table
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=False)
    op.create_index(op.f('ix_posts_vk_id'), 'posts', ['vk_id'], unique=False)
    op.create_index(op.f('ix_posts_group_id'), 'posts', ['group_id'], unique=False)


def downgrade() -> None:
    """Drop posts table"""
    
    # Drop indexes
    op.drop_index(op.f('ix_posts_group_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_vk_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_id'), table_name='posts')
    
    # Drop table
    op.drop_table('posts')
