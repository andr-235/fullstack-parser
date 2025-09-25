# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

### Backend (Express.js)
```bash
# Development
cd backend/
npm run dev      # Start Express.js server with nodemon
npm test         # Run Jest tests
npm run migrate  # Run database migrations
node server.js   # Start server directly

# Dependencies
npm install      # Install dependencies
```

### Frontend (Vue.js 3)
```bash
# Development
cd frontend/
npm run dev      # Start Vite dev server on port 5173
npm run build    # Build for production
npm run preview  # Preview production build

# Dependencies
npm install      # Install dependencies
```

### Docker Services
```bash
# Development environment
docker-compose up -d              # Start all services (postgres, redis, api, frontend)
docker-compose down               # Stop all services
docker-compose logs -f api        # View API service logs
docker-compose logs -f frontend   # View frontend service logs
docker-compose exec postgres bash # Shell into PostgreSQL container
```

## Architecture Overview

### Full Stack Application Architecture
This is a **Vue.js 3 + Express.js** full-stack application for VK (VKontakte) social media analytics.

#### Backend (Express.js)
- **Location**: `backend/` directory
- **Main entry**: `backend/server.js`
- **Port**: 3000 (API server)
- **Architecture**: MVC pattern with:
  - `src/controllers/` - Route handlers (taskController.js, groupsController.js)
  - `src/services/` - Business logic (vkService.js, taskService.js, groupsService.js)
  - `src/models/` - Sequelize ORM models (post.js, comment.js, task.js, group.js)
  - `src/repositories/` - Data access layer (dbRepo.js, vkApi.js, groupsRepo.js)
  - `src/middleware/` - Express middleware (upload.js)
  - `src/config/` - Database configuration (db.js)
  - `src/utils/` - Utilities (logger.js, fileParser.js, vkValidator.js)

#### Frontend (Vue.js 3)
- **Location**: `frontend/` directory
- **Framework**: Vue.js 3 with Composition API
- **Port**: 5173 (development), 80 (Docker production)
- **UI Framework**: Vuetify 3 (Material Design)
- **Architecture**: Feature-based structure with:
  - `src/views/` - Page components (FetchComments.vue, CommentsList.vue, TaskStatus.vue)
  - `src/views/groups/` - Groups management views
  - `src/components/` - Reusable UI components including Vuetify components
  - `src/components/groups/` - Groups-specific components
  - `src/stores/` - Pinia state management (comments.js, tasks.js, groups.js)
  - `src/router/` - Vue Router configuration (simplified, no authentication)
  - `src/services/` - API communication layer (api.js)

### Key Features

1. **VK Comments Analysis**:
   - Fetch comments from VK posts
   - Background task processing with progress tracking
   - Comment filtering and analysis

2. **Groups Management**:
   - VK groups file upload and processing
   - Groups validation and management
   - Bulk operations on groups data

3. **Task Processing System**:
   - Asynchronous task execution with BullMQ
   - Real-time task progress monitoring
   - Task status tracking and history

### Infrastructure Stack
- **Database**: PostgreSQL with Sequelize ORM
- **Cache/Queue**: Redis with BullMQ for background jobs
- **Logging**: Winston with structured logging
- **API Security**: Rate limiting, CORS, input validation with Joi
- **File Upload**: Multer middleware for file processing
- **Containerization**: Docker Compose for all services

### Testing

#### Backend Tests (Jest)
```bash
cd backend/
npm test                    # Run all Jest tests
npm test -- --watch        # Run tests in watch mode
npm test fileParser.test.js # Run specific test file
```

Test structure:
- `tests/unit/` - Unit tests for utilities and services
- `tests/integration/` - Integration tests for API endpoints

#### Frontend Tests
```bash
cd frontend/
npm run test               # Run Vitest tests (currently placeholder)
npx playwright test        # Run Playwright E2E tests
```

### Database Operations
```bash
# Via Docker Compose
docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Manual migration (backend)
cd backend/
npm run migrate

# Database initialization
# Migrations run automatically via init.sql on container startup
```

## Development Guidelines

### Code Organization
- **Backend**: Follow MVC pattern with service/repository layers
- **Frontend**: Vue.js 3 Composition API with Pinia for state management
- **No Authentication**: Simplified architecture without user authentication
- **File Structure**: Feature-based organization in frontend, layered architecture in backend

### Key Technologies

#### Backend Stack
- **Node.js** with Express.js 5.1.0
- **Sequelize ORM** for PostgreSQL operations
- **BullMQ** for background job processing
- **Redis** for caching and job queues
- **Winston** for structured logging
- **Joi** for request validation
- **Multer** for file upload handling

#### Frontend Stack
- **Vue.js 3** with Composition API
- **Vuetify 3** for Material Design UI components
- **Pinia** for state management
- **Vue Router 4** for navigation
- **Vite** for build tooling
- **Axios** for API communication

### Important Files

#### Backend Files
- `backend/server.js` - Express.js application entry point
- `backend/src/config/db.js` - Database configuration and connection
- `backend/src/models/` - Sequelize models (comment.js, post.js, task.js, group.js)
- `backend/src/controllers/` - Route handlers for API endpoints
- `backend/src/services/` - Business logic layer
- `backend/src/repositories/` - Data access layer
- `backend/migrations/` - Database schema migrations

#### Frontend Files
- `frontend/src/main.js` - Vue application entry point
- `frontend/src/App.vue` - Root Vue component with Vuetify layout
- `frontend/src/router/index.js` - Vue Router configuration
- `frontend/src/stores/` - Pinia stores for state management
- `frontend/src/views/` - Page-level Vue components
- `frontend/vite.config.js` - Vite build configuration

#### Configuration Files
- `docker-compose.yml` - Services orchestration
- `.env` - Environment variables (created from .env.prod template)
- `init.sql` - Database initialization script

## API Endpoints and Service URLs
- **Backend API**: `http://localhost:3000` (Express.js)
- **Frontend**: `http://localhost:5173` (development) / `http://localhost:5173` (Docker)
- **API routes**: `http://localhost:3000/api/*`

### Main API Endpoints
- `POST /api/tasks` - Create VK comment fetching tasks
- `GET /api/tasks/:id` - Get task status and progress
- `GET /api/comments` - Retrieve processed comments
- `POST /api/groups/upload` - Upload groups file for processing
- `GET /api/groups` - Retrieve groups data

## Service Configuration

### Environment Setup
```bash
# Environment variables are pre-configured
# .env file is included in the repository
# Key variables are already set for development
```

### Key Environment Variables
- `POSTGRES_DB=vk_analyzer` - Database name
- `POSTGRES_USER=postgres` - Database user
- `POSTGRES_PASSWORD=password` - Database password
- `VK_ACCESS_TOKEN` - VK API access token (set as needed)
- `CORS_ORIGINS=http://localhost:5173` - Allowed frontend origins

### Service Ports
- **Backend API**: `3000`
- **Frontend**: `5173` (development), `80` (Docker container)
- **PostgreSQL**: `5432`
- **Redis**: `6379`

## Deployment Scripts

Available deployment scripts in `scripts/` directory:
```bash
./scripts/deploy-express.sh    # Deploy Express.js backend
./scripts/manage-services.sh   # Service management utilities
./scripts/quick-deploy-adm79.sh # Quick deployment script
./scripts/rollback.sh          # Rollback deployment
```

## Common Development Tasks

### Starting Development Environment
```bash
# Option 1: Docker Compose (recommended)
docker-compose up -d

# Option 2: Local development
# Terminal 1 - Backend
cd backend/
npm install
npm run dev

# Terminal 2 - Frontend
cd frontend/
npm install
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend/
npm test

# Frontend E2E tests
cd frontend/
npx playwright test
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 3000, 5173, 5432, 6379 are available
2. **Docker issues**:
   - `docker-compose down && docker-compose up -d` to restart services
   - `docker-compose logs -f <service>` to check service logs
3. **Database connection**: Verify PostgreSQL is running and accessible
4. **VK API issues**: Check `VK_ACCESS_TOKEN` environment variable
5. **Frontend build issues**: Clear node_modules and reinstall dependencies
6. **CORS errors**: Ensure frontend runs on `http://localhost:5173`

### Debugging
- **Backend logs**: `docker-compose logs -f api`
- **Database access**: `docker-compose exec postgres psql -U postgres -d vk_analyzer`
- **Redis access**: `docker-compose exec redis redis-cli`

## AI Assistant Guidelines


* Разработка ведется на OC Windows, сервер на Debian
* Ты должен общаться нарусском языке
* Не редактируй .env файл - лишь говори какие переменные нужно туда добавить
* Используй Context7 для доступа к документациям библиотек
* Для реализации любых фич с использованием интеграций с внешним api/библиотеками изучай документацию с помощью context7
* После изменений делай коммиты