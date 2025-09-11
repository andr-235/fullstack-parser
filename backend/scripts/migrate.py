#!/usr/bin/env python3
"""
Database migration management script for VK Parser Backend.

This script provides convenient commands for managing database migrations
using Alembic with proper environment handling.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import config_service


def run_command(cmd: List[str], env: Optional[dict] = None) -> int:
    """Run a command with proper environment setup."""
    env = env or {}
    env.update(os.environ)

    # Set database URL from config if not already set
    if "DATABASE_URL" not in env:
        env["DATABASE_URL"] = config_service.database_url

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(
        cmd, env=env, cwd=Path(__file__).parent.parent
    ).returncode


def migrate_up(revision: str = "head") -> int:
    """Apply migrations up to specified revision."""
    return run_command(["alembic", "upgrade", revision])


def migrate_down(revision: str = "-1") -> int:
    """Downgrade migrations to specified revision."""
    return run_command(["alembic", "downgrade", revision])


def create_migration(message: str, autogenerate: bool = True) -> int:
    """Create a new migration."""
    cmd = ["alembic", "revision"]
    if autogenerate:
        cmd.append("--autogenerate")
    cmd.extend(["-m", message])
    return run_command(cmd)


def show_history() -> int:
    """Show migration history."""
    return run_command(["alembic", "history", "--verbose"])


def show_current() -> int:
    """Show current migration state."""
    return run_command(["alembic", "current"])


def show_migration(revision: str) -> int:
    """Show specific migration details."""
    return run_command(["alembic", "show", revision])


def merge_migrations(revisions: List[str], message: str) -> int:
    """Merge multiple migration heads."""
    cmd = ["alembic", "merge"] + revisions + ["-m", message]
    return run_command(cmd)


def stamp_revision(revision: str) -> int:
    """Stamp database with specific revision without running migrations."""
    return run_command(["alembic", "stamp", revision])


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Database migration management for VK Parser Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/migrate.py up                    # Apply all pending migrations
  python scripts/migrate.py up +1                 # Apply next migration
  python scripts/migrate.py down                  # Rollback last migration
  python scripts/migrate.py down base             # Rollback to base (empty database)
  python scripts/migrate.py create "Add user table"  # Create new migration
  python scripts/migrate.py history               # Show migration history
  python scripts/migrate.py current               # Show current state
  python scripts/migrate.py show abc123           # Show specific migration
  python scripts/migrate.py merge abc123 def456 "Merge migrations"  # Merge heads
  python scripts/migrate.py stamp abc123          # Stamp without running
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands"
    )

    # Up command
    up_parser = subparsers.add_parser("up", help="Apply migrations")
    up_parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Target revision (default: head)",
    )

    # Down command
    down_parser = subparsers.add_parser("down", help="Rollback migrations")
    down_parser.add_argument(
        "revision",
        nargs="?",
        default="-1",
        help="Target revision (default: -1)",
    )

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create new migration"
    )
    create_parser.add_argument("message", help="Migration message")
    create_parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Create empty migration without autogenerate",
    )

    # History command
    subparsers.add_parser("history", help="Show migration history")

    # Current command
    subparsers.add_parser("current", help="Show current migration state")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show specific migration")
    show_parser.add_argument("revision", help="Revision to show")

    # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge migration heads")
    merge_parser.add_argument(
        "revisions", nargs="+", help="Revisions to merge"
    )
    merge_parser.add_argument("message", help="Merge message")

    # Stamp command
    stamp_parser = subparsers.add_parser(
        "stamp", help="Stamp database with revision"
    )
    stamp_parser.add_argument("revision", help="Revision to stamp")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "up":
            return migrate_up(args.revision)
        elif args.command == "down":
            return migrate_down(args.revision)
        elif args.command == "create":
            return create_migration(args.message, not args.no_autogenerate)
        elif args.command == "history":
            return show_history()
        elif args.command == "current":
            return show_current()
        elif args.command == "show":
            return show_migration(args.revision)
        elif args.command == "merge":
            return merge_migrations(args.revisions, args.message)
        elif args.command == "stamp":
            return stamp_revision(args.revision)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\nMigration interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
