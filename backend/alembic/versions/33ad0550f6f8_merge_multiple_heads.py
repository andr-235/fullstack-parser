"""merge multiple heads

Revision ID: 33ad0550f6f8
Revises: 20250115000000, 999999999999
Create Date: 2025-07-16 12:01:27.544426

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "33ad0550f6f8"
down_revision: Union[str, Sequence[str], None] = (
    "20250115000000",
    "51fcd6f1165b",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
