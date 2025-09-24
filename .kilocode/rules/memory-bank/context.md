# Context

## Текущий фокус
Обновление Memory Bank для JS-проекта (Node.js/Express backend, Vue.js frontend) по анализу VK комментариев. Адаптация под MVC-like структуру, async processing и VK integration.

## Недавние изменения
- Полная перезапись frontend views (FetchComments.vue, TaskStatus.vue, CommentsList.vue) и stores (tasks.js, comments.js) под новые API backend: POST /api/tasks с token в body, GET /api/tasks/:id для статуса с progress, GET /api/comments?task_id= для комментариев с пагинацией/фильтрами. Нет аутентификации, токен в body. Использован BullMQ для async задач (статусы pending/processing/completed/error).
- Обновление architecture.md и tech.md под Node.js/Express, taskService.js для async tasks, vkApi.js для VK API.
- Controllers: taskController.js (fetch comments, task status).
- Services: vkService.js (VK operations), taskService.js (async tasks с placeholders).
- Models: comment.js, post.js, task.js (схемы данных).
- Repositories: dbRepo.js (PostgreSQL), vkApi.js (VK API calls с rate limiting).
- Frontend: Pinia stores (comments.js, tasks.js), views (FetchComments.vue, TaskStatus.vue, CommentsList.vue), components (ErrorMessage.vue, LoadingSpinner.vue).
- Тесты: unit (taskService.test.js, vkApi.test.js), integration (api.test.js).
- Setup: docker-compose.yml (postgres/redis/backend/frontend), package.json (dependencies).

Проект на стадии ~50% готовности backend и frontend, миграция с Python завершена.

## Следующие шаги
- Полная реализация async processing в taskService.js (BullMQ с Redis queues для background tasks).
- Интеграция morphological analysis (NLP lib для keywords/sentiment).
- Полные тесты (>80% coverage, Jest/Vitest).
- Frontend enhancements (визуализация insights, дополнительные views/stores).