"""merge all heads - make 20250116000000 the final head

Revision ID: 20250121000000
Revises: 20250116000000, 33ad0550f6f8
Create Date: 2025-01-21 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250121000000"
down_revision: Union[str, Sequence[str], None] = (
    "20250116000000",
    "33ad0550f6f8",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration - no schema changes needed
    pass


def downgrade() -> None:
    # This is a merge migration - no schema changes needed
    pass
