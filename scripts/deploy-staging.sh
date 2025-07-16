#!/bin/bash
set -e

echo "🚀 Deploying to staging..."

# Pull latest images
docker-compose -f docker-compose.yml pull

# Update services with zero downtime
docker-compose -f docker-compose.yml up -d --remove-orphans

# Health check
timeout 60 bash -c 'until curl -f http://localhost:8001/api/v1/health > /dev/null 2>&1; do sleep 2; done'
timeout 60 bash -c 'until curl -f http://localhost:3001 > /dev/null 2>&1; do sleep 2; done'

echo "✅ Staging deployment completed"
