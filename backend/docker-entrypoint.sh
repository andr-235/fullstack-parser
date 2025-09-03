#!/bin/bash
set -e

# Function to run FastAPI application
run_fastapi() {
    echo "🚀 Starting FastAPI application..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to run ARQ worker
run_arq_worker() {
    echo "⚡ Starting ARQ worker..."
    exec arq src.arq_tasks.worker.worker_settings "$@"
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
    "arq"|"worker")
        shift
        run_arq_worker "$@"
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
