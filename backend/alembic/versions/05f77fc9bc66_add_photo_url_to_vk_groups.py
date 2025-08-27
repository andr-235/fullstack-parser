"""add_photo_url_to_vk_groups

Revision ID: 05f77fc9bc66
Revises: 2911c79d1296
Create Date: 2025-08-27 17:23:00.873685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05f77fc9bc66"
down_revision: Union[str, Sequence[str], None] = "2911c79d1296"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем колонку photo_url в таблицу vk_groups
    op.add_column(
        "vk_groups", sa.Column("photo_url", sa.String(500), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем колонку photo_url из таблицы vk_groups
    op.drop_column("vk_groups", "photo_url")
