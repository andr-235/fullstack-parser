"""update_keywords_table_structure

Revision ID: 128983c4a464
Revises: 7bd888354bf6
Create Date: 2025-09-08 16:48:57.800415

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "128983c4a464"
down_revision: Union[str, Sequence[str], None] = "7bd888354bf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем новые колонки в таблицу keywords
    op.add_column(
        "keywords", sa.Column("category_name", sa.String(100), nullable=True)
    )
    op.add_column(
        "keywords", sa.Column("category_description", sa.Text(), nullable=True)
    )
    op.add_column(
        "keywords",
        sa.Column(
            "priority", sa.Integer(), nullable=False, server_default="5"
        ),
    )
    op.add_column(
        "keywords",
        sa.Column(
            "match_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "keywords",
        sa.Column(
            "is_archived", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "keywords", sa.Column("group_id", sa.Integer(), nullable=True)
    )

    # Создаем индексы
    op.create_index("ix_keywords_category_name", "keywords", ["category_name"])
    op.create_index("ix_keywords_group_id", "keywords", ["group_id"])

    # Удаляем старые колонки, которые больше не нужны
    op.drop_column("keywords", "category")
    op.drop_column("keywords", "is_case_sensitive")
    op.drop_column("keywords", "is_whole_word")
    op.drop_column("keywords", "total_matches")


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем старые колонки
    op.add_column(
        "keywords", sa.Column("category", sa.String(100), nullable=True)
    )
    op.add_column(
        "keywords",
        sa.Column(
            "is_case_sensitive",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "keywords",
        sa.Column(
            "is_whole_word",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "keywords",
        sa.Column(
            "total_matches", sa.Integer(), nullable=False, server_default="0"
        ),
    )

    # Удаляем индексы
    op.drop_index("ix_keywords_group_id", "keywords")
    op.drop_index("ix_keywords_category_name", "keywords")

    # Удаляем новые колонки
    op.drop_column("keywords", "group_id")
    op.drop_column("keywords", "is_archived")
    op.drop_column("keywords", "match_count")
    op.drop_column("keywords", "priority")
    op.drop_column("keywords", "category_description")
    op.drop_column("keywords", "category_name")
