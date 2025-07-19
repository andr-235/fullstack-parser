#!/bin/bash

# =============================================================================
# Development Environment Stop Script
# =============================================================================

set -e

echo "🛑 Stopping development environment..."

# Stop all services
docker-compose -f docker-compose.dev.yml down --remove-orphans

# Clean up volumes (optional)
read -p "Do you want to remove volumes? This will delete all data (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing volumes..."
    docker-compose -f docker-compose.dev.yml down -v
    docker volume prune -f
fi

# Clean up images (optional)
read -p "Do you want to remove development images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Removing development images..."
    docker image prune -f
fi

echo "✅ Development environment stopped!" 