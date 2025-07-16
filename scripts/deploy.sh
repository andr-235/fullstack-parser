#!/bin/bash

# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# Автоматический деплой fullstack приложения
# Использование: ./deploy.sh [branch] [--force]

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
APP_DIR="/opt/app"
BACKUP_DIR="/opt/app/backup"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

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
        log_error "Production docker-compose file not found. Are you in the correct directory?"
        exit 1
    fi

    # Check if .env.prod exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Production environment file ($ENV_FILE) not found"
        exit 1
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

    # Create database backup
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

    # Compress backup
    gzip "$BACKUP_FILE"

    log_success "Database backup created: ${BACKUP_FILE}.gz"

    # Clean old backups (keep last 10)
    find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f | sort -r | tail -n +11 | xargs rm -f
}

backup_volumes() {
    log_info "Creating volume backup..."

    # Backup postgres data
    docker run --rm -v "$(pwd)"_postgres_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

    # Backup redis data
    docker run --rm -v "$(pwd)"_redis_data:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/redis_data_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

    log_success "Volume backups created"
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================
pull_latest_code() {
    log_info "Pulling latest code from $BRANCH branch..."

    # Stash any local changes
    git stash

    # Fetch latest changes
    git fetch origin

    # Checkout target branch
    git checkout "$BRANCH"

    # Pull latest changes
    git pull origin "$BRANCH"

    log_success "Code updated to latest $BRANCH"
}

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

run_tests() {
    log_info "Running tests..."

    # Run backend tests
    log_info "Running backend tests..."
    docker-compose -f docker-compose.yml run --rm backend python -m pytest tests/ -v

    # Run frontend tests
    log_info "Running frontend tests..."
    docker-compose -f docker-compose.yml run --rm frontend npm test -- --coverage --watchAll=false

    log_success "All tests passed"
}

check_services_health() {
    log_info "Checking services health..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check if all services are healthy
        local unhealthy_services=$(docker-compose -f "$COMPOSE_FILE" ps --services --filter "health=unhealthy")

        if [[ -z "$unhealthy_services" ]]; then
            log_success "All services are healthy"
            return 0
        fi

        log_warning "Waiting for services to be healthy: $unhealthy_services"
        sleep 10
        ((attempt++))
    done

    log_error "Services failed to become healthy within timeout"
    return 1
}

deploy_application() {
    log_info "Deploying application..."

    # Stop existing containers gracefully
    log_info "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down --timeout 30

    # Remove unused images and volumes
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f

    # Start services in correct order
    log_info "Starting database services..."
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis

    # Wait for database to be ready
    sleep 10

    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" run --rm backend alembic upgrade head

    # Start application services
    log_info "Starting application services..."
    docker-compose -f "$COMPOSE_FILE" up -d backend frontend

    # Start nginx last
    log_info "Starting reverse proxy..."
    docker-compose -f "$COMPOSE_FILE" up -d nginx

    log_success "Application deployed successfully"
}

update_nginx_config() {
    log_info "Updating Nginx configuration..."

    # Backup current nginx config
    if docker exec fullstack_nginx test -f /etc/nginx/nginx.conf; then
        docker exec fullstack_nginx cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi

    # Restart nginx to load new config
    docker-compose -f "$COMPOSE_FILE" restart nginx

    # Test nginx configuration
    if docker exec fullstack_nginx nginx -t; then
        log_success "Nginx configuration updated successfully"
    else
        log_error "Nginx configuration test failed"
        # Restore backup if available
        docker exec fullstack_nginx cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf 2>/dev/null || true
        docker-compose -f "$COMPOSE_FILE" restart nginx
        return 1
    fi
}

# =============================================================================
# MONITORING & VERIFICATION
# =============================================================================
verify_deployment() {
    log_info "Verifying deployment..."

    # Check if containers are running
    local running_containers=$(docker-compose -f "$COMPOSE_FILE" ps --services --filter "status=running")
    local expected_containers="postgres redis backend frontend nginx"

    for service in $expected_containers; do
        if echo "$running_containers" | grep -q "$service"; then
            log_success "✓ $service is running"
        else
            log_error "✗ $service is not running"
            return 1
        fi
    done

    # Test API endpoint
    log_info "Testing API endpoint..."
    if curl -f -s "http://localhost:8000/health" > /dev/null; then
        log_success "✓ Backend API is responding"
    else
        log_warning "⚠ Backend API health check failed"
    fi

    # Test frontend
    log_info "Testing frontend..."
    if curl -f -s "http://localhost:3000" > /dev/null; then
        log_success "✓ Frontend is responding"
    else
        log_warning "⚠ Frontend health check failed"
    fi

    log_success "Deployment verification completed"
}

show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "Branch: $BRANCH"
    echo "Timestamp: $(date)"
    echo "Backup location: $BACKUP_DIR"
    echo
    echo "=== SERVICES STATUS ==="
    docker-compose -f "$COMPOSE_FILE" ps
    echo
    echo "=== USEFUL COMMANDS ==="
    echo "View logs: docker-compose -f $COMPOSE_FILE logs -f [service]"
    echo "Check status: docker-compose -f $COMPOSE_FILE ps"
    echo "Access backend: docker-compose -f $COMPOSE_FILE exec backend bash"
    echo "Access database: docker-compose -f $COMPOSE_FILE exec postgres psql -U \$DB_USER -d \$DB_NAME"
    echo
    echo "=== MONITORING ==="
    echo "Monitor containers: watch 'docker-compose -f $COMPOSE_FILE ps'"
    echo "View resource usage: docker stats"
    echo "Check logs: docker-compose -f $COMPOSE_FILE logs --tail=100 -f"
}

# =============================================================================
# ROLLBACK FUNCTION
# =============================================================================
rollback() {
    log_warning "Initiating rollback..."

    # Get previous git commit
    local previous_commit=$(git rev-parse HEAD~1)

    # Checkout previous commit
    git checkout "$previous_commit"

    # Rebuild and deploy
    build_images
    deploy_application

    log_success "Rollback completed"
}

# =============================================================================
# ERROR HANDLING
# =============================================================================
cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."

    # Try to restore from backup if deployment fails
    if [[ -f "$BACKUP_DIR/postgres_data_$(date +%Y%m%d)*.tar.gz" ]]; then
        log_info "Backup available. Consider manual restoration if needed."
    fi

    # Show logs for debugging
    echo "=== RECENT LOGS ==="
    docker-compose -f "$COMPOSE_FILE" logs --tail=50
}

# Set trap for error handling
trap cleanup_on_error ERR

# =============================================================================
# MAIN EXECUTION
# =============================================================================
main() {
    log_info "Starting production deployment..."
    echo "Branch: $BRANCH"
    echo "Force rebuild: ${FORCE:-"false"}"
    echo

    # Confirmation prompt
    if [[ "$FORCE" != "--force" ]]; then
        read -p "Are you sure you want to deploy to production? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi

    check_prerequisites
    backup_database
    backup_volumes
    pull_latest_code
    build_images

    # Run tests only if not forcing
    if [[ "$FORCE" != "--force" ]]; then
        run_tests
    fi

    deploy_application
    update_nginx_config
    check_services_health
    verify_deployment
    show_deployment_info

    log_success "Production deployment completed successfully!"
}

# Run main function
main "$@"
