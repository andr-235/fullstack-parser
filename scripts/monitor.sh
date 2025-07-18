#!/bin/bash

# =============================================================================
# MONITORING SCRIPT FOR FULLSTACK APPLICATION
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_FILE="/opt/app/logs/monitor.log"
CONTAINERS=("fullstack_prod_frontend" "fullstack_prod_backend" "fullstack_prod_arq_worker" "fullstack_prod_redis" "fullstack_prod_postgres" "fullstack_prod_nginx")

# Create logs directory if it doesn't exist
mkdir -p /opt/app/logs

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check container status
check_container_status() {
    local container=$1
    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
    
    if [ "$status" = "running" ]; then
        echo -e "${GREEN}✓${NC} $container: $status"
        log_message "INFO: Container $container is running"
    elif [ "$status" = "not_found" ]; then
        echo -e "${RED}✗${NC} $container: not found"
        log_message "ERROR: Container $container not found"
    else
        echo -e "${YELLOW}⚠${NC} $container: $status"
        log_message "WARNING: Container $container status: $status"
    fi
}

# Function to check container health
check_container_health() {
    local container=$1
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no_health_check")
    
    if [ "$health" = "healthy" ]; then
        echo -e "${GREEN}✓${NC} $container health: $health"
        log_message "INFO: Container $container health: $health"
    elif [ "$health" = "no_health_check" ]; then
        echo -e "${BLUE}ℹ${NC} $container: no health check"
    else
        echo -e "${RED}✗${NC} $container health: $health"
        log_message "ERROR: Container $container health: $health"
    fi
}

# Function to check resource usage
check_resource_usage() {
    echo -e "\n${BLUE}=== RESOURCE USAGE ===${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    log_message "INFO: Resource usage checked"
}

# Function to check restart count
check_restart_count() {
    echo -e "\n${BLUE}=== RESTART COUNTS ===${NC}"
    for container in "${CONTAINERS[@]}"; do
        local restart_count=$(docker inspect --format='{{.RestartCount}}' "$container" 2>/dev/null || echo "N/A")
        if [ "$restart_count" = "0" ]; then
            echo -e "${GREEN}✓${NC} $container: $restart_count restarts"
        elif [ "$restart_count" = "N/A" ]; then
            echo -e "${YELLOW}⚠${NC} $container: not found"
        else
            echo -e "${RED}✗${NC} $container: $restart_count restarts"
            log_message "WARNING: Container $container has $restart_count restarts"
        fi
    done
}

# Function to check application health endpoints
check_health_endpoints() {
    echo -e "\n${BLUE}=== HEALTH ENDPOINTS ===${NC}"
    
    # Check nginx health
    if curl -f -s http://localhost/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Nginx health: OK"
        log_message "INFO: Nginx health check passed"
    else
        echo -e "${RED}✗${NC} Nginx health: FAILED"
        log_message "ERROR: Nginx health check failed"
    fi
    
    # Check frontend health
    if curl -f -s -k https://localhost/health/frontend >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend health: OK"
        log_message "INFO: Frontend health check passed"
    else
        echo -e "${RED}✗${NC} Frontend health: FAILED"
        log_message "ERROR: Frontend health check failed"
    fi
    
    # Check backend health
    if curl -f -s -k https://localhost/health/backend >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend health: OK"
        log_message "INFO: Backend health check passed"
    else
        echo -e "${RED}✗${NC} Backend health: FAILED"
        log_message "ERROR: Backend health check failed"
    fi
}

# Function to check disk space
check_disk_space() {
    echo -e "\n${BLUE}=== DISK SPACE ===${NC}"
    df -h /opt/app | tail -1 | awk '{print "Usage: " $5 " (" $3 "/" $2 ")"}'
    log_message "INFO: Disk space checked"
}

# Function to check recent logs for errors
check_recent_errors() {
    echo -e "\n${BLUE}=== RECENT ERRORS ===${NC}"
    
    # Check nginx error logs
    if docker exec fullstack_prod_nginx test -f /var/log/nginx/error.log; then
        local nginx_errors=$(docker exec fullstack_prod_nginx tail -10 /var/log/nginx/error.log | grep -i error | wc -l)
        if [ "$nginx_errors" -gt 0 ]; then
            echo -e "${YELLOW}⚠${NC} Nginx: $nginx_errors recent errors"
            log_message "WARNING: Nginx has $nginx_errors recent errors"
        else
            echo -e "${GREEN}✓${NC} Nginx: no recent errors"
        fi
    fi
    
    # Check frontend logs
    local frontend_logs=$(docker logs fullstack_prod_frontend --since 1h 2>&1 | grep -i error | wc -l)
    if [ "$frontend_logs" -gt 0 ]; then
        echo -e "${YELLOW}⚠${NC} Frontend: $frontend_logs recent errors"
        log_message "WARNING: Frontend has $frontend_logs recent errors"
    else
        echo -e "${GREEN}✓${NC} Frontend: no recent errors"
    fi
    
    # Check backend logs
    local backend_logs=$(docker logs fullstack_prod_backend --since 1h 2>&1 | grep -i error | wc -l)
    if [ "$backend_logs" -gt 0 ]; then
        echo -e "${YELLOW}⚠${NC} Backend: $backend_logs recent errors"
        log_message "WARNING: Backend has $backend_logs recent errors"
    else
        echo -e "${GREEN}✓${NC} Backend: no recent errors"
    fi
}

# Main monitoring function
main() {
    echo -e "${BLUE}=== FULLSTACK APPLICATION MONITORING ===${NC}"
    log_message "INFO: Starting monitoring check"
    
    echo -e "\n${BLUE}=== CONTAINER STATUS ===${NC}"
    for container in "${CONTAINERS[@]}"; do
        check_container_status "$container"
    done
    
    echo -e "\n${BLUE}=== CONTAINER HEALTH ===${NC}"
    for container in "${CONTAINERS[@]}"; do
        check_container_health "$container"
    done
    
    check_restart_count
    check_health_endpoints
    check_resource_usage
    check_disk_space
    check_recent_errors
    
    echo -e "\n${GREEN}=== MONITORING COMPLETE ===${NC}"
    log_message "INFO: Monitoring check completed"
}

# Run main function
main "$@" 