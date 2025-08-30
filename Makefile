# =============================================================================
# Full Stack Parser - Makefile
# =============================================================================

.PHONY: help install-frontend install-backend install-all \
        lint-frontend lint-backend lint-all \
        format-frontend format-backend format-all \
        test-frontend test-backend test-all \
        build-frontend build-backend build-all \
        docker-build docker-up docker-down docker-logs \
        clean-frontend clean-backend clean-all \
        dev-frontend dev-backend dev-all \
        deploy-staging deploy-production \
        security-scan quality-check ci

# Default target
help: ## Show this help message
	@echo "Full Stack Parser - Development and CI/CD Commands"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Installation Commands
# =============================================================================

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && bun install

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	cd backend && poetry install

install-all: install-frontend install-backend ## Install all dependencies

# =============================================================================
# Linting Commands
# =============================================================================

lint-frontend: ## Run frontend linting
	@echo "Running frontend linting..."
	cd frontend && bun run lint

lint-backend: ## Run backend linting
	@echo "Running backend linting..."
	cd backend && poetry run ruff check .

lint-all: lint-frontend lint-backend ## Run all linting

# =============================================================================
# Code Formatting Commands
# =============================================================================

format-frontend: ## Format frontend code
	@echo "Formatting frontend code..."
	cd frontend && bun run format

format-backend: ## Format backend code
	@echo "Formatting backend code..."
	cd backend && poetry run black . && poetry run isort .

format-all: format-frontend format-backend ## Format all code

# =============================================================================
# Testing Commands
# =============================================================================

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	cd frontend && bun run test -- --watchAll=false --passWithNoTests

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	cd backend && poetry run pytest

test-all: test-frontend test-backend ## Run all tests

# =============================================================================
# Building Commands
# =============================================================================

build-frontend: ## Build frontend application
	@echo "Building frontend..."
	cd frontend && bun run build

build-backend: ## Build backend application (if needed)
	@echo "Building backend..."
	# Backend is built via Docker, no separate build step needed

build-all: build-frontend build-backend ## Build all applications

# =============================================================================
# Docker Commands
# =============================================================================

docker-build: ## Build all Docker images
	@echo "Building Docker images..."
	docker-compose -f docker-compose.prod.yml build

docker-up: ## Start all Docker services
	@echo "Starting Docker services..."
	docker-compose -f docker-compose.prod.yml up -d

docker-down: ## Stop all Docker services
	@echo "Stopping Docker services..."
	docker-compose -f docker-compose.prod.yml down

docker-logs: ## Show Docker logs
	@echo "Showing Docker logs..."
	docker-compose -f docker-compose.prod.yml logs -f

docker-clean: ## Clean Docker resources
	@echo "Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f

# =============================================================================
# Development Commands
# =============================================================================

dev-frontend: ## Start frontend development server
	@echo "Starting frontend development server..."
	cd frontend && bun run dev

dev-backend: ## Start backend development server
	@echo "Starting backend development server..."
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-all: ## Start all development servers
	@echo "Starting all development servers..."
	make -j2 dev-frontend dev-backend

# =============================================================================
# Database Commands
# =============================================================================

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

db-create-migration: ## Create new database migration
	@echo "Creating database migration..."
	@if [ -z "$(name)" ]; then \
		echo "Usage: make db-create-migration name='migration_name'"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "$(name)"

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "Resetting database..."
	docker-compose -f docker-compose.prod.yml down -v
	docker-compose -f docker-compose.prod.yml up -d postgres redis
	sleep 10
	make db-migrate

# =============================================================================
# Deployment Commands
# =============================================================================

deploy-production: ## Deploy to production environment
	@echo "Deploying to production..."
	@echo "Pulling latest changes..."
	git pull origin main
	@echo "Building and deploying..."
	docker-compose -f docker-compose.prod.yml down
	docker-compose -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "Running migrations..."
	make db-migrate

# =============================================================================
# Security and Quality Commands
# =============================================================================

security-scan: ## Run security vulnerability scans
	@echo "Running security scans..."
	@echo "Frontend security scan..."
	cd frontend && npm audit --audit-level moderate
	@echo "Backend security scan..."
	cd backend && poetry run bandit -r src/
	cd backend && poetry run pip-audit

quality-check: ## Run all quality checks
	@echo "Running quality checks..."
	make lint-all
	make test-all
	make security-scan

# =============================================================================
# Cleanup Commands
# =============================================================================

clean-frontend: ## Clean frontend build artifacts
	@echo "Cleaning frontend..."
	cd frontend && rm -rf .next node_modules/.cache out

clean-backend: ## Clean backend build artifacts
	@echo "Cleaning backend..."
	cd backend && rm -rf __pycache__ .pytest_cache .mypy_cache *.pyc *.pyo

clean-all: clean-frontend clean-backend ## Clean all build artifacts

# =============================================================================
# CI/CD Commands
# =============================================================================

ci: ## Run full CI pipeline locally
	@echo "Running CI pipeline..."
	make install-all
	make quality-check
	make build-all
	make test-all

# =============================================================================
# Utility Commands
# =============================================================================

update-deps: ## Update all dependencies
	@echo "Updating dependencies..."
	cd frontend && bun update
	cd backend && poetry update

health-check: ## Check health of all services
	@echo "Checking service health..."
	@echo "Frontend health:"
	curl -f http://localhost:3000/api/health || echo "Frontend not healthy"
	@echo "Backend health:"
	curl -f http://localhost:8000/health || echo "Backend not healthy"
	@echo "Nginx health:"
	curl -f http://localhost/health || echo "Nginx not healthy"

logs: ## Show all service logs
	@echo "Showing service logs..."
	docker-compose -f docker-compose.prod.yml logs -f --tail=100

# =============================================================================
# Environment Setup
# =============================================================================

setup-dev: ## Setup development environment
	@echo "Setting up development environment..."
	make install-all
	@echo "Development environment setup complete!"
	@echo "Run 'make dev-all' to start all services"

setup-prod: ## Setup production environment
	@echo "Setting up production environment..."
	make docker-build
	make docker-up
	@echo "Waiting for services to be ready..."
	sleep 30
	make db-migrate
	@echo "Production environment setup complete!"

# =============================================================================
# Help for specific targets
# =============================================================================

help-dev: ## Show development-related commands
	@echo "Development Commands:"
	@echo "  make dev-all           - Start all development servers"
	@echo "  make dev-frontend      - Start frontend dev server"
	@echo "  make dev-backend       - Start backend dev server"
	@echo "  make test-all          - Run all tests"
	@echo "  make lint-all          - Run all linters"
	@echo "  make format-all        - Format all code"

help-deploy: ## Show deployment-related commands
	@echo "Deployment Commands:"
	@echo "  make deploy-production - Deploy to production"
	@echo "  make docker-up         - Start production services"
	@echo "  make docker-down       - Stop production services"
	@echo "  make db-migrate        - Run database migrations"
