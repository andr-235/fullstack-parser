# Architecture

## System architecture
Проект использует MVC-подобную архитектуру для backend на Node.js с Express: Controllers (обработка HTTP-запросов), Services (бизнес-логика), Repositories (доступ к данным), Models (схемы данных). Frontend на Vue.js с Pinia для state management. Асинхронная обработка задач через taskService.js (вероятно с Redis очередями). Хранение в PostgreSQL для persistent data, Redis для cache/queues/tokens. Интеграция VK API через vkApi.js с async/await. Docker-compose для setup (backend, frontend, postgres, redis). Мониторинг не реализован явно.

## Source Code paths
- **backend/server.js**: Entry point - Express app setup, routes.
- **backend/src/controllers/**: HTTP handlers - taskController.js (fetch comments, task status).
- **backend/src/models/**: Data schemas - comment.js, post.js, task.js (вероятно Sequelize или raw SQL).
- **backend/src/repositories/**: Data access - dbRepo.js (PostgreSQL), vkApi.js (VK API calls).
- **backend/src/services/**: Business logic - taskService.js (async tasks), vkService.js (VK integration).
- **backend/src/utils/**: Shared - logger.js.
- **frontend/src/**: Vue app - App.vue, router/index.js, services/api.js (HTTP to backend), stores/ (Pinia: comments.js, tasks.js), views/ (CommentsList.vue, FetchComments.vue, TaskStatus.vue), components/ (ErrorMessage.vue, LoadingSpinner.vue).

## Key technical decisions
- **MVC-like structure**: Разделение concerns в backend для maintainability (Express routes -> controllers -> services -> repositories).
- **Async processing**: Async/await для API calls, taskService.js для background tasks (возможно Bull или Redis-based queues).
- **Rate limiting**: Вероятно в vkApi.js для VK API (3 req/s, не явно в структуре, но подразумевается).
- **Error handling**: Try-catch в services, logging via logger.js.
- **Security**: Env vars для secrets (VK tokens, DB creds), CORS в Express, input validation в controllers.
- **Frontend state**: Pinia stores для reactive data (tasks, comments), Vue Router для navigation.

## Design patterns in use
- **Repository pattern**: Абстракция доступа к VK API и DB в repositories/.
- **Service layer**: Инкапсуляция бизнес-логики (e.g., vkService.js для VK operations).
- **MVC pattern**: В backend (Controllers handle requests, Models for data, Views absent as API-only).
- **State management**: Pinia в frontend для centralized state (stores для comments/tasks).
- **Singleton/Factory**: Возможно для DB connections в dbRepo.js.

## Component relationships
- Frontend (Vue views/stores) -> api.js (HTTP) -> Express API (controllers) -> Services (taskService, vkService) -> Repositories (vkApi, dbRepo) -> VK API/PostgreSQL/Redis.
- API endpoint -> taskService -> Queue (Redis) -> Background processing -> Update DB.
- Redis: Cache tokens, queue tasks.
- PostgreSQL: Persistent storage for comments, posts, tasks.

## Critical implementation paths
1. **VK Data Flow**: Frontend FetchComments.vue -> api.js POST /api/tasks -> taskController.js -> taskService.js -> vkService.js/vkApi.js -> VK API -> Store in DB via dbRepo.js.
2. **Auth Flow**: VK OAuth (implicit) -> Store token in Redis -> Use in vkApi.js.
3. **Task Status**: Frontend TaskStatus.vue -> GET /api/tasks/:id -> taskController.js -> taskService.js -> Return status from DB/Redis.

## Диаграмма архитектуры
```
Frontend (Vue/Pinia) -> API Service -> Express Controllers -> Services (task/vk)
                       ↓
                  Redis Queue -> Background Tasks -> VK API/DB Repositories
                       ↓                    ↓
                  Redis Cache ← Comments Models -> PostgreSQL