#!/bin/bash

# =============================================================================
# Production Deployment Script for NestJS Backend
# =============================================================================

set -e

echo "🚀 Starting production deployment..."

# Load environment variables
if [ -f .env.prod ]; then
    echo "📋 Loading production environment variables..."
    export $(cat .env.prod | grep -v '^#' | xargs)
else
    echo "❌ Error: .env.prod file not found"
    exit 1
fi

# Build and deploy with Docker Compose
echo "🐳 Building and deploying with Docker Compose..."
docker-compose -f docker-compose.prod.ip.yml build --no-cache

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.ip.yml down

# Start services
echo "▶️ Starting services..."
docker-compose -f docker-compose.prod.ip.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose -f docker-compose.prod.ip.yml exec -T backend npx prisma migrate deploy

# Verify deployment
echo "✅ Verifying deployment..."
docker-compose -f docker-compose.prod.ip.yml ps

echo "🎉 Production deployment completed successfully!"
echo "📊 Application is running at: http://${SERVER_IP:-localhost}"
echo "📚 API Documentation: http://${SERVER_IP:-localhost}/api/docs" 