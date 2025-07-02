#!/bin/bash

# =============================================================================
# DATABASE BACKUP SCRIPT
# =============================================================================
# Автоматический backup PostgreSQL базы данных
# Использование: ./backup.sh [manual|auto]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
BACKUP_TYPE=${1:-"manual"}
BACKUP_DIR="/opt/app/backup"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
RETENTION_DAYS=30

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if .env.prod exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Production environment file ($ENV_FILE) not found"
        exit 1
    fi
    
    # Source environment variables
    source "$ENV_FILE"
    
    # Check if required variables are set
    if [[ -z "${DB_NAME:-}" ]] || [[ -z "${DB_USER:-}" ]] || [[ -z "${DB_PASSWORD:-}" ]]; then
        log_error "Database environment variables not set properly"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if postgres container exists
    if ! docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log_error "PostgreSQL container is not running"
        exit 1
    fi
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    log_success "Prerequisites check passed"
}

# =============================================================================
# BACKUP FUNCTIONS
# =============================================================================
create_sql_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/db_backup_${timestamp}.sql"
    
    log_info "Creating SQL backup..."
    
    # Create database dump
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --clean \
        --no-owner \
        --no-privileges \
        > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    local compressed_file="${backup_file}.gz"
    local file_size=$(du -h "$compressed_file" | cut -f1)
    
    log_success "SQL backup created: $compressed_file ($file_size)"
    echo "$compressed_file"
}

create_custom_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/db_backup_${timestamp}.dump"
    
    log_info "Creating custom format backup..."
    
    # Create custom format dump (smaller and faster)
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --verbose \
        --clean \
        --no-owner \
        --no-privileges \
        > "$backup_file"
    
    local file_size=$(du -h "$backup_file" | cut -f1)
    
    log_success "Custom backup created: $backup_file ($file_size)"
    echo "$backup_file"
}

create_schema_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/schema_backup_${timestamp}.sql"
    
    log_info "Creating schema-only backup..."
    
    # Create schema-only dump
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --schema-only \
        --verbose \
        --clean \
        --no-owner \
        --no-privileges \
        > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    local compressed_file="${backup_file}.gz"
    local file_size=$(du -h "$compressed_file" | cut -f1)
    
    log_success "Schema backup created: $compressed_file ($file_size)"
    echo "$compressed_file"
}

create_data_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/data_backup_${timestamp}.sql"
    
    log_info "Creating data-only backup..."
    
    # Create data-only dump
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --data-only \
        --verbose \
        --no-owner \
        --no-privileges \
        > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    local compressed_file="${backup_file}.gz"
    local file_size=$(du -h "$compressed_file" | cut -f1)
    
    log_success "Data backup created: $compressed_file ($file_size)"
    echo "$compressed_file"
}

# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================
verify_backup() {
    local backup_file="$1"
    
    log_info "Verifying backup integrity..."
    
    # Check if file exists and is not empty
    if [[ ! -f "$backup_file" ]] || [[ ! -s "$backup_file" ]]; then
        log_error "Backup file is missing or empty"
        return 1
    fi
    
    # For compressed files, test compression integrity
    if [[ "$backup_file" == *.gz ]]; then
        if gzip -t "$backup_file"; then
            log_success "Backup compression is valid"
        else
            log_error "Backup compression is corrupted"
            return 1
        fi
    fi
    
    # For custom format, test with pg_restore
    if [[ "$backup_file" == *.dump ]]; then
        if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_restore --list "$backup_file" > /dev/null 2>&1; then
            log_success "Custom backup format is valid"
        else
            log_error "Custom backup format is corrupted"
            return 1
        fi
    fi
    
    log_success "Backup verification completed"
    return 0
}

# =============================================================================
# CLEANUP FUNCTIONS
# =============================================================================
cleanup_old_backups() {
    log_info "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
    
    # Find and remove old backups
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "db_backup_*.dump" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "schema_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "data_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    local remaining_backups=$(find "$BACKUP_DIR" -name "*backup_*.sql.gz" -o -name "*backup_*.dump" | wc -l)
    
    log_success "Cleanup completed. Remaining backups: $remaining_backups"
}

# =============================================================================
# MONITORING FUNCTIONS
# =============================================================================
log_backup_stats() {
    local backup_file="$1"
    
    log_info "Backup statistics:"
    echo "File: $backup_file"
    echo "Size: $(du -h "$backup_file" | cut -f1)"
    echo "Created: $(date)"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    
    # Get database size
    local db_size=$(docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
    echo "Database size: $db_size"
    
    # Get table count
    local table_count=$(docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
    echo "Tables: $table_count"
}

send_notification() {
    local status="$1"
    local backup_file="$2"
    
    # Simple notification (extend as needed)
    if [[ "$status" == "success" ]]; then
        log_success "Backup completed successfully: $backup_file"
    else
        log_error "Backup failed: $backup_file"
    fi
    
    # Here you can add email/Slack/Discord notifications
    # Example:
    # curl -X POST -H 'Content-type: application/json' \
    #   --data '{"text":"Database backup '"$status"': '"$backup_file"'"}' \
    #   "$SLACK_WEBHOOK_URL"
}

# =============================================================================
# MAIN BACKUP FUNCTIONS
# =============================================================================
perform_full_backup() {
    log_info "Starting full backup process..."
    
    # Create both SQL and custom format backups
    local sql_backup=$(create_sql_backup)
    local custom_backup=$(create_custom_backup)
    
    # Verify backups
    if verify_backup "$sql_backup" && verify_backup "$custom_backup"; then
        log_success "Full backup completed successfully"
        log_backup_stats "$sql_backup"
        send_notification "success" "$sql_backup"
        return 0
    else
        log_error "Full backup verification failed"
        send_notification "failed" "$sql_backup"
        return 1
    fi
}

perform_schema_backup() {
    log_info "Starting schema backup process..."
    
    local schema_backup=$(create_schema_backup)
    
    if verify_backup "$schema_backup"; then
        log_success "Schema backup completed successfully"
        log_backup_stats "$schema_backup"
        send_notification "success" "$schema_backup"
        return 0
    else
        log_error "Schema backup verification failed"
        send_notification "failed" "$schema_backup"
        return 1
    fi
}

perform_data_backup() {
    log_info "Starting data backup process..."
    
    local data_backup=$(create_data_backup)
    
    if verify_backup "$data_backup"; then
        log_success "Data backup completed successfully"
        log_backup_stats "$data_backup"
        send_notification "success" "$data_backup"
        return 0
    else
        log_error "Data backup verification failed"
        send_notification "failed" "$data_backup"
        return 1
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================
show_usage() {
    echo "Usage: $0 [TYPE]"
    echo
    echo "Types:"
    echo "  full     - Complete database backup (default)"
    echo "  schema   - Schema-only backup"
    echo "  data     - Data-only backup"
    echo "  auto     - Automated full backup with cleanup"
    echo
    echo "Examples:"
    echo "  $0 full    # Manual full backup"
    echo "  $0 auto    # Automated backup (for cron)"
    echo "  $0 schema  # Schema backup only"
}

main() {
    case "$BACKUP_TYPE" in
        "full"|"manual")
            check_prerequisites
            perform_full_backup
            ;;
        "schema")
            check_prerequisites
            perform_schema_backup
            ;;
        "data")
            check_prerequisites
            perform_data_backup
            ;;
        "auto")
            check_prerequisites
            perform_full_backup
            cleanup_old_backups
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown backup type: $BACKUP_TYPE"
            show_usage
            exit 1
            ;;
    esac
}

# Error handling
trap 'log_error "Backup process failed"' ERR

# Run main function
main "$@" 