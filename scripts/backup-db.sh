#!/bin/bash
# =============================================================================
# Database Backup Script for VK Parser API
# Automated backup with retention policy
# =============================================================================

set -euo pipefail

# Configuration
COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
DB_NAME="vk_parser"
DB_USER="postgres"
RETENTION_DAYS=7
LOG_FILE="./logs/backup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Check if PostgreSQL container is running
check_postgres() {
    log "Checking PostgreSQL container status..."
    
    if ! docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log_error "PostgreSQL container is not running"
        exit 1
    fi
    
    log_success "PostgreSQL container is running"
}

# Create backup directory
create_backup_dir() {
    log "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
    log_success "Backup directory ready"
}

# Create database backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/db_backup_${timestamp}.sql"
    local compressed_file="$backup_file.gz"
    
    log "Creating database backup: $backup_file"
    
    # Create SQL dump
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain > "$backup_file" 2>/dev/null; then
        
        log_success "Database dump created successfully"
        
        # Compress the backup
        if gzip "$backup_file"; then
            log_success "Backup compressed: $compressed_file"
            
            # Get file size
            local file_size=$(du -h "$compressed_file" | cut -f1)
            log "Backup size: $file_size"
            
            # Verify backup integrity
            if gzip -t "$compressed_file"; then
                log_success "Backup integrity verified"
                return 0
            else
                log_error "Backup integrity check failed"
                rm -f "$compressed_file"
                return 1
            fi
        else
            log_error "Failed to compress backup"
            rm -f "$backup_file"
            return 1
        fi
    else
        log_error "Failed to create database backup"
        return 1
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    local deleted_count=0
    
    # Find and delete old backup files
    while IFS= read -r -d '' file; do
        if rm "$file"; then
            deleted_count=$((deleted_count + 1))
            log "Deleted old backup: $(basename "$file")"
        fi
    done < <(find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    if [ $deleted_count -gt 0 ]; then
        log_success "Cleaned up $deleted_count old backup(s)"
    else
        log "No old backups to clean up"
    fi
}

# List current backups
list_backups() {
    log "Current backups:"
    
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        ls -lah "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | while read -r line; do
            log "  $line"
        done
    else
        log_warning "No backups found"
    fi
}

# Restore from backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log "Restoring database from backup: $backup_file"
    
    # Check if backup is compressed
    if [[ "$backup_file" == *.gz ]]; then
        log "Decompressing backup..."
        if ! gunzip -c "$backup_file" | docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U "$DB_USER" -d postgres; then
            log_error "Failed to restore from compressed backup"
            exit 1
        fi
    else
        if ! docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U "$DB_USER" -d postgres < "$backup_file"; then
            log_error "Failed to restore from backup"
            exit 1
        fi
    fi
    
    log_success "Database restored successfully from $backup_file"
}

# Main backup function
main() {
    log "Starting database backup process..."
    
    check_postgres
    create_backup_dir
    
    if create_backup; then
        cleanup_old_backups
        list_backups
        log_success "Backup process completed successfully! 💾"
    else
        log_error "Backup process failed!"
        exit 1
    fi
}

# Handle script arguments
case "${1:-backup}" in
    "backup")
        main
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "list")
        list_backups
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo ""
        echo "Commands:"
        echo "  backup              Create a new database backup (default)"
        echo "  restore <file>      Restore database from backup file"
        echo "  list                List all available backups"
        echo "  cleanup             Clean up old backups"
        echo "  help                Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore ./backups/db_backup_20240101_120000.sql.gz"
        echo "  $0 list"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
