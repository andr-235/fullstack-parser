# Alembic Database Migrations

This directory contains database migration scripts for the VK Parser Backend project.

## Configuration

The Alembic configuration is optimized for FastAPI + SQLAlchemy 2.0 async setup with PostgreSQL and follows best practices 2025.

### Key Features

- **Async Support**: Full async/await support for SQLAlchemy 2.0
- **Auto-formatting**: Automatic code formatting with Black and linting with Ruff
- **Timezone Support**: UTC timezone for consistent timestamps
- **Connection Pooling**: Optimized connection pooling for better performance
- **Error Handling**: Comprehensive error handling and logging
- **Autogenerate**: Smart autogenerate with type comparison and server defaults

## Usage

### Basic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# Show current status
alembic current

# Show migration history
alembic history

# Show specific migration
alembic show <revision>
```

### Using the Migration Script

For convenience, use the provided migration script:

```bash
# Navigate to backend directory
cd backend

# Create new migration
python scripts/migrate.py create "Add new table"

# Apply migrations
python scripts/migrate.py up

# Downgrade
python scripts/migrate.py down

# Show status
python scripts/migrate.py status

# Show history
python scripts/migrate.py history
```

### Poetry Scripts

The project includes Poetry scripts for common operations:

```bash
# Create migration
poetry run makemigrations "Add new table"

# Apply migrations
poetry run migrate

# Downgrade
poetry run downgrade

# Show current revision
poetry run migration-current

# Show history
poetry run migration-history
```

## Configuration Files

### alembic.ini

Main configuration file with:
- Database URL (fallback)
- Migration file naming template
- Post-write hooks for formatting
- Logging configuration

### pyproject.toml

Modern configuration using PEP 621:
- Source code organization
- Post-write hooks
- Path separators

### env.py

Environment configuration with:
- Async engine setup
- Model imports
- Error handling
- Connection pooling

## Best Practices

### 1. Migration Naming

Use descriptive names for migrations:
```bash
alembic revision --autogenerate -m "Add user authentication table"
alembic revision --autogenerate -m "Add indexes for performance"
alembic revision --autogenerate -m "Rename column from old_name to new_name"
```

### 2. Model Imports

All SQLAlchemy models must be imported in `env.py`:
```python
from src.shared.infrastructure.database.base import Base
from src.authors.infrastructure.models.author_model import AuthorModel
from src.posts.infrastructure.models.post_model import PostModel
# ... other models
```

### 3. Async Operations

For async operations in migrations, use:
```python
def upgrade() -> None:
    # Use op.run_async() for async operations
    async with op.run_async() as conn:
        await conn.execute(text("SELECT 1"))
```

### 4. Data Migrations

For data migrations, use raw SQL:
```python
def upgrade() -> None:
    op.execute(text("UPDATE users SET status = 'active' WHERE status IS NULL"))
```

### 5. Reversible Migrations

Always provide downgrade functions:
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(255)))

def downgrade() -> None:
    op.drop_column('users', 'email')
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all models are imported in `env.py`
2. **Connection Errors**: Check database URL and connection settings
3. **Autogenerate Issues**: Verify model definitions and relationships
4. **Formatting Issues**: Ensure Black and Ruff are installed

### Debug Mode

Enable SQL logging by setting `echo=True` in `env.py`:
```python
connectable = create_async_engine(
    url,
    echo=True,  # Enable SQL logging
    # ... other options
)
```

### Manual Migration

If autogenerate fails, create manual migration:
```bash
alembic revision -m "Manual migration description"
```

## Environment Variables

- `DATABASE_URL`: Database connection URL
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Dependencies

- SQLAlchemy 2.0+
- Alembic 1.13+
- asyncpg (PostgreSQL driver)
- Black (code formatting)
- Ruff (linting)

## Migration Files

Migration files are stored in `versions/` directory and follow the naming pattern:
`YYYY_MM_DD_HHMM-<revision_id>_<description>.py`

Example: `2024_01_15_1430-abc123_add_user_table.py`
