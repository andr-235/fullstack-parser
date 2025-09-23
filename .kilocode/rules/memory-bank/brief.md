# Brief

## Обзор проекта
Проект - backend-система на Go для анализа комментариев из VK API. Использует Clean Architecture для разделения слоев: Domain (entities как VKComment, VKPost), Use Cases (VKAuthUseCase, VKCommentsUseCase), Repository (VKRepository, Postgres), Delivery (Gin handlers). Асинхронная обработка через Asynq, хранение в PostgreSQL, кэш/токены в Redis. Интеграция VK API с rate limiting и retry.

## Цели
- Автоматизированный сбор комментариев к постам VK (wall.getComments).
- Морфологический анализ (keywords, sentiment) с placeholder в analysis.go.
- Хранение и поиск результатов для insights (мониторинг мнений, тренды).
- Масштабируемость: обработка 1000+ comments/min, миграция с Python для performance.

## Scope
- Backend only (~50% ready): entities, usecases/repos/handlers реализованы частично (Asynq placeholder), тесты unit/integration.
- Нет frontend.
- Dependencies: Gin, GORM, Asynq, resty, go-redis.
- Setup: docker-compose (postgres/redis/api/worker), env vars for secrets.
- Future: full Asynq, NLP lib for analysis, full tests >80%, frontend.