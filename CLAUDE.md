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
npm test            # Run Jest tests
npm run test:watch  # Run tests in watch mode (if configured)
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
- **Health endpoint**: `http://localhost:3000/` (basic status)
- **API routes**: `http://localhost:3000/api/*`
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
- **Database**: `5432` (PostgreSQL)
- **Cache**: `6379` (Redis)
- **Monitoring**: `9090` (Prometheus)

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
6. **Port conflicts**: Ensure ports 3000, 5432, 6379 are available
7. **CORS issues**: Frontend should run on `http://localhost:5173` (Vue.js)
8. **VK API**: Ensure `VK_ACCESS_TOKEN` is set in environment