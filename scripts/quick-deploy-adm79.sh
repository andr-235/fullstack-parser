#!/bin/bash

# =============================================================================
# Quick Deploy Script for adm79 Self-hosted Runner
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration for adm79 user
PROJECT_DIR="/home/adm79/fullstack-parser"
BACKUP_DIR="/home/adm79/backups"
LOG_FILE="/home/adm79/logs/quick-deploy.log"

# Create directories if they don't exist
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

# Function to check if we're running as adm79
check_user() {
    if [ "$(whoami)" != "adm79" ]; then
        error "This script should be run as user 'adm79'"
        error "Current user: $(whoami)"
        exit 1
    fi
    success "Running as user: $(whoami)"
}

# Function to check project directory
check_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Project directory not found: $PROJECT_DIR"
        log "Available directories in /home/adm79:"
        ls -la /home/adm79/ || true
        exit 1
    fi
    success "Project directory exists: $PROJECT_DIR"
}

# Function to backup database quickly
quick_backup() {
    log "Creating quick database backup..."

    local backup_file="$BACKUP_DIR/quick_backup_$(date +%Y%m%d_%H%M%S).sql.gz"

    cd "$PROJECT_DIR"

    if docker-compose ps postgres | grep -q "Up"; then
        if docker-compose exec -T postgres pg_dump -U postgres vk_parser | gzip > "$backup_file"; then
            success "Quick backup created: $backup_file"
        else
            warning "Quick backup failed, continuing without backup"
        fi
    else
        warning "PostgreSQL container not running, skipping backup"
    fi
}

# Function to deploy Express.js backend
deploy_express() {
    log "Starting Express.js backend deployment..."

    cd "$PROJECT_DIR"

    # Show current status
    log "Current directory: $(pwd)"
    log "Current git branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"

    # Pull latest changes
    log "Pulling latest changes..."
    if ! git pull origin main; then
        error "Failed to pull latest changes"
        exit 1
    fi

    # Quick backup
    quick_backup

    # Check if .env exists
    if [ ! -f ".env" ]; then
        warning ".env file not found"
        if [ -f "env.example" ]; then
            log "Copying env.example to .env"
            cp env.example .env
            warning "Please review and update .env file with correct values"
        fi
    fi

    # Show current services
    log "Current services status:"
    docker-compose ps || true

    # Stop current services
    log "Stopping current services..."
    docker-compose down || true

    # Build and start services
    log "Building and starting services..."
    if docker-compose up -d --build; then
        success "Services started successfully"
    else
        error "Failed to start services"
        exit 1
    fi

    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 20

    # Check Express.js backend
    for i in {1..10}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            success "Express.js backend is responding on port 3000"
            break
        else
            log "Attempt $i/10: Express.js backend not ready yet..."
            sleep 3
        fi

        if [ $i -eq 10 ]; then
            error "Express.js backend failed to start"
            log "Checking logs..."
            docker-compose logs --tail=20 api || true
            exit 1
        fi
    done

    # Show final status
    log "Final services status:"
    docker-compose ps

    # Clean up old images
    log "Cleaning up old Docker images..."
    docker image prune -f > /dev/null 2>&1 || true

    success "Express.js backend deployment completed successfully!"
}

# Function to show service status
show_status() {
    cd "$PROJECT_DIR"
    echo "=== Service Status ==="
    docker-compose ps
    echo ""
    echo "=== Recent Logs ==="
    docker-compose logs --tail=10
    echo ""
    echo "=== Disk Usage ==="
    df -h "$PROJECT_DIR"
    echo ""
    echo "=== Docker Images ==="
    docker images | head -10
}

# Function to show logs
show_logs() {
    cd "$PROJECT_DIR"
    docker-compose logs -f --tail=50
}

# Function to restart services
restart_services() {
    cd "$PROJECT_DIR"
    log "Restarting services..."
    docker-compose restart
    sleep 10

    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        success "Services restarted successfully"
    else
        error "Services failed to restart properly"
    fi
}

# Function to show help
show_help() {
    echo "Quick Deploy Script for adm79 Self-hosted Runner"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy     Deploy Express.js backend"
    echo "  status     Show current status"
    echo "  logs       Show live logs"
    echo "  restart    Restart services"
    echo "  backup     Create database backup only"
    echo "  help       Show this help message"
    echo ""
    echo "Environment:"
    echo "  Project:   $PROJECT_DIR"
    echo "  Backups:   $BACKUP_DIR"
    echo "  Logs:      $LOG_FILE"
    echo ""
}

# Main script
main() {
    log "=== Quick Deploy Script Started ==="

    check_user
    check_project_dir

    case "${1:-deploy}" in
        deploy)
            deploy_express
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        restart)
            restart_services
            ;;
        backup)
            quick_backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Usage: $0 {deploy|status|logs|restart|backup|help}"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"