"""
Alembic environment configuration for VK Parser Backend.

This module configures Alembic to work with our FastAPI + SQLAlchemy 2.0 setup.
It handles both online and offline migration modes with proper async support.
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import only the base class and specific models that should be managed by Alembic
from src.models import Base
from src.auth.models import UserModel
from src.parser.models import ParsingTaskModel
from src.authors.models import Author

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Base.metadata


# Get database URL from environment or config
def get_database_url() -> str:
    """Get database URL from environment variables or config file."""
    # Try environment variables first (for different environments)
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Fallback to config file
        database_url = config.get_main_option("sqlalchemy.url")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable or sqlalchemy.url in alembic.ini must be set"
        )

    return database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    By skipping the Engine creation we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enable autogenerate for better migration detection
        compare_type=True,
        compare_server_default=True,
        # Include object names in migration comments
        include_object=include_object,
        # Process revision directives
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    url = get_database_url()

    # Create async engine with proper configuration
    connectable = create_async_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,  # Set to True for SQL debugging
    )

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enable autogenerate features
            compare_type=True,
            compare_server_default=True,
            # Include object names in migration comments
            include_object=include_object,
            # Process revision directives
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def include_object(object, name, type_, reflected, compare_to):
    """Filter objects to include in migrations."""
    # Skip certain objects if needed
    if type_ == "table" and name.startswith("alembic_version"):
        return False

    # Include all other objects
    return True


def process_revision_directives(context, revision, directives):
    """Process revision directives for better migration management."""
    # Add custom processing if needed
    pass


# Main execution logic
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run migrations online with proper error handling
    try:
        asyncio.run(run_migrations_online())
    except Exception as e:
        # Log error but don't fail during autogenerate
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Migration execution failed: {e}")

        # Only raise if not in autogenerate mode
        if not context.get_x_argument(as_dictionary=True).get("autogenerate"):
            raise
