#!/bin/bash

# Database backup script for VK Analyzer
# Creates database backup before production deployments

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="vk_analyzer_backup_$TIMESTAMP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
    log "Environment variables loaded from .env"
else
    error ".env file not found in $PROJECT_DIR"
    exit 1
fi

# Check if required variables are set
if [ -z "${POSTGRES_DB:-}" ] || [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_PASSWORD:-}" ]; then
    error "Missing required database environment variables (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
log "Backup directory: $BACKUP_DIR"

# Check if PostgreSQL container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    error "PostgreSQL container is not running"
    exit 1
fi

log "Starting database backup: $BACKUP_NAME"

# Create database backup
BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.sql"

log "Creating PostgreSQL dump..."
if docker-compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"; then
    log "Database backup created successfully: $BACKUP_FILE"
else
    error "Failed to create database backup"
    exit 1
fi

# Compress backup
log "Compressing backup..."
if gzip "$BACKUP_FILE"; then
    BACKUP_FILE="${BACKUP_FILE}.gz"
    log "Backup compressed: $BACKUP_FILE"
else
    warn "Failed to compress backup, keeping uncompressed version"
fi

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup size: $BACKUP_SIZE"

# Keep only last 5 backups
log "Cleaning up old backups (keeping last 5)..."
cd "$BACKUP_DIR"
ls -t vk_analyzer_backup_*.sql.gz 2>/dev/null | tail -n +6 | xargs rm -f || true
ls -t vk_analyzer_backup_*.sql 2>/dev/null | tail -n +6 | xargs rm -f || true

log "Backup completed successfully!"
log "Backup file: $BACKUP_FILE"
log "Backup size: $BACKUP_SIZE"

# List current backups
log "Available backups:"
ls -lah "$BACKUP_DIR"/vk_analyzer_backup_* 2>/dev/null || log "No previous backups found"

exit 0