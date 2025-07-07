#!/bin/bash
set -e

echo "🏭 Deploying to production..."

# Backup current state
./scripts/backup.sh

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Blue-green deployment
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Health check
timeout 120 bash -c 'until curl -f https://api.your-domain.com/health > /dev/null 2>&1; do sleep 5; done'
timeout 120 bash -c 'until curl -f https://your-domain.com > /dev/null 2>&1; do sleep 5; done'

echo "✅ Production deployment completed" 