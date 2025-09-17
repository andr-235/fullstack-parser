"""Create comments table

Revision ID: 0133_create_comments_table
Revises: 0132_create_users_table
Create Date: 2025-01-14 01:27:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0133_create_comments_table'
down_revision = '0132_create_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create comments and comment_keyword_matches tables"""
    
    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vk_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vk_id')
    )
    
    # Create indexes for comments table
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_index(op.f('ix_comments_vk_id'), 'comments', ['vk_id'], unique=True)
    op.create_index(op.f('ix_comments_group_id'), 'comments', ['group_id'], unique=False)
    op.create_index(op.f('ix_comments_post_id'), 'comments', ['post_id'], unique=False)
    op.create_index(op.f('ix_comments_author_id'), 'comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_comments_created_at'), 'comments', ['created_at'], unique=False)
    op.create_index(op.f('ix_comments_is_deleted'), 'comments', ['is_deleted'], unique=False)
    
    # Create comment_keyword_matches table
    op.create_table('comment_keyword_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(length=255), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for comment_keyword_matches table
    op.create_index(op.f('ix_comment_keyword_matches_id'), 'comment_keyword_matches', ['id'], unique=False)
    op.create_index(op.f('ix_comment_keyword_matches_comment_id'), 'comment_keyword_matches', ['comment_id'], unique=False)
    op.create_index(op.f('ix_comment_keyword_matches_keyword'), 'comment_keyword_matches', ['keyword'], unique=False)
    op.create_index('ix_comment_keyword', 'comment_keyword_matches', ['comment_id', 'keyword'], unique=False)
    op.create_index('ix_keyword_confidence', 'comment_keyword_matches', ['keyword', 'confidence'], unique=False)


def downgrade() -> None:
    """Drop comments and comment_keyword_matches tables"""
    
    # Drop comment_keyword_matches table and its indexes
    op.drop_index('ix_keyword_confidence', table_name='comment_keyword_matches')
    op.drop_index('ix_comment_keyword', table_name='comment_keyword_matches')
    op.drop_index(op.f('ix_comment_keyword_matches_keyword'), table_name='comment_keyword_matches')
    op.drop_index(op.f('ix_comment_keyword_matches_comment_id'), table_name='comment_keyword_matches')
    op.drop_index(op.f('ix_comment_keyword_matches_id'), table_name='comment_keyword_matches')
    op.drop_table('comment_keyword_matches')
    
    # Drop comments table and its indexes
    op.drop_index(op.f('ix_comments_is_deleted'), table_name='comments')
    op.drop_index(op.f('ix_comments_created_at'), table_name='comments')
    op.drop_index(op.f('ix_comments_author_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_post_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_group_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_vk_id'), table_name='comments')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
