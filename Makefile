# =============================================================================
# Production-Ready Makefile for Go Backend API
# Docker Compose + Nginx Management
# =============================================================================

.PHONY: help build up down restart logs status health backup restore clean deploy

# Default target
.DEFAULT_GOAL := help

# Configuration
COMPOSE_FILE = backend/docker-compose.yml
PROD_COMPOSE_FILE = docker-compose.prod.yml
ENV_FILE = .env

# Colors
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Help target
help: ## Show this help message
	@echo "$(BLUE)Go Backend API - Docker Management$(NC)"
	@echo "======================================"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make up          # Start development environment"
	@echo "  make deploy      # Deploy to production"
	@echo "  make logs        # View application logs"
	@echo "  make backup      # Create database backup"

# Development commands
build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Development environment started$(NC)"
	@echo "$(YELLOW)API: http://localhost:8080$(NC)"
	@echo "$(YELLOW)Health: http://localhost:8080/health$(NC)"

down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

# Production commands
deploy: ## Deploy to production with zero-downtime
	@echo "$(BLUE)Deploying to production...$(NC)"
	./scripts/deploy.sh
	@echo "$(GREEN)✅ Production deployment completed$(NC)"

prod-up: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Production environment started$(NC)"

prod-down: ## Stop production environment
	@echo "$(BLUE)Stopping production environment...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f $(PROD_COMPOSE_FILE) down
	@echo "$(GREEN)✅ Production environment stopped$(NC)"

# Monitoring commands
logs: ## View application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## View API logs only
	@echo "$(BLUE)Showing API logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f api

logs-db: ## View database logs only
	@echo "$(BLUE)Showing database logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f postgres

logs-nginx: ## View Nginx logs only
	@echo "$(BLUE)Showing Nginx logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

logs-frontend: ## View Frontend logs only
	@echo "$(BLUE)Showing Frontend logs...$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

status: ## Show service status
	@echo "$(BLUE)Service status:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	./scripts/deploy.sh health

# Database commands
backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	./scripts/backup-db.sh
	@echo "$(GREEN)✅ Database backup completed$(NC)"

backup-list: ## List available backups
	@echo "$(BLUE)Available backups:$(NC)"
	./scripts/backup-db.sh list

backup-restore: ## Restore database from backup (usage: make backup-restore FILE=backup.sql.gz)
	@echo "$(BLUE)Restoring database from backup...$(NC)"
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make backup-restore FILE=backup.sql.gz$(NC)"; \
		exit 1; \
	fi
	./scripts/backup-db.sh restore $(FILE)
	@echo "$(GREEN)✅ Database restored$(NC)"

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec api ./main migrate
	@echo "$(GREEN)✅ Migrations completed$(NC)"

# Maintenance commands
clean-docker: ## Clean up unused Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

# Setup commands
setup: ## Initial setup (copy env file, create directories)
	@echo "$(BLUE)Setting up project...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		cp env.example $(ENV_FILE); \
		echo "$(YELLOW)⚠️  Please edit $(ENV_FILE) with your configuration$(NC)"; \
	fi
	mkdir -p logs backups
	@echo "$(GREEN)✅ Project setup completed$(NC)"

# Development helpers
shell-api: ## Open shell in API container
	@echo "$(BLUE)Opening shell in API container...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec api bash

shell-db: ## Open PostgreSQL shell
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U postgres -d comments_analysis

shell-redis: ## Open Redis shell
	@echo "$(BLUE)Opening Redis shell...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec redis redis-cli

shell-frontend: ## Open shell in Frontend container
	@echo "$(BLUE)Opening shell in Frontend container...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec frontend sh

# Testing commands
test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec api go test ./...
	@echo "$(GREEN)✅ Tests completed$(NC)"

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec api go test -coverprofile=coverage.out ./...
	@echo "$(GREEN)✅ Test coverage completed$(NC)"

# Security commands
security-scan: ## Run security scan on images
	@echo "$(BLUE)Running security scan...$(NC)"
	@if command -v trivy >/dev/null 2>&1; then \
		trivy image go_backend_api:latest; \
	else \
		echo "$(YELLOW)⚠️  Trivy not installed. Install with: https://aquasecurity.github.io/trivy/$(NC)"; \
	fi

# Information commands
info: ## Show project information
	@echo "$(BLUE)Go Backend API - Project Information$(NC)"
	@echo "======================================="
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API:      http://localhost:8080"
	@echo "  Nginx:    http://localhost:80"
	@echo "  Health:   http://localhost:8080/health"
	@echo ""
	@echo "$(YELLOW)Database:$(NC)"
	@echo "  Host:     localhost"
	@echo "  Port:     5432"
	@echo "  Database: comments_analysis"
	@echo "  User:     postgres"
	@echo ""
	@echo "$(YELLOW)Redis:$(NC)"
	@echo "  Host:     localhost"
	@echo "  Port:     6379"
	@echo ""
	@echo "$(YELLOW)Logs:$(NC)"
	@echo "  Location: ./logs/"
	@echo "  View:     make logs"
	@echo ""
	@echo "$(YELLOW)Backups:$(NC)"
	@echo "  Location: ./backups/"
	@echo "  Create:   make backup"
	@echo "  List:     make backup-list"

# Cleanup commands
clean: ## Clean project from temporary files and caches
	@echo "$(BLUE)Cleaning project...$(NC)"
	@./cleanup.sh
	@echo "$(GREEN)✅ Project cleaned successfully$(NC)"

clean-docker-new: ## Clean Docker images, containers and volumes
	@echo "$(BLUE)Cleaning Docker artifacts...$(NC)"
	docker system prune -f
	docker volume prune -f
	docker image prune -f
	@echo "$(GREEN)✅ Docker cleaned successfully$(NC)"

clean-all: clean clean-docker-new ## Clean everything (project + Docker)
	@echo "$(GREEN)✅ Complete cleanup finished$(NC)"

# Maintenance commands
maintenance: ## Show maintenance commands
	@echo "$(BLUE)Maintenance Commands$(NC)"
	@echo "====================="
	@echo ""
	@echo "$(YELLOW)Cleanup:$(NC)"
	@echo "  make clean        # Clean project files"
	@echo "  make clean-docker # Clean Docker artifacts"
	@echo "  make clean-all    # Clean everything"
	@echo ""
	@echo "$(YELLOW)Health:$(NC)"
	@echo "  make health       # Check service health"
	@echo "  make logs         # View logs"
	@echo "  make status       # Show service status"
	@echo ""
	@echo "$(YELLOW)Backup:$(NC)"
	@echo "  make backup       # Create backup"
	@echo "  make backup-list  # List backups"