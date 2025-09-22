#!/usr/bin/env python3
"""
Database migration management script for VK Parser Backend.

This script provides convenient commands for managing database migrations
using Alembic with proper async support and error handling.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy.ext.asyncio import create_async_engine
from src.shared.config import settings


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    config = Config("alembic.ini")
    return config


async def check_database_connection() -> bool:
    """Check if database connection is available."""
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def get_current_revision() -> Optional[str]:
    """Get current database revision."""
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
        await engine.dispose()
        return current_rev
    except Exception as e:
        print(f"Failed to get current revision: {e}")
        return None


async def get_head_revision() -> Optional[str]:
    """Get head revision from migration files."""
    try:
        config = get_alembic_config()
        from alembic.script import ScriptDirectory
        script = ScriptDirectory.from_config(config)
        head = script.get_current_head()
        return head
    except Exception as e:
        print(f"Failed to get head revision: {e}")
        return None


async def migrate_up(target: str = "head") -> bool:
    """Run migrations up to target revision."""
    if not await check_database_connection():
        return False
    
    try:
        config = get_alembic_config()
        command.upgrade(config, target)
        print(f"Successfully migrated to {target}")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False


async def migrate_down(target: str = "-1") -> bool:
    """Run migrations down to target revision."""
    if not await check_database_connection():
        return False
    
    try:
        config = get_alembic_config()
        command.downgrade(config, target)
        print(f"Successfully downgraded to {target}")
        return True
    except Exception as e:
        print(f"Downgrade failed: {e}")
        return False


async def create_migration(message: str) -> bool:
    """Create a new migration."""
    if not await check_database_connection():
        return False
    
    try:
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        print(f"Successfully created migration: {message}")
        return True
    except Exception as e:
        print(f"Migration creation failed: {e}")
        return False


async def show_status() -> None:
    """Show migration status."""
    current = await get_current_revision()
    head = await get_head_revision()
    
    print(f"Current revision: {current}")
    print(f"Head revision: {head}")
    
    if current == head:
        print("Database is up to date")
    else:
        print("Database is not up to date")


async def show_history() -> None:
    """Show migration history."""
    try:
        config = get_alembic_config()
        command.history(config)
    except Exception as e:
        print(f"Failed to show history: {e}")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command> [args]")
        print("Commands:")
        print("  up [target]     - Migrate up to target (default: head)")
        print("  down [target]   - Migrate down to target (default: -1)")
        print("  create <message> - Create new migration")
        print("  status          - Show migration status")
        print("  history         - Show migration history")
        return
    
    command_name = sys.argv[1]
    
    if command_name == "up":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        await migrate_up(target)
    elif command_name == "down":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        await migrate_down(target)
    elif command_name == "create":
        if len(sys.argv) < 3:
            print("Please provide a migration message")
            return
        message = sys.argv[2]
        await create_migration(message)
    elif command_name == "status":
        await show_status()
    elif command_name == "history":
        await show_history()
    else:
        print(f"Unknown command: {command_name}")


if __name__ == "__main__":
    asyncio.run(main())