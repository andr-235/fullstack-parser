"""Add author-comment relationship

Revision ID: add_author_comment_relationship
Revises: 1d3c4329d09c
Create Date: 2025-09-13 15:37:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_author_comment_relationship'
down_revision = '1d3c4329d09c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add foreign key constraint from comments to authors"""
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_comments_author_id',
        'comments', 'authors',
        ['author_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Add index for better performance
    op.create_index(
        'ix_comments_author_id',
        'comments', ['author_id']
    )


def downgrade() -> None:
    """Remove foreign key constraint and index"""
    # Drop index
    op.drop_index('ix_comments_author_id', table_name='comments')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_comments_author_id', 'comments', type_='foreignkey')
