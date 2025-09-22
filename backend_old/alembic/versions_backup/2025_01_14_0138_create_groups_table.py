"""Create groups table

Revision ID: 0138_create_groups_table
Revises: 0137_create_posts_table
Create Date: 2025-01-14 01:38:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0138_create_groups_table'
down_revision = '0137_create_posts_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create groups table"""
    
    # Create groups table
    op.create_table('groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vk_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('screen_name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('members_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vk_id'),
        sa.UniqueConstraint('screen_name')
    )
    
    # Create indexes for groups table
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=False)
    op.create_index(op.f('ix_groups_vk_id'), 'groups', ['vk_id'], unique=True)
    op.create_index(op.f('ix_groups_screen_name'), 'groups', ['screen_name'], unique=True)


def downgrade() -> None:
    """Drop groups table"""
    
    # Drop indexes
    op.drop_index(op.f('ix_groups_screen_name'), table_name='groups')
    op.drop_index(op.f('ix_groups_vk_id'), table_name='groups')
    op.drop_index(op.f('ix_groups_id'), table_name='groups')
    
    # Drop table
    op.drop_table('groups')
