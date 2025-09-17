"""Initial migration

Revision ID: 1d3c4329d09c
Revises: make_published_at_nullable
Create Date: 2025-09-12 08:02:21.652617+00:00

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "1d3c4329d09c"
down_revision: Union[str, Sequence[str], None] = "make_published_at_nullable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
