# Project Instructions

## Code Style

- Use TypeScript for all frontend files (Next.js) and Python for backend (FastAPI).
- Use functional components and hooks in React.
- Follow snake_case for database columns.
- Apply linters and formatters: `black` for Python, `eslint` and `prettier` for TypeScript.
- Keep code clean, readable, and maintainable.

## Architecture

- Use a layered architecture: controllers → services → repositories → models.
- Business logic resides in services.
- Repositories handle database access only.
- Controllers handle request/response only.
- For database, use PostgreSQL with SQLAlchemy and Alembic for migrations.

## Git Workflow

- Always create a feature branch before starting a task.
- Merge feature branch into main/master after task completion.
- Close the branch after merging.
- Write meaningful commit messages using conventional commits.

## Testing

- Write unit tests for all critical functions.
- Integration tests for API endpoints.
- Aim for at least 80% code coverage.

## Deployment

- All deployments are production-ready.
- Ensure environment variables are used instead of hardcoding secrets.
- Health checks must be implemented for backend services.
