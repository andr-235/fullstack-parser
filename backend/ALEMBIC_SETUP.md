# Alembic Setup Guide - Best Practices 2025

This guide explains how to set up and use Alembic for database migrations in the VK Parser Backend project.

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have the following installed:
- Python 3.11+
- PostgreSQL
- Poetry (for dependency management)

### 2. Environment Setup

Create a `.env` file with your database configuration:

```bash
# Database configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vk_parser
LOG_LEVEL=INFO

# Test database (optional)
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vk_parser_test
```

### 3. Install Dependencies

```bash
# Install project dependencies
poetry install

# Or with pip
pip install -r requirements.txt
```

### 4. Initialize Alembic

```bash
# Using the provided script
python scripts/init_alembic.py

# Or manually
alembic init alembic
```

### 5. Create Initial Migration

```bash
# Using the migration script
python scripts/migrate.py create "Initial migration"

# Or using Poetry
poetry run makemigrations "Initial migration"
```

### 6. Apply Migrations

```bash
# Using the migration script
python scripts/migrate.py up

# Or using Poetry
poetry run migrate
```

## 📁 Project Structure

```
backend/
├── alembic/
│   ├── versions/           # Migration files
│   ├── env.py             # Alembic environment configuration
│   ├── script.py.mako     # Migration template
│   ├── test.ini           # Test configuration
│   └── README.md          # Alembic documentation
├── scripts/
│   ├── migrate.py         # Migration management script
│   ├── init_alembic.py    # Alembic initialization script
│   └── test_migrations.py # Migration testing script
├── src/
│   └── shared/
│       └── infrastructure/
│           └── database/
│               └── base.py # SQLAlchemy Base class
├── alembic.ini            # Main Alembic configuration
├── pyproject.toml         # Poetry configuration with Alembic settings
└── Makefile.migrations    # Makefile for migration commands
```

## 🛠️ Configuration Files

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

## 🔧 Usage Commands

### Basic Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# Show current status
alembic current

# Show migration history
alembic history
```

### Using Migration Scripts

```bash
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

### Using Poetry Scripts

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

### Using Makefile

```bash
# Apply migrations
make -f Makefile.migrations migrate-up

# Create migration
make -f Makefile.migrations migrate-create MESSAGE="Add new table"

# Show status
make -f Makefile.migrations migrate-status

# Show history
make -f Makefile.migrations migrate-history
```

## 🧪 Testing Migrations

### Test Database Setup

1. Create test database:
```sql
CREATE DATABASE vk_parser_test;
```

2. Run migration tests:
```bash
python scripts/test_migrations.py
```

### Test Configuration

Use `alembic/test.ini` for test-specific configuration:
```bash
alembic -c alembic/test.ini upgrade head
```

## 📋 Best Practices

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

## 🔍 Troubleshooting

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

## 🌟 Features

### Async Support

Full async/await support for SQLAlchemy 2.0:
- Async engine creation
- Connection pooling
- Proper error handling

### Auto-formatting

Automatic code formatting with Black and linting with Ruff:
- Consistent code style
- Automatic fixes
- Pre-commit hooks

### Timezone Support

UTC timezone for consistent timestamps:
- Migration file names
- Migration content
- Database timestamps

### Connection Pooling

Optimized connection pooling for better performance:
- Pool size configuration
- Connection recycling
- Timeout settings

### Error Handling

Comprehensive error handling and logging:
- Detailed error messages
- Stack traces
- Graceful degradation

### Autogenerate

Smart autogenerate with type comparison and server defaults:
- Type comparison
- Server default comparison
- Object filtering

## 📚 Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

When contributing to migrations:

1. Always test migrations before committing
2. Use descriptive migration names
3. Provide both upgrade and downgrade functions
4. Follow the established naming conventions
5. Update this documentation if needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
