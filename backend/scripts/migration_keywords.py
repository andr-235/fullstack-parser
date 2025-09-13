"""add_missing_columns_to_keywords

Revision ID: 13a317881bd9
Revises: 05f77fc9bc66
Create Date: 2025-08-27 18:08:43.399530

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "13a317881bd9"
down_revision: Union[str, Sequence[str], None] = "05f77fc9bc66"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем недостающие колонки в таблицу keywords
    op.add_column("keywords", sa.Column("category", sa.String(100), nullable=True))
    op.add_column("keywords", sa.Column("description", sa.Text, nullable=True))
    op.add_column(
        "keywords",
        sa.Column(
            "is_case_sensitive", sa.Boolean, nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "keywords",
        sa.Column("is_whole_word", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "keywords",
        sa.Column("total_matches", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем добавленные колонки
    op.drop_column("keywords", "total_matches")
    op.drop_column("keywords", "is_whole_word")
    op.drop_column("keywords", "is_case_sensitive")
    op.drop_column("keywords", "description")
    op.drop_column("keywords", "category")
