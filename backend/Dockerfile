# =============================================================================
# Optimized Production Dockerfile for FastAPI Backend with Poetry and ARQ Worker
# =============================================================================

# Build stage
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential \
 curl \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry \
 POETRY_VIRTUALENVS_IN_PROJECT=true \
 POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry==1.8.3

# Set working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create virtual environment in project
RUN poetry config virtualenvs.create true
RUN poetry config virtualenvs.in-project true

# Install dependencies and create virtual environment
RUN poetry install --only=main --no-dev

# Production stage
FROM python:3.11-slim AS runtime

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
 curl \
 && rm -rf /var/lib/apt/lists/*

# Create non-privileged user
ARG UID=10001
RUN groupadd --gid $UID appuser \
 && useradd --uid $UID --gid $UID --create-home --shell /bin/bash appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
 PYTHONDONTWRITEBYTECODE=1 \
 PYTHONPATH=/app/src \
 PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/

# Copy Alembic configuration
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Switch to non-privileged user
USER appuser

# Health check for the FastAPI application
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
 CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["fastapi"]
