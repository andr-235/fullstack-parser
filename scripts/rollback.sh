#!/bin/bash

# =============================================================================
# Rollback Script for Express.js Backend
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration for adm79 user
APP_DIR="/home/adm79/fullstack-parser"
BACKUP_DIR="/home/adm79/backups"
LOG_FILE="/home/adm79/logs/rollback.log"
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"

# Create required directories if they don't exist
mkdir -p "$(dirname $LOG_FILE)"
mkdir -p "$BACKUP_DIR"

# Function to log messages
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if service is healthy
check_health() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-15}
    local attempt=1

    log "Checking health of $service_name..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "$service_name is healthy!"
            return 0
        fi

        log "Attempt $attempt/$max_attempts: $service_name not ready, waiting..."
        sleep 2
        ((attempt++))
    done

    error "$service_name failed health check after $max_attempts attempts"
    return 1
}

# Function to rollback to previous commit
rollback_code() {
    local commits_back=${1:-1}

    log "Rolling back code to $commits_back commit(s) ago..."

    cd "$APP_DIR" || {
        error "Failed to change to app directory: $APP_DIR"
        exit 1
    }

    # Get current commit hash for reference
    local current_commit=$(git rev-parse HEAD)
    log "Current commit: $current_commit"

    # Get target commit
    local target_commit=$(git rev-parse HEAD~$commits_back)
    log "Target commit: $target_commit"

    # Backup current state
    git tag "before-rollback-$(date +%Y%m%d-%H%M%S)" "$current_commit" || warning "Failed to create backup tag"

    # Rollback to target commit
    if git reset --hard "$target_commit"; then
        success "Code rolled back to commit: $target_commit"
    else
        error "Failed to rollback code"
        return 1
    fi
}

# Function to rollback database
rollback_database() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        return 1
    fi

    log "Rolling back database from: $backup_file"

    # Stop services to prevent database access
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" stop api

    # Restore database
    if zcat "$backup_file" | docker-compose exec -T postgres psql -U postgres -d vk_parser; then
        success "Database rolled back successfully"
    else
        error "Database rollback failed"
        return 1
    fi
}

# Function to list available backups
list_backups() {
    log "Available database backups:"

    if [ -d "$BACKUP_DIR" ]; then
        ls -la "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -10 || log "No backups found"
    else
        warning "Backup directory not found: $BACKUP_DIR"
    fi
}

# Function to rollback containers to previous images
rollback_containers() {
    log "Rolling back Docker containers..."

    cd "$APP_DIR"

    # Stop current services
    log "Stopping current services..."
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down

    # Try to use previous images (this is simplified - in real scenario you'd have versioned tags)
    log "Starting services with rollback..."
    if docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d; then
        success "Containers rolled back and started"
    else
        error "Failed to start rolled back containers"
        return 1
    fi

    # Wait for services
    sleep 20

    # Health checks
    if check_health "Express.js Backend" "http://localhost:3000"; then
        success "Rollback completed successfully"
    else
        error "Rollback health check failed"
        return 1
    fi
}

# Function for full rollback
full_rollback() {
    local commits_back=${1:-1}
    local backup_file=${2:-""}

    log "Starting full rollback process..."

    # Find latest backup if not specified
    if [ -z "$backup_file" ]; then
        backup_file=$(ls -t "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -1 || echo "")
        if [ -z "$backup_file" ]; then
            warning "No database backup found, skipping database rollback"
        else
            log "Using latest backup: $backup_file"
        fi
    fi

    # Rollback code
    if ! rollback_code "$commits_back"; then
        error "Code rollback failed"
        exit 1
    fi

    # Rollback database if backup available
    if [ -n "$backup_file" ]; then
        if ! rollback_database "$backup_file"; then
            warning "Database rollback failed, continuing with code rollback only"
        fi
    fi

    # Rollback and restart containers
    if ! rollback_containers; then
        error "Container rollback failed"
        exit 1
    fi

    success "Full rollback completed!"
}

# Function to show help
show_help() {
    echo "Rollback Script for Express.js Backend"
    echo ""
    echo "Usage: $0 [OPTION] [PARAMETERS]"
    echo ""
    echo "Options:"
    echo "  full [commits] [backup_file]  Full rollback (code + db + containers)"
    echo "  code [commits]                Rollback code only (default: 1 commit)"
    echo "  database [backup_file]        Rollback database only"
    echo "  containers                    Rollback containers only"
    echo "  list-backups                  List available database backups"
    echo "  help                          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 full 2                                    # Rollback 2 commits with latest backup"
    echo "  $0 code 3                                    # Rollback code 3 commits"
    echo "  $0 database /opt/backups/db_backup_xxx.sql.gz  # Rollback specific backup"
    echo ""
}

# Main script logic
case "${1:-}" in
    full)
        full_rollback "${2:-1}" "${3:-}"
        ;;
    code)
        rollback_code "${2:-1}"
        ;;
    database)
        if [ -z "${2:-}" ]; then
            error "Database backup file required"
            echo "Usage: $0 database <backup_file>"
            exit 1
        fi
        rollback_database "$2"
        ;;
    containers)
        rollback_containers
        ;;
    list-backups)
        list_backups
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Usage: $0 {full|code|database|containers|list-backups|help}"
        echo "Run '$0 help' for more information"
        exit 1
        ;;
esac