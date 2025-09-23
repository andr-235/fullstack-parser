# Техническое задание: Backend для сбора постов и комментариев VK групп на Express.js

## 1. Обзор проекта
Проект представляет собой RESTful backend на Node.js с использованием Express.js для автоматизированного сбора данных из VK API. Backend будет парсить указанные группы (публичные сообщества VK), собирать последние 10 постов из каждой группы и все комментарии к этим постам (с пагинацией). Данные хранятся в PostgreSQL для последующего анализа (совместимо с текущим Go-backend). 

Это альтернативная реализация текущего Go-проекта, ориентированная на быструю разработку и интеграцию с frontend (Vue.js из workspace). Основные вызовы: соблюдение rate limits VK API (3 запроса/сек), обработка больших объемов комментариев (retry, пагинация) и scalability для нескольких групп одновременно.

**Версия ТЗ:** 1.0  
**Дата:** 2025-09-23  
**Статус:** Готово к реализации  

## 2. Цели и задачи
### Цели
- Автоматизировать сбор данных из VK групп без ручного вмешательства.
- Обеспечить надежную интеграцию с VK API с учетом ограничений (rate limit 3 req/s, 5000 вызовов/сутки).
- Хранить собранные данные в структурированной форме для анализа (посты, комментарии, метаданные).
- Поддерживать асинхронный сбор для scalability (обработка до 10 групп параллельно, ~1000 комментариев/мин).
- Интегрировать с существующим frontend для запуска сбора и просмотра результатов.

### Задачи
- Реализовать API для ввода списка групп, запуска сбора и получения результатов.
- Обработать аутентификацию VK (access_token из env).
- Собрать данные: последние 10 постов (wall.get), все комментарии (wall.getComments с offset/limit).
- Хранить данные в PostgreSQL с моделями для постов и комментариев.
- Обеспечить error handling, logging и мониторинг.

## 3. Требования к функционалу
### Функциональные требования
- **Ввод групп:** POST /api/groups - принять массив ID групп (например, [-123456] для сообщества), сохранить в БД как задачу.
- **Запуск сбора:** POST /api/collect/:taskId - асинхронно запустить сбор (возвращает taskId и status: 'pending').
- **Статус задачи:** GET /api/tasks/:taskId - вернуть прогресс (pending, in_progress, completed, failed) и метрики (посты собрано, комментарии собрано).
- **Получение результатов:** GET /api/results/:taskId - вернуть JSON с постами и комментариями (фильтры: groupId, postId).
- **Список задач:** GET /api/tasks - пагинированный список задач с статусами.

### Нефункциональные требования
- **Производительность:** Асинхронный сбор с concurrency limit (max 5 параллельных запросов к VK). Обработка пагинации комментариев (offset до 1000, count=100).
- **Надежность:** Retry с exponential backoff (max 3 попытки) на ошибки VK API (например, rate limit). Логирование с Winston.
- **Безопасность:** Валидация input (Joi), токены в .env, CORS для frontend.
- **Масштабируемость:** Поддержка нескольких задач параллельно; опционально BullMQ для очередей (аналог Asynq).
- **Тестирование:** Unit-тесты (Jest) >80% coverage, integration-тесты для API и VK mocks.

### Примеры API запросов/ответов
- **POST /api/groups**  
  Request: `{ "groups": [-123456, -789012] }`  
  Response: `{ "taskId": "uuid-123", "status": "created" }` (201)

- **POST /api/collect/task-123**  
  Response: `{ "taskId": "task-123", "status": "pending", "startedAt": "2025-09-23T22:00:00Z" }` (202)

- **GET /api/tasks/task-123**  
  Response: `{ "status": "completed", "progress": { "posts": 20, "comments": 1500 }, "errors": [] }` (200)

- **GET /api/results/task-123?groupId=-123456**  
  Response: `{ "posts": [{ "id": 1, "text": "...", "comments": [{ "id": 1, "text": "...", "author": "user1" }] }], "totalComments": 750 }` (200)

Коды ошибок: 400 (invalid input), 429 (rate limit), 500 (internal error).

## 4. Архитектура
### Общая структура
- **Фреймворк:** Express.js (v4.18+).
- **Слои (адаптация Clean Architecture):**
  - **Controllers (Delivery):** Обработка HTTP-запросов (routes/groups.js, routes/tasks.js).
  - **Services (Use Cases):** Бизнес-логика (vkService.js для сбора, taskService.js для управления задачами).
  - **Repositories (Data):** Доступ к VK API (vkApi.js) и БД (postgresRepo.js с Sequelize).
  - **Models (Domain):** Схемы данных (Post, Comment, Task).
- **Внешние зависимости:** Axios для HTTP, rate-limiter-flexible для rate limiting, BullMQ (опционально) для очередей, Sequelize для ORM.

### Диаграмма архитектуры (Mermaid)
```mermaid
graph TD
    A[Frontend] --> B[Express API Controllers]
    B --> C[Task Service]
    C --> D[VK Service]
    D --> E[VK API Repository<br/>(Axios + Rate Limiter)]
    E --> F[VK API<br/>(wall.get, wall.getComments)]
    C --> G[DB Repository<br/>(Sequelize)]
    G --> H[PostgreSQL<br/>(Posts, Comments, Tasks)]
    I[BullMQ Queue] -.->|Async Tasks| D
    J[Redis] -.->|Queue Storage| I
```

- **Поток данных:** API → Service → Repository → VK API/DB. Асинхронно: enqueue task в BullMQ, worker обрабатывает сбор.
- **Файловая структура:**
  ```
  backend/
  ├── src/
  │   ├── controllers/ (routes)
  │   ├── services/ (vkService.js, taskService.js)
  │   ├── repositories/ (vkApi.js, dbRepo.js)
  │   ├── models/ (post.js, comment.js, task.js)
  │   ├── config/ (db.js, vk.js)
  │   └── utils/ (rateLimiter.js, logger.js)
  ├── tests/ (unit, integration)
  ├── package.json
  └── server.js
  ```

## 5. Интеграция с VK API
- **Методы:** 
  - wall.get: owner_id (группа, отрицательный), count=10, offset=0 для последних постов.
  - wall.getComments: owner_id, post_id, offset=0, count=100, extended=1 (для авторов); пагинация до items.length < count.
- **Rate limiting:** Использовать rate-limiter-flexible (3 req/s, burst=10). Ждать перед запросом.
- **Retry:** Axios interceptor с retry-axios (exponential backoff: 1s, 2s, 4s; max 3).
- **Аутентификация:** access_token из process.env.VK_TOKEN; version=5.131.
- **Обработка ошибок:** Парсить response.error (code, message); логировать, возвращать 429/500.

## 6. Хранение данных
- **БД:** PostgreSQL (для consistency с текущим проектом; альтернатива MongoDB для JSON-like данных).
- **Модели (Sequelize schemas):**
  - **Task:** id (UUID), groups (JSON array), status (enum: pending/in_progress/completed/failed), createdAt, updatedAt, metrics (JSON: {posts: 0, comments: 0}).
  - **Post:** id (VK post_id), groupId (int), text (string), date (timestamp), likes (int), taskId (foreign key).
  - **Comment:** id (VK comment_id), postId (foreign key), text (string), authorId (int), authorName (string), date (timestamp), likes (int).
- **Миграции:** Использовать sequelize-cli для таблиц и индексов (на groupId, postId для быстрых запросов).

## 7. Безопасность
- **Секреты:** .env для VK_TOKEN, DB_URL; игнорировать в .gitignore.
- **Валидация:** Joi для body/query params (например, groups: array of numbers).
- **Аутентификация:** Опционально JWT для API (если интеграция с frontend); CORS для localhost:5173 (Vite).
- **Защита:** Helmet для headers, rate limiting на API (express-rate-limit, 100 req/min per IP).

## 8. Развертывание и setup
- **Зависимости (package.json):** express, axios, sequelize, pg, rate-limiter-flexible, joi, winston, bullmq (опционально), jest.
- **Запуск:** node server.js (порт 3000); npm run dev (nodemon).
- **Docker:** 
  - Dockerfile: FROM node:18, COPY ., npm install, CMD ["node", "server.js"].
  - docker-compose.yml: services для app, postgres (image:15), redis (для очередей); volumes для data, env_file: .env.
- **CI/CD:** GitHub Actions: test (jest), build (docker), deploy (если нужно).
- **Мониторинг:** Winston для логов; опционально Prometheus для метрик.

## 9. Риски и предположения
- Риски: VK API изменения (мониторить docs.vk.com); высокая нагрузка на rate limits при больших группах.
- Предположения: Публичные группы (без приватного доступа); access_token с правами wall.
- Следующие шаги: Реализация по ТЗ, unit-тесты, интеграция с frontend.