"""fix_timezone_fields_to_utc

Revision ID: 002_fix_timezone_fields_to_utc
Revises: 001_initial_migration_001
Create Date: 2025-07-28 14:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_fix_timezone_fields_to_utc"
down_revision = "001_initial_migration_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Изменяем типы времени на timestamp with time zone для правильной работы с UTC

    # VK Comments
    op.alter_column(
        "vk_comments",
        "published_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "vk_comments",
        "processed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_comments",
        "viewed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_comments",
        "archived_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # VK Posts
    op.alter_column(
        "vk_posts",
        "published_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "vk_posts",
        "parsed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    # VK Groups
    op.alter_column(
        "vk_groups",
        "next_monitoring_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_groups",
        "last_parsed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_groups",
        "last_monitoring_success",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Возвращаем обратно к timestamp without time zone

    # VK Comments
    op.alter_column(
        "vk_comments",
        "published_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "vk_comments",
        "processed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_comments",
        "viewed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_comments",
        "archived_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )

    # VK Posts
    op.alter_column(
        "vk_posts",
        "published_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "vk_posts",
        "parsed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )

    # VK Groups
    op.alter_column(
        "vk_groups",
        "next_monitoring_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_groups",
        "last_parsed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
    op.alter_column(
        "vk_groups",
        "last_monitoring_success",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
    )
