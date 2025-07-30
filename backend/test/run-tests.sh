#!/bin/bash

# Test runner script for NestJS backend
# This script runs all integration tests and generates reports

set -e

echo "🚀 Starting NestJS Backend Integration Tests"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the backend directory."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Generate Prisma client
echo "🔧 Generating Prisma client..."
npx prisma generate

# Run database migrations
echo "🗄️ Running database migrations..."
npx prisma migrate dev --name test-setup

# Run unit tests
echo "🧪 Running unit tests..."
npm run test

# Run E2E tests
echo "🔍 Running E2E integration tests..."
npm run test:e2e

# Run performance tests
echo "⚡ Running performance tests..."
npm run test:e2e -- --testPathPattern=performance.e2e-spec.ts

# Generate coverage report
echo "📊 Generating coverage report..."
npm run test:cov

echo "✅ All tests completed successfully!"
echo "📈 Coverage report available in coverage/ directory"
echo "📋 Test results summary:"
echo "   - Unit tests: ✅"
echo "   - E2E tests: ✅"
echo "   - Performance tests: ✅"
echo "   - Coverage: Generated" 