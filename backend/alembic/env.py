"""
Alembic environment configuration for async SQLAlchemy
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import all models to ensure they are registered
try:
    from src.shared.infrastructure.database.base import Base
    # Import all models through the models module
    from src import models  # This imports all models
except ImportError as e:
    print(f"Warning: Could not import models: {e}")
    # Fallback: create minimal metadata
    from sqlalchemy import MetaData
    Base = MetaData()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata if hasattr(Base, 'metadata') else Base

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    import os
    
    # Get database URL from environment or config
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback to config file
        config_dict = config.get_section(config.config_ini_section, {})
        database_url = config_dict.get("sqlalchemy.url")
    
    # Ensure asyncpg URL for Alembic
    if database_url and "postgresql://" in database_url and "postgresql+asyncpg://" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"Using database URL: {database_url}")
    
    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
