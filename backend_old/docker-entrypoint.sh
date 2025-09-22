#!/bin/bash
set -euo pipefail

# =============================================================================
# Production-Ready Entrypoint Script for FastAPI Backend
# =============================================================================

# Global variables
APP_PID=""
SHUTDOWN_TIMEOUT=30

# Signal handlers for graceful shutdown
cleanup() {
    echo "🛑 Received shutdown signal, initiating graceful shutdown..."
    
    if [ -n "$APP_PID" ]; then
        echo "🔄 Stopping application (PID: $APP_PID)..."
        kill -TERM "$APP_PID" 2>/dev/null || true
        
        # Wait for graceful shutdown
        local count=0
        while kill -0 "$APP_PID" 2>/dev/null && [ $count -lt $SHUTDOWN_TIMEOUT ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$APP_PID" 2>/dev/null; then
            echo "⚠️ Force killing application after timeout"
            kill -KILL "$APP_PID" 2>/dev/null || true
        fi
    fi
    
    echo "✅ Graceful shutdown completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Function to run database migrations
run_migrations() {
    echo "🗄️ Running database migrations..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if timeout 5 bash -c "</dev/tcp/postgres/5432" >/dev/null 2>&1; then
            echo "✅ Database connection established"
            break
        else
            echo "⏳ Waiting for database... (attempt $attempt/$max_attempts)"
            sleep 2
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Database connection failed after $max_attempts attempts"
        exit 1
    fi
    
    # Run migrations with verbose output
    echo "🔍 Running alembic command: alembic -c /app/alembic.ini upgrade head"
    if alembic -c /app/alembic.ini upgrade head; then
        echo "✅ Database migrations completed successfully"
    else
        echo "❌ Database migrations failed"
        echo "🔍 Checking current alembic state..."
        alembic -c /app/alembic.ini current 2>/dev/null || echo "No current revision found"
        echo "🔍 Listing available revisions..."
        alembic -c /app/alembic.ini heads 2>/dev/null || echo "Failed to get heads"
        exit 1
    fi
}

# Function to run FastAPI application
run_fastapi() {
    echo "🚀 Starting FastAPI application..."
    
    # Run migrations before starting the app
    run_migrations
    
    echo "🌐 Starting uvicorn server..."
    
    # Start uvicorn in background and capture PID
    uvicorn src.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 1 \
        --access-log \
        --log-level info \
        --no-use-colors \
        --loop uvloop \
        --http httptools &
    
    APP_PID=$!
    echo "📝 Application started with PID: $APP_PID"
    
    # Wait for the application to finish
    wait $APP_PID
}

# Function to run Celery worker
run_celery_worker() {
    echo "🚀 Starting Celery worker..."
    exec /app/.venv/bin/celery "$@"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Available commands:"
    echo "  fastapi, uvicorn    Start FastAPI application (default)"
    echo "  celery             Start Celery worker"
    echo "  help               Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  DATABASE_URL       Database connection URL"
    echo "  REDIS_URL          Redis connection URL"
    echo "  SENTRY_DSN         Sentry DSN for error tracking"
}

# Main entrypoint logic
case "${1:-fastapi}" in
    "uvicorn"|"fastapi")
        shift
        run_fastapi "$@"
        ;;
    "celery")
        shift
        run_celery_worker "$@"
        ;;
    "help"|"--help"|"-h")
        show_help
        exit 0
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
