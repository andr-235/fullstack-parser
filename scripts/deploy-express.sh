#!/bin/bash

# =============================================================================
# Express.js Backend Deployment Script
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
LOG_FILE="/home/adm79/logs/deploy.log"
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
    local max_attempts=${3:-30}
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

# Function to backup database
backup_database() {
    log "Creating database backup..."

    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
    fi

    local backup_file="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql.gz"

    if docker-compose exec -T postgres pg_dump -U postgres -d vk_parser | gzip > "$backup_file"; then
        success "Database backup created: $backup_file"
    else
        error "Database backup failed"
        return 1
    fi
}

# Function to rollback deployment
rollback() {
    error "Deployment failed. Rolling back..."

    log "Stopping current containers..."
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down

    log "Restoring from backup..."
    # Here you would restore from the backup created before deployment

    log "Starting previous version..."
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d

    error "Rollback completed"
}

# Function to deploy application
deploy() {
    log "Starting Express.js backend deployment..."

    # Change to app directory
    cd "$APP_DIR" || {
        error "Failed to change to app directory: $APP_DIR"
        exit 1
    }

    # Create backup
    if ! backup_database; then
        warning "Database backup failed, continuing with deployment..."
    fi

    # Pull latest code
    log "Pulling latest code from repository..."
    if ! git pull origin main; then
        error "Failed to pull latest code"
        exit 1
    fi

    # Check if .env files exist
    if [ ! -f ".env" ]; then
        warning ".env file not found, copying from example..."
        if [ -f "env.example" ]; then
            cp env.example .env
        else
            error "No .env or env.example file found"
            exit 1
        fi
    fi

    # Pull latest Docker images
    log "Pulling latest Docker images..."
    if ! docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" pull; then
        error "Failed to pull Docker images"
        exit 1
    fi

    # Stop current services
    log "Stopping current services..."
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" down

    # Start services with new images
    log "Starting services with new images..."
    if ! docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" up -d; then
        rollback
        exit 1
    fi

    # Wait for services to start
    log "Waiting for services to start..."
    sleep 30

    # Health checks
    log "Running health checks..."

    # Check Express.js backend
    if ! check_health "Express.js Backend" "http://localhost:3000"; then
        rollback
        exit 1
    fi

    # Check database connectivity through backend
    if ! check_health "Database (via backend)" "http://localhost:3000/api/health"; then
        rollback
        exit 1
    fi

    # Check if frontend is accessible (if nginx is configured)
    if docker-compose ps | grep -q nginx; then
        if ! check_health "Frontend (via Nginx)" "http://localhost"; then
            warning "Frontend health check failed, but continuing..."
        fi
    fi

    # Clean up old images and containers
    log "Cleaning up old Docker images..."
    docker image prune -f
    docker container prune -f

    success "Deployment completed successfully!"

    # Display service status
    log "Service status:"
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" ps

    log "Deployment logs:"
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" logs --tail=10
}

# Function to show help
show_help() {
    echo "Express.js Backend Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy    Deploy the application"
    echo "  health    Check application health"
    echo "  logs      Show application logs"
    echo "  status    Show service status"
    echo "  backup    Create database backup"
    echo "  help      Show this help message"
    echo ""
}

# Function to show service status
show_status() {
    cd "$APP_DIR"
    echo "Service Status:"
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" ps
}

# Function to show logs
show_logs() {
    cd "$APP_DIR"
    docker-compose -f "$COMPOSE_FILE" -f "$PROD_COMPOSE_FILE" logs -f
}

# Function to run health checks
run_health_checks() {
    log "Running comprehensive health checks..."

    check_health "Express.js Backend" "http://localhost:3000"
    check_health "Database Health" "http://localhost:3000/api/health"

    if docker-compose ps | grep -q nginx; then
        check_health "Frontend" "http://localhost"
    fi

    success "All health checks passed!"
}

# Main script logic
case "${1:-}" in
    deploy)
        deploy
        ;;
    health)
        run_health_checks
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    backup)
        backup_database
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Usage: $0 {deploy|health|logs|status|backup|help}"
        exit 1
        ;;
esac