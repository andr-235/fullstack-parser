# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

### Backend (Express.js + TypeScript)
```bash
# Development
cd backend/
npm run dev         # Start TypeScript server with ts-node
npm run dev:watch   # Start with nodemon + ts-node for auto-reload
npm run build       # Compile TypeScript to JavaScript
npm run start       # Start compiled JavaScript server
npm test            # Run Jest tests
npm run test:watch  # Run tests in watch mode
npm run migrate     # Run database migrations

# Code Quality
npx eslint .        # Run ESLint for TypeScript/JavaScript linting
```

### Frontend (Vue.js 3)
```bash
# Development
cd frontend/
npm run dev         # Start Vite dev server on port 5173
npm run dev:local   # Start with local backend configuration
npm run build       # Build for production
npm run preview     # Preview production build

# Testing
npx playwright test       # Run Playwright E2E tests
npx playwright test --ui  # Run with UI interface

# Code Quality
npx eslint .              # Run ESLint for Vue/JavaScript linting
npx prettier --write .    # Format code with Prettier
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
This is a **Vue.js 3 + Express.js TypeScript** full-stack application for VK (VKontakte) social media analytics.

#### Backend (Express.js + TypeScript)
- **Location**: `backend/` directory
- **Main entry**: `backend/src/server.ts` (TypeScript source)
- **Compiled output**: `backend/dist/` directory
- **Port**: 3000 (API server)
- **Runtime**: Node.js with TypeScript support via ts-node
- **Architecture**: Layered MVC pattern with:
  - `src/controllers/` - Route handlers (taskController.ts, groupsController.ts)
  - `src/services/` - Business logic layer (vkService.ts, taskService.ts, groupsService.ts)
  - `src/models/` - Sequelize TypeScript models with decorators
  - `src/repositories/` - Data access layer (dbRepo.ts, vkApi.ts, groupsRepo.ts)
  - `src/middleware/` - Express middleware (upload.ts)
  - `src/config/` - Configuration (db.ts, queue.ts)
  - `src/utils/` - Utilities (logger.ts, fileParser.ts, vkValidator.ts)
  - `src/types/` - TypeScript type definitions

#### Frontend (Vue.js 3)
- **Location**: `frontend/` directory
- **Framework**: Vue.js 3 with Composition API
- **Port**: 5173 (development), 80 (Docker production)
- **UI Framework**: Vuetify 3 (Material Design)
- **Architecture**: Feature-based structure with:
  - `src/views/` - Page components (FetchComments.vue, CommentsList.vue, TaskStatus.vue)
  - `src/views/groups/` - Groups management views
  - `src/components/` - Reusable UI components
  - `src/stores/` - Pinia state management (comments.js, tasks.js, groups.js)
  - `src/router/` - Vue Router configuration
  - `src/services/` - API communication layer (api.js)

### Key Features

1. **VK Comments Analysis**:
   - Fetch comments from VK posts
   - Background task processing with BullMQ
   - Real-time progress tracking
   - Comment sentiment analysis

2. **Groups Management**:
   - VK groups file upload and processing
   - Groups validation and management
   - Bulk operations on groups data

3. **Task Processing System**:
   - Asynchronous task execution with BullMQ
   - Real-time task progress monitoring via polling
   - Task status tracking and history

### Infrastructure Stack
- **Language**: TypeScript (backend), JavaScript (frontend)
- **Database**: PostgreSQL with Sequelize TypeScript ORM
- **Cache/Queue**: Redis with BullMQ for background jobs
- **Logging**: Winston with structured logging
- **API Security**: Rate limiting, CORS, input validation with Joi
- **File Upload**: Multer middleware for file processing
- **Containerization**: Docker Compose for all services

### Testing

#### Backend Tests (Jest + TypeScript)
```bash
cd backend/
npm test                    # Run all Jest tests
npm run test:watch          # Run tests in watch mode
npm test -- --coverage     # Run tests with coverage report
npm test fileParser.test.ts # Run specific test file
```

Test configuration:
- **Test Runner**: Jest with ts-jest preset
- **Coverage threshold**: 80% for branches, functions, lines, statements
- **Test environment**: Node.js
- **Module mapping**: `@/` alias for `src/` directory
- **TypeScript support**: Full TypeScript compilation in tests

Test structure:
- `tests/unit/` - Unit tests for utilities and services
- `tests/integration/` - Integration tests for API endpoints
- `src/**/__tests__/` - Component-level tests
- `tests/setup.ts` - Test setup configuration

#### Frontend Tests
```bash
cd frontend/
npx playwright test        # Run Playwright E2E tests
npx playwright test --ui   # Run Playwright with UI
```

Test structure:
- `src/**/__tests__/` - Component and store unit tests
- `e2e/` - End-to-end test scenarios with Playwright

### Database Operations
```bash
# Via Docker Compose
docker-compose exec postgres psql -U postgres -d vk_analyzer

# Manual migration (TypeScript)
cd backend/
npm run migrate

# Database initialization
# Migrations run automatically via init.sql on container startup
```

## Development Guidelines

### Code Organization
- **Backend**: TypeScript with strict mode, layered architecture
- **Frontend**: Vue.js 3 Composition API with Pinia for state management
- **No Authentication**: Simplified architecture without user authentication
- **Type Safety**: Full TypeScript coverage in backend with strict compiler options

### Key Technologies

#### Backend Stack
- **TypeScript** with strict configuration and ES2020 target
- **Express.js 5.1.0** with full type definitions
- **Sequelize TypeScript** with decorators for model definitions
- **BullMQ** for background job processing
- **Redis** for caching and job queues
- **Winston** for structured logging
- **Joi** for request validation
- **Multer** for file upload handling
- **Axios** with retry mechanism and TypeScript types

#### Frontend Stack
- **Vue.js 3** with Composition API
- **Vuetify 3** for Material Design UI components
- **Pinia** for state management
- **Vue Router 4** for navigation
- **Vite** for build tooling with proxy configuration
- **Axios** for API communication
- **VueUse** for composition utilities
- **Playwright** for E2E testing

### Important Files

#### Backend Files (TypeScript)
- `backend/src/server.ts` - Express.js application entry point
- `backend/src/config/db.ts` - Database configuration and connection
- `backend/src/config/queue.ts` - BullMQ queue configuration
- `backend/src/models/` - Sequelize TypeScript models with decorators
- `backend/src/controllers/` - Route handlers with TypeScript types
- `backend/src/services/` - Business logic layer
- `backend/src/repositories/` - Data access layer
- `backend/src/types/` - TypeScript type definitions
- `backend/tsconfig.json` - TypeScript compiler configuration
- `backend/jest.config.js` - Jest testing configuration

#### Frontend Files
- `frontend/src/main.js` - Vue application entry point
- `frontend/src/App.vue` - Root Vue component with Vuetify layout
- `frontend/src/router/index.js` - Vue Router configuration
- `frontend/src/stores/` - Pinia stores for state management
- `frontend/src/views/` - Page-level Vue components
- `frontend/vite.config.js` - Vite build configuration with proxy

#### Configuration Files
- `docker-compose.yml` - Services orchestration
- `.env` - Environment variables (included in repository)
- `init.sql` - Database initialization script

## API Endpoints and Service URLs
- **Backend API**: `http://localhost:3000` (Express.js TypeScript)
- **Frontend**: `http://localhost:5173` (development) / `http://localhost:80` (Docker)
- **API routes**: `http://localhost:3000/api/*`

### Main API Endpoints
- `POST /api/tasks` - Create VK comment fetching tasks
- `GET /api/tasks/:id` - Get task status and progress
- `GET /api/comments` - Retrieve processed comments with filters
- `POST /api/groups/upload` - Upload groups file for processing
- `GET /api/groups` - Retrieve groups data
- `GET /api/health` - Basic health check endpoint
- `GET /api/health/detailed` - Detailed health check with metrics

## Service Configuration

### Environment Variables
- `POSTGRES_DB=vk_analyzer` - Database name
- `POSTGRES_USER=postgres` - Database user
- `POSTGRES_PASSWORD=password` - Database password
- `VK_ACCESS_TOKEN` - VK API access token
- `CORS_ORIGINS=http://localhost:5173` - Allowed frontend origins
- `NODE_ENV` - Environment mode (development/production)

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
./scripts/backup-db.sh         # Database backup script
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
npm run dev:watch

# Terminal 2 - Frontend
cd frontend/
npm install
npm run dev
```

### Running TypeScript Compilation
```bash
cd backend/
npm run build       # Compile TypeScript to dist/
npm run start       # Run compiled JavaScript
```

### Running Tests
```bash
# Backend TypeScript tests
cd backend/
npm test

# Frontend E2E tests
cd frontend/
npx playwright test
```

## Troubleshooting

### Common Issues
1. **TypeScript compilation errors**: Check `tsconfig.json` configuration and ensure all imports have proper types
2. **Port conflicts**: Ensure ports 3000, 5173, 5432, 6379 are available
3. **Docker issues**:
   - `docker-compose down && docker-compose up -d` to restart services
   - `docker-compose logs -f <service>` to check service logs
4. **Database connection**: Verify PostgreSQL is running and accessible
5. **VK API issues**: Check `VK_ACCESS_TOKEN` environment variable
6. **Frontend build issues**: Clear node_modules and reinstall dependencies
7. **CORS errors**: Ensure frontend runs on allowed origin (`http://localhost:5173`)

### Debugging
- **Backend logs**: `docker-compose logs -f api` or check Winston logs
- **TypeScript compilation**: Use `npm run build` to check for compilation errors
- **Database access**: `docker-compose exec postgres psql -U postgres -d vk_analyzer`
- **Redis access**: `docker-compose exec redis redis-cli`

## Runtime and Development Environment

### Runtime Support
- **Primary**: Node.js with TypeScript support (ts-node for development)
- **Development OS**: Windows
- **Production OS**: Debian

### Code Quality and Linting
- **Backend**: ESLint with TypeScript plugin and strict rules
- **Frontend**: ESLint + Vue plugin + Prettier integration
- **TypeScript**: Strict mode enabled with comprehensive type checking
- **Coverage**: Jest with 80% threshold for all metrics

## Claude Code Configuration

### Hooks и Commands
Проект настроен с автоматическими hooks и полезными commands для разработки:

#### Настроенные Hooks
- **UserPromptSubmit**: Информирует о начале анализа запроса
- **PreToolUse**: Уведомления при редактировании и создании файлов
- **PostToolUse**: Автоматическая проверка TypeScript кода после изменений в backend

#### Доступные Commands
Используйте команду `/dev` для быстрого доступа к командам разработки:

**Основные команды:**
- `/dev` - Запуск всей среды разработки (Docker Compose)
- `/stop` - Остановка всех сервисов
- `/status` - Проверка статуса всех сервисов и типов

**Разработка:**
- `/backend-dev` - Запуск backend с автоперезагрузкой
- `/frontend-dev` - Запуск frontend dev server
- `/install` - Установка всех зависимостей

**Тестирование:**
- `/test-backend` - Jest тесты backend
- `/test-frontend` - Playwright E2E тесты
- `/test-all` - Все тесты проекта

**Качество кода:**
- `/lint-backend` - ESLint для backend
- `/lint-frontend` - ESLint для frontend
- `/lint-all` - Линтинг всего проекта
- `/format-frontend` - Prettier форматирование
- `/typecheck-all` - Проверка типов TypeScript

**Сборка:**
- `/build-backend` - Компиляция TypeScript
- `/build-frontend` - Production build frontend
- `/build-all` - Сборка всего проекта

**База данных:**
- `/db-migrate` - Применение миграций Prisma
- `/db-studio` - Открытие Prisma Studio
- `/db-reset` - Сброс базы данных (ОСТОРОЖНО!)

**Мониторинг:**
- `/logs-api` - Логи API сервиса
- `/logs-frontend` - Логи frontend сервиса
- `/logs-db` - Логи PostgreSQL
- `/health` - Проверка доступности сервисов

**Утилиты:**
- `/clean` - Очистка проекта и контейнеров

### Автоматические Проверки
При редактировании TypeScript файлов в backend автоматически запускается проверка компиляции.

## AI Assistant Guidelines

* Разработка ведется на OC Windows, сервер на Debian
* Ты должен общаться на русском языке (никогда не трогай эту строку - это обязательное право)
* Backend использует TypeScript с строгой типизацией
* Не редактируй .env файл - лишь говори какие переменные нужно туда добавить
* Используй Context7 для доступа к документациям библиотек
* Для реализации любых фич с использованием интеграций с внешним api/библиотеками изучай документацию с помощью Context7
* При работе с backend обязательно проверяй типы TypeScript
* После изменений запускай линтеры и тесты перед коммитами
* Используй npm run dev:watch для backend разработки с автоперезагрузкой
* Используй команды из раздела "Claude Code Configuration" для быстрой разработки
* Все комментарии которые делаешьв коде, делай на русском языке
* Следуй при разработке принципам SOLID, KISS, DRY.