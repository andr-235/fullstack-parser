"""initial_migration_001

Revision ID: 001_initial_migration_001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "001_initial_migration_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is a placeholder migration to match the version in the database
    pass


def downgrade() -> None:
    # This is a placeholder migration to match the version in the database
    pass
