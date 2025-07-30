#!/bin/bash

# =============================================================================
# Database Migration Script for NestJS Backend
# =============================================================================

set -e

echo "🚀 Starting database migration..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    exit 1
fi

# Generate Prisma client
echo "📦 Generating Prisma client..."
npx prisma generate

# Run database migrations
echo "🔄 Running database migrations..."
npx prisma migrate deploy

# Verify database connection
echo "✅ Verifying database connection..."
npx prisma db seed --preview-feature

echo "🎉 Database migration completed successfully!" 