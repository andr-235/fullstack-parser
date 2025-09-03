#!/bin/bash
set -e

# Function to run database migrations
run_migrations() {
    echo "🗄️ Running database migrations..."
    if alembic -c /app/alembic.ini upgrade head; then
        echo "✅ Database migrations completed successfully"
    else
        echo "❌ Database migrations failed, but continuing..."
    fi
}

# Function to run FastAPI application
run_fastapi() {
    echo "🚀 Starting FastAPI application..."

    # Run migrations before starting the app
    run_migrations

    echo "🌐 Starting uvicorn server..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
}


# Function to run Celery worker
run_celery_worker() {
    echo "🚀 Starting Celery worker..."
    exec /app/.venv/bin/celery "$@"
}

# Main entrypoint logic
case "$1" in
    "uvicorn"|"fastapi")
        shift
        run_fastapi "$@"
        ;;
    "celery")
        shift
        run_celery_worker "$@"
        ;;
    *)
        # Default to FastAPI if no specific command
        echo "Unknown command: $1"
        echo "Available commands: uvicorn, fastapi, arq, worker, celery"
        exit 1
        ;;
esac
