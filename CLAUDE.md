# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

### Express.js Backend (Primary)
```bash
# Development
cd backend/
bun run dev      # Start Express.js server with nodemon
bun test         # Run Jest tests
node server.js   # Start server directly

# Dependencies
bun install      # with Bun runtime

# Database operations via Docker
make migrate     # Run database migrations
make backup      # Create database backup
make shell-db    # Open PostgreSQL shell
```

### Docker Services
```bash
# Development with Express.js backend
make up          # Start development environment with Docker
make down        # Stop all services
make restart     # Restart all services
make logs        # View all logs

# Production
make deploy      # Deploy to production with zero-downtime
make prod-up     # Start production environment
make health      # Check service health
```

### Docker Services
```bash
# Standard Docker operations
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f api        # View specific service logs
docker-compose exec api bash      # Shell into Go API container

# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Architecture Overview

### Current State: Express.js Backend Architecture
The project uses **Express.js** as the primary backend implementation:

#### Express.js Backend (Active)
- **Location**: `backend/` directory
- **Main entry**: `backend/server.js`
- **Port**: 3000
- **Frontend CORS**: Configured for Vue.js on `http://localhost:5173`
- **Architecture**: MVC pattern with:
  - `src/controllers/` - Route handlers (taskController.js)
  - `src/services/` - Business logic (vkService.js, taskService.js)
  - `src/models/` - Sequelize ORM models (post.js, comment.js, task.js)
  - `src/repositories/` - Data access layer (dbRepo.js, vkApi.js)
  - `src/config/` - Database configuration (db.js)
  - `src/utils/` - Utilities (logger.js)

#### Frontend (Vue.js 3)
- **Location**: `frontend/` directory
- **Framework**: Vue.js 3 with Vite
- **Port**: 5173 (development), 80 (Docker)
- **Architecture**: Feature-based with:
  - `src/auth/` - Complete authentication system (JWT-based)
  - `src/components/` - Reusable UI components
  - `src/views/` - Page components (Home, Profile, Admin, etc.)
  - `src/stores/` - Pinia state management (comments, tasks)
  - `src/router/` - Vue Router configuration with guards


### Key Components

1. **Domain Entities**:
   - `comments/` - Comment analysis and processing
   - `keywords/` - Keyword management and morphological analysis
   - `tasks/` - Background task processing
   - `users/` - User management and authentication
   - `settings/` - Application settings

2. **Express.js Infrastructure**:
   - PostgreSQL database with Sequelize ORM
   - Redis for caching and task queues
   - BullMQ for background job processing
   - Winston for logging
   - Rate limiting with rate-limiter-flexible
   - Joi for request validation

3. **Services Architecture**:
   - Express.js API server (`backend/server.js`)
   - VK API integration service
   - Task processing service
   - Database repositories
   - Background job workers

### Testing

#### Express.js Backend Tests
```bash
cd backend/
bun test         # Run Jest tests with Bun
npm run test     # Alternative: Run with npm
```

#### Frontend Tests
```bash
cd frontend/
bun run test     # Run Vue/Vite tests (configured to pass currently)
bun run lint     # Run linting (placeholder)
bun run type-check # Run TypeScript type checking (placeholder)
```

### Database Operations
- Migrations run automatically on container startup
- Manual migration: `make migrate`
- Database shell: `make shell-db`
- Backups: `make backup` and `make backup-list`
- Restore: `make backup-restore FILE=backup.sql.gz`

## Development Guidelines

### Code Organization
- Follow Clean Architecture principles
- Use dependency injection pattern
- Repository pattern for data access
- Use cases for business logic encapsulation

### Key Technologies

#### Express.js Backend Stack
- **Node.js** with Express.js 5.1.0
- **Sequelize ORM** for database operations
- **BullMQ** for background job processing
- **PostgreSQL** (pg driver)
- **Winston** for logging
- **Rate limiting** with rate-limiter-flexible
- **Joi** for validation

#### Shared Infrastructure
- **PostgreSQL** database
- **Redis** for caching and queues
- **Docker Compose** for orchestration

### Important Files

#### Express.js Backend Files
- `backend/package.json` - Node.js dependencies and scripts
- `backend/server.js` - Express.js application entry point
- `backend/src/` - Application source code
  - `controllers/taskController.js` - API route handlers
  - `services/vkService.js` - VK API integration
  - `models/` - Sequelize database models
  - `repositories/` - Data access layers
  - `config/db.js` - Database configuration

#### Shared Configuration
- `Makefile` - Development commands and automation
- `docker-compose.yml` - Development service definitions
- `docker-compose.prod.yml` - Production overrides
- `env.example` - Environment variables template
- `scripts/` - Deployment and utility scripts

## API Endpoints and Health Checks
- **Express.js API**: `http://localhost:3000`
- **Frontend Dev Server**: `http://localhost:5173`
- **Health endpoint**: `http://localhost:3000/` (basic status)
- **API routes**: `http://localhost:3000/api/*`
- **Frontend (Docker)**: `http://localhost:5173` (mapped to container port 80)
- Check status: `make status`
- View logs: `make logs`

## Service Configuration

### Environment Setup
```bash
# Copy environment template
cp env.example .env
# Edit .env with your configuration
```

### Key Environment Variables
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database configuration
- `SECRET_KEY` - JWT token signing key
- `CORS_ORIGINS` - Allowed frontend origins
- `LOG_LEVEL` - Application logging level
- `VK_ACCESS_TOKEN` - VK API access token (if needed)

### Service Ports
- **Express.js API**: `3000` (Node.js backend)
- **Frontend (Dev)**: `5173` (Vite dev server)
- **Frontend (Docker)**: `5173` (mapped to container port 80)
- **Database**: `5432` (PostgreSQL)
- **Cache**: `6379` (Redis)
- **Go API (Docker)**: `8080` (Legacy/Alternative backend)

## Scripts and Utilities

### Deployment Scripts
```bash
./scripts/deploy.sh         # Zero-downtime deployment
./scripts/backup-db.sh       # Database backup/restore
./scripts/monitor.sh         # Service monitoring
./scripts/docker-cleanup.sh  # Docker cleanup
```

### Maintenance Commands
```bash
make clean-docker    # Clean Docker resources
make setup          # Initial project setup
make info           # Show project information
make security-scan  # Security scan (requires trivy)
```

## Troubleshooting
1. **Service issues**: Check with `make status` or `docker-compose ps`
2. **Database problems**: Use `make shell-db` to inspect
3. **Build failures**: Clean with `make clean-docker`
4. **Log analysis**: Use `make logs` or specific service logs
5. **Health checks**: `make health` or visit `/health` endpoint
6. **Port conflicts**: Ensure ports 3000, 5173, 5432, 6379, 8080 are available
7. **CORS issues**: Frontend should run on `http://localhost:5173` (Vue.js)
8. **API proxy issues**: Vite proxies `/api` to `http://localhost:8000` (check vite.config.ts)
9. **Authentication**: Frontend includes complete JWT-based auth system
10. **VK API**: Ensure `VK_ACCESS_TOKEN` is set in environment

## Frontend Development Notes
- **State Management**: Uses Pinia stores for comments and tasks
- **Authentication**: Complete JWT auth system in `src/auth/`
- **Routing**: Vue Router with authentication guards
- **API Integration**: Axios with interceptors for auth headers
- **Development**: Hot reload with Vite on port 5173
- **Testing**: Jest tests configured but minimal implementation