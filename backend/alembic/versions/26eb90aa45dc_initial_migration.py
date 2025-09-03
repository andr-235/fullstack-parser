"""Initial migration

Revision ID: 26eb90aa45dc
Revises: 05f77fc9bc66
Create Date: 2025-09-03 12:11:38.782640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26eb90aa45dc'
down_revision: Union[str, Sequence[str], None] = '05f77fc9bc66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
