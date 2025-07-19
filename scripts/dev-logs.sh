#!/bin/bash

# =============================================================================
# Development Environment Logs Script
# =============================================================================

# Default service to show logs for
SERVICE=${1:-""}

echo "📋 Development environment logs"

if [ -z "$SERVICE" ]; then
    echo "Showing logs for all services..."
    echo "Usage: $0 [service_name]"
    echo "Available services: postgres, redis, backend, arq_worker, frontend, nginx"
    echo ""
    docker-compose -f docker-compose.dev.yml logs -f
else
    echo "Showing logs for service: $SERVICE"
    docker-compose -f docker-compose.dev.yml logs -f "$SERVICE"
fi 