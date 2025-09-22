#!/usr/bin/env python3
"""
Initialize Alembic for VK Parser Backend.

This script initializes Alembic with proper configuration
and creates the initial migration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from src.shared.config import settings


async def check_database_connection() -> bool:
    """Check if database connection is available."""
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def init_alembic() -> bool:
    """Initialize Alembic configuration."""
    try:
        config = Config("alembic.ini")
        
        # Check if alembic is already initialized
        if config.get_main_option("script_location"):
            print("✅ Alembic is already initialized")
            return True
        
        print("❌ Alembic configuration not found")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize Alembic: {e}")
        return False


def create_initial_migration() -> bool:
    """Create initial migration."""
    try:
        config = Config("alembic.ini")
        command.revision(config, message="Initial migration", autogenerate=True)
        print("✅ Initial migration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create initial migration: {e}")
        return False


async def main():
    """Main function."""
    print("🚀 Initializing Alembic for VK Parser Backend")
    print("=" * 50)
    
    # Check database connection
    if not await check_database_connection():
        print("Please check your database configuration and try again")
        return
    
    # Check Alembic configuration
    if not init_alembic():
        print("Please run 'alembic init alembic' first")
        return
    
    # Create initial migration
    if create_initial_migration():
        print("\n🎉 Alembic initialization completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated migration file in alembic/versions/")
        print("2. Apply the migration: python scripts/migrate.py up")
        print("3. Check status: python scripts/migrate.py status")
    else:
        print("❌ Failed to create initial migration")


if __name__ == "__main__":
    asyncio.run(main())
