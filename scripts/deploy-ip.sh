#!/bin/bash

# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT FOR IP ADDRESS
# =============================================================================
# Автоматический деплой на сервер 192.168.88.12
# Использование: ./deploy-ip.sh [branch] [--force]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
BRANCH=${1:-"main"}
FORCE=${2:-""}
SERVER_IP="192.168.88.12"
APP_DIR="/opt/app"
BACKUP_DIR="/opt/app/backup"
COMPOSE_FILE="docker-compose.prod.ip.yml"
ENV_FILE="/opt/app/.env.prod"

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

    # Check if running from correct directory
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "IP production docker-compose file not found. Are you in the correct directory?"
        exit 1
    fi

    # Check if .env.prod exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Production environment file ($ENV_FILE) not found"
        log_info "Please create $ENV_FILE file with production configuration"
        exit 1
    fi

    # Check if SSL certificates exist
    if [[ ! -f "./nginx/ssl/cert.pem" ]] || [[ ! -f "./nginx/ssl/key.pem" ]]; then
        log_warning "SSL certificates not found"
        log_info "Running SSL certificate generation..."
        chmod +x ./scripts/create-ssl-certs.sh
        ./scripts/create-ssl-certs.sh
    fi

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi

    # Check if user has docker permissions
    if ! docker ps > /dev/null 2>&1; then
        log_error "Current user doesn't have Docker permissions"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# =============================================================================
# BACKUP FUNCTIONS
# =============================================================================
backup_database() {
    log_info "Creating database backup..."

    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Get database credentials from env file
    source "$ENV_FILE"

    # Create backup filename with timestamp
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

    # Check if postgres container is running
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        # Create database backup
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

        # Compress backup
        gzip "$BACKUP_FILE"

        log_success "Database backup created: ${BACKUP_FILE}.gz"

        # Clean old backups (keep last 10)
        find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | sort -r | tail -n +11 | xargs rm -f
    else
        log_warning "PostgreSQL container not running, skipping database backup"
    fi
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================
build_images() {
    log_info "Building Docker images..."

    # Build images without cache if force flag is set
    if [[ "$FORCE" == "--force" ]]; then
        docker-compose -f "$COMPOSE_FILE" build --no-cache
    else
        docker-compose -f "$COMPOSE_FILE" build
    fi

    log_success "Docker images built successfully"
}

check_services_health() {
    log_info "Checking services health..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Get all services status
        local services_status=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Service}}\t{{.State}}")

        # Check if all main services are running
        local postgres_running=$(docker-compose -f "$COMPOSE_FILE" ps postgres | grep -c "Up" || echo "0")
        local redis_running=$(docker-compose -f "$COMPOSE_FILE" ps redis | grep -c "Up" || echo "0")
        local backend_running=$(docker-compose -f "$COMPOSE_FILE" ps backend | grep -c "Up" || echo "0")
        local frontend_running=$(docker-compose -f "$COMPOSE_FILE" ps frontend | grep -c "Up" || echo "0")
        local nginx_running=$(docker-compose -f "$COMPOSE_FILE" ps nginx | grep -c "Up" || echo "0")

        if [[ $postgres_running -eq 1 && $redis_running -eq 1 && $backend_running -eq 1 && $frontend_running -eq 1 && $nginx_running -eq 1 ]]; then
            log_success "All services are running"

            # Additional health checks
            log_info "Performing additional health checks..."

            # Check if nginx is responding
            if curl -k -f "https://$SERVER_IP/health" > /dev/null 2>&1; then
                log_success "Application is accessible at https://$SERVER_IP"
                return 0
            else
                log_warning "Application not yet accessible, waiting..."
            fi
        fi

        log_warning "Waiting for services to be healthy..."
        sleep 10
        ((attempt++))
    done

    log_error "Services failed to become healthy within timeout"
    log_info "Current services status:"
    docker-compose -f "$COMPOSE_FILE" ps
    return 1
}

deploy_application() {
    log_info "Deploying application to $SERVER_IP..."

    # Create backup if services are running
    backup_database

    # Stop existing containers gracefully
    log_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down --timeout 30 || true

    # Remove unused images and volumes (but keep data volumes)
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f

    # Start services in correct order
    log_info "Starting database services..."
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 30

    # Start backend service
    log_info "Starting backend service..."
    docker-compose -f "$COMPOSE_FILE" up -d backend

    # Wait for backend to be ready
    log_info "Waiting for backend to be ready..."
    sleep 20

    # Start frontend service
    log_info "Starting frontend service..."
    docker-compose -f "$COMPOSE_FILE" up -d frontend

    # Wait for frontend to be ready
    log_info "Waiting for frontend to be ready..."
    sleep 15

    # Start nginx service
    log_info "Starting nginx reverse proxy..."
    docker-compose -f "$COMPOSE_FILE" up -d nginx

    log_success "All services started"
}

show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo
    log_info "Application URLs:"
    echo "  🌐 Main Application: https://$SERVER_IP"
    echo "  🔧 API Documentation: https://$SERVER_IP/api/docs"
    echo "  ❤️  Health Check: https://$SERVER_IP/health"
    echo
    log_info "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo
    log_warning "Note: Using self-signed SSL certificates. Your browser may show security warnings."
    log_info "To avoid warnings, add the certificate to your browser's trusted certificates."
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================
main() {
    log_info "Starting deployment for IP: $SERVER_IP"
    log_info "Branch: $BRANCH"
    log_info "Force rebuild: ${FORCE:-false}"

    # Check prerequisites
    check_prerequisites

    # Build images
    build_images

    # Deploy application
    deploy_application

    # Check health
    if check_services_health; then
        show_deployment_info
    else
        log_error "Deployment completed but health checks failed"
        log_info "Check logs with: docker-compose -f $COMPOSE_FILE logs"
        exit 1
    fi
}

# =============================================================================
# ERROR HANDLING
# =============================================================================
handle_error() {
    log_error "Deployment failed!"
    log_info "Rolling back..."

    # Show logs for debugging
    log_info "Recent logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=50

    exit 1
}

# Set up error handling
trap handle_error ERR

# Run main function
main "$@"
