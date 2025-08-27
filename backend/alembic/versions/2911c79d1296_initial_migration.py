"""Initial migration

Revision ID: 2911c79d1296
Revises: 
Create Date: 2025-08-27 16:21:46.123456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2911c79d1296"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables."""

    # Таблица пользователей
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Таблица ключевых слов
    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("word", sa.String(255), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("word"),
    )

    # Таблица VK групп
    op.create_table(
        "vk_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vk_id", sa.Integer(), nullable=False),
        sa.Column("screen_name", sa.String(255), nullable=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vk_id"),
    )

    # Таблица VK авторов
    op.create_table(
        "vk_authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vk_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("screen_name", sa.String(255), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vk_id"),
    )

    # Таблица VK постов
    op.create_table(
        "vk_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vk_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["vk_groups.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "vk_id", "group_id", name="uix_vkpost_vkid_groupid"
        ),
    )

    # Таблица VK комментариев
    op.create_table(
        "vk_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vk_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column(
            "is_archived", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "is_viewed", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["vk_authors.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["post_id"], ["vk_posts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vk_id"),
    )

    # Таблица связей комментариев с ключевыми словами
    op.create_table(
        "comment_keyword_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("keyword_id", sa.Integer(), nullable=False),
        sa.Column("matched_text", sa.String(500), nullable=True),
        sa.Column("match_position", sa.Integer(), nullable=True),
        sa.Column("match_context", sa.String(1000), nullable=True),
        sa.Column(
            "found_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["vk_comments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["keyword_id"], ["keywords.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица ошибок
    op.create_table(
        "error_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("error_type", sa.String(100), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("context_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица отчетов об ошибках
    op.create_table(
        "error_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(50), nullable=False, server_default="open"
        ),
        sa.Column(
            "priority", sa.String(20), nullable=False, server_default="medium"
        ),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Создаем индексы
    op.create_index(
        "ix_vk_comments_is_archived", "vk_comments", ["is_archived"]
    )
    op.create_index("ix_vk_comments_is_viewed", "vk_comments", ["is_viewed"])
    op.create_index(
        "ix_vk_comments_post_id_created_at",
        "vk_comments",
        ["post_id", "created_at"],
    )
    op.create_index("ix_vk_groups_vk_id", "vk_groups", ["vk_id"])
    op.create_index("ix_vk_posts_vk_id", "vk_posts", ["vk_id"])
    op.create_index("ix_vk_authors_vk_id", "vk_authors", ["vk_id"])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("comment_keyword_matches")
    op.drop_table("vk_comments")
    op.drop_table("vk_posts")
    op.drop_table("vk_authors")
    op.drop_table("vk_groups")
    op.drop_table("keywords")
    op.drop_table("error_reports")
    op.drop_table("error_entries")
    op.drop_table("users")
