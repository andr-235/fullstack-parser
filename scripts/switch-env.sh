#!/bin/bash

# =============================================================================
# ENVIRONMENT SWITCHER SCRIPT
# =============================================================================
# Скрипт для переключения между dev и prod режимами

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {dev|prod|status}"
    echo ""
    echo "Commands:"
    echo "  dev     - Switch to development mode (HTTP only)"
    echo "  prod    - Switch to production mode (HTTPS with redirect)"
    echo "  status  - Show current environment status"
    echo ""
    echo "Examples:"
    echo "  $0 dev   # Switch to development mode"
    echo "  $0 prod  # Switch to production mode"
    echo "  $0 status # Check current status"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to stop all containers
stop_containers() {
    print_status "Stopping all containers..."
    
    # Stop containers from both compose files
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    print_success "All containers stopped"
}

# Function to switch to development mode
switch_to_dev() {
    print_status "Switching to DEVELOPMENT mode..."
    
    check_docker
    stop_containers
    
    # Check if .env.prod exists
    if [ ! -f ".env.prod" ]; then
        print_warning ".env.prod file not found. Creating from env.example..."
        cp env.example .env.prod
    fi
    
    print_status "Starting development environment..."
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Development environment started!"
    print_status "Access your application at: http://localhost"
    print_status "Backend API: http://localhost/api"
    print_status "Health check: http://localhost/health"
}

# Function to switch to production mode
switch_to_prod() {
    print_status "Switching to PRODUCTION mode..."
    
    check_docker
    stop_containers
    
    # Check if .env.prod exists
    if [ ! -f ".env.prod" ]; then
        print_error ".env.prod file not found. Please create it first."
        exit 1
    fi
    
    # Check if SSL certificates exist
    if [ ! -d "nginx/ssl" ] || [ ! -f "nginx/ssl/fullchain.pem" ]; then
        print_warning "SSL certificates not found. HTTPS will not work."
        print_status "Please run: ./scripts/create-ssl-certs.sh"
    fi
    
    print_status "Starting production environment..."
    docker-compose up -d
    
    print_success "Production environment started!"
    print_status "Access your application at: https://yourdomain.com"
    print_status "HTTP requests will be redirected to HTTPS"
    print_status "Health check: https://yourdomain.com/health"
}

# Function to show current status
show_status() {
    print_status "Checking current environment status..."
    
    # Check if containers are running
    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "fullstack"; then
        print_success "Containers are running:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "fullstack"
        
        # Check which compose file is being used
        if docker-compose ps | grep -q "fullstack"; then
            print_status "Using: docker-compose.yml (Production mode)"
        elif docker-compose -f docker-compose.dev.yml ps | grep -q "fullstack"; then
            print_status "Using: docker-compose.dev.yml (Development mode)"
        fi
        
        # Check nginx configuration
        if docker exec fullstack_dev_nginx nginx -t 2>/dev/null; then
            print_success "Nginx configuration is valid"
        else
            print_error "Nginx configuration has errors"
        fi
        
        # Check if HTTPS is available
        if curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null | grep -q "200\|301\|302"; then
            print_success "HTTPS is working"
        else
            print_warning "HTTPS is not working (expected in dev mode)"
        fi
        
        # Check if HTTP is available
        if curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "200\|301\|302"; then
            print_success "HTTP is working"
        else
            print_error "HTTP is not working"
        fi
        
    else
        print_warning "No containers are currently running"
    fi
    
    # Check environment files
    if [ -f ".env.prod" ]; then
        print_success ".env.prod file exists"
    else
        print_warning ".env.prod file not found"
    fi
    
    if [ -f "env.example" ]; then
        print_success "env.example file exists"
    else
        print_warning "env.example file not found"
    fi
}

# Main script logic
case "$1" in
    dev)
        switch_to_dev
        ;;
    prod)
        switch_to_prod
        ;;
    status)
        show_status
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 