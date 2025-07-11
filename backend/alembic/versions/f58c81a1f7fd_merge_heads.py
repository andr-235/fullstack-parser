"""merge heads

Revision ID: f58c81a1f7fd
Revises: 18c97baa177b, 84629a3c9ad3
Create Date: 2025-07-07 10:22:00.939593

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f58c81a1f7fd"
down_revision: Union[str, None] = "84629a3c9ad3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
