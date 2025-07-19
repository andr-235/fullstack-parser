#!/bin/bash

# =============================================================================
# Development Environment Startup Script
# =============================================================================

set -e

echo "🚀 Starting development environment..."

# Check if .env.dev exists
if [ ! -f .env.dev ]; then
    echo "❌ Error: .env.dev file not found!"
    echo "Please copy env.example to .env.dev and configure it"
    exit 1
fi

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker-compose -f docker-compose.dev.yml down --remove-orphans

# Clean up any dangling images
echo "🧹 Cleaning up dangling images..."
docker image prune -f

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check backend
echo "Checking backend..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -s http://localhost/api/v1/health/ > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    echo "⏳ Waiting for backend... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -eq $timeout ]; then
    echo "❌ Backend health check failed"
    docker-compose -f docker-compose.dev.yml logs backend
    exit 1
fi

# Check frontend
echo "Checking frontend..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -s http://localhost > /dev/null 2>&1; then
        echo "✅ Frontend is healthy"
        break
    fi
    echo "⏳ Waiting for frontend... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -eq $timeout ]; then
    echo "❌ Frontend health check failed"
    docker-compose -f docker-compose.dev.yml logs frontend
    exit 1
fi

echo "🎉 Development environment is ready!"
echo ""
echo "📱 Frontend: http://localhost"
echo "🔧 Backend API: http://localhost/api/v1/"
echo "📊 Health Check: http://localhost/health"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.dev.yml down"
echo "  - Restart services: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "🔄 Hot reload is enabled for both frontend and backend!" 