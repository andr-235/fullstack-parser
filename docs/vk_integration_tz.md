# Техническое задание на интеграцию VK API в backend проекта

## Введение

### Цель документа
Настоящее техническое задание (ТЗ) определяет требования к интеграции API социальной сети VKontakte (VK API) в backend проекта на базе Go с использованием Clean Architecture. Интеграция позволит получать данные о комментариях, постах и пользователях из VK для анализа в системе. Документ обновлен с учетом миграции проекта с Python/FastAPI на Go/Gin и текущего состояния разработки (backend готовность ~40%).

### Область применения
Интеграция охватывает:
- Получение комментариев и постов из указанных сообществ.
- Обработку данных в соответствии с доменной моделью проекта (комментарии, ключевые слова).
- Асинхронную обработку запросов через Asynq с морфологическим анализом русского языка.
- Хранение обработанных данных в PostgreSQL через Repository слой.

### Предположения
- Проект использует Clean Architecture: Domain, Use Cases, Repository, Delivery.
- Backend на Go с Gin, GORM, PostgreSQL, Redis, Asynq.
- Токены VK API хранятся в переменных окружения.
- Проект находится на стадии реализации базовых API endpoints (приоритет №1).

## Требования

### Функциональные требования
1. **Аутентификация и авторизация**:
   - Поддержка Implicit Flow для VK OAuth 2.0.
   - Хранение access_token в Redis с TTL.
   - Обновление токена при истечении.

2. **Получение данных из VK**:
   - Метод для получения комментариев из поста: `wall.getComments`.
   - Метод для получения постов: `wall.get`.
   - Фильтрация по owner_id (ID сообщества).
   - Пагинация с offset и count (max 100 на запрос).
   - Обработка ошибок VK API (rate limits, временные блокировки).

3. **Обработка данных и морфологический анализ**:
   - Маппинг VK-ответов на доменные модели (Comment, User, VKComment).
   - Выявление ключевых слов с приоритетами.
   - Сохранение в PostgreSQL через Repository слой.

4. **Асинхронная обработка**:
   - Интеграция с Asynq для фоновой обработки тяжелых операций.
   - Task type: "vk:fetch_comments" для получения комментариев.
   - Task type: "morphological:analyze" для анализа текста.
   - Retry логика для неудачных задач.

5. **API Endpoints**:
   - POST /api/vk/fetch-comments: Параметры — post_id, owner_id. Возвращает ID задачи Asynq.
   - GET /api/vk/task/{task_id}: Статус задачи и результаты.
   - GET /api/comments: Получение обработанных комментариев с фильтрацией.

### Интеграция с VK API
Интеграция с VK API обеспечивает загрузку комментариев и данных о вовлеченности для последующего анализа в системе. Это соответствует высокому приоритету реализации API для комментариев (backend готовность ~40%) и вписывается в домен comments.

#### Аутентификация
- Пользователь псам вставит в переменные окружения токен (placeholder для token в конфигурации: `VK_ACCESS_TOKEN=your_token_here`).
- Безопасность: токен не хранится в коде, только в env; использование HTTPS для всех запросов.

#### Ключевые методы
- **wall.getComments**: Загрузка комментариев к посту. Параметры: owner_id (ID владельца поста, отрицательный для групп), post_id (ID поста), access_token, v=5.131.
- **likes.getList**: Получение списка лайков для анализа вовлеченности. Параметры: type (post/comment), owner_id, item_id, access_token, v=5.131.

#### Примеры запросов и ответов
**Пример запроса wall.getComments (JSON):**
```
GET https://api.vk.com/method/wall.getComments?owner_id=-12345678&post_id=1&access_token={VK_ACCESS_TOKEN}&v=5.131
```

**Пример ответа (JSON, упрощенный):**
```json
{
  "response": {
    "items": [
      {
        "id": 1,
        "from_id": 1000001,
        "date": 1695283200,
        "text": "Отличный пост! Рекомендую всем.",
        "likes": {
          "count": 5,
          "user_likes": 0
        },
        "reply_count": 2
      }
    ],
    "count": 1
  }
}
```

**Пример запроса likes.getList (JSON):**
```
GET https://api.vk.com/method/likes.getList?type=post&owner_id=-12345678&item_id=1&access_token={VK_ACCESS_TOKEN}&v=5.131
```

**Пример ответа (JSON, упрощенный):**
```json
{
  "response": {
    "count": 10,
    "items": [1000001, 1000002, 1000003]
  }
}
```

#### Обработка rate limits
- Лимит: 3 запроса в секунду (без специального токена; с токеном — до 5000 в сутки).
- Реализация в Go: Использовать rate limiter (например, golang.org/x/time/rate) в VKRepository.
- Retry logic: При ошибке 429 (Too Many Requests) — экспоненциальный backoff (sleep 1s, затем 2s, max 5 попыток).
- Мониторинг: Метрики Prometheus для отслеживания запросов/сек и ошибок rate limit.

#### Связь с доменом comments
- **Загрузка**: Данные из wall.getComments маппятся на доменную модель Comment в Use Cases слое.
- **Хранение**: Сохранение в PostgreSQL через CommentRepository (GORM).
- Интеграция: Соответствует критическому пути "Управление комментариями" в архитектуре (Frontend → API → Handler → Use Case → Repository → Asynq).

### Нефункциональные требования
- **Производительность**: Обработка до 1000 комментариев/мин. Асинхронно.
- **Масштабируемость**: Горизонтальное масштабирование workers через Asynq.
- **Безопасность**: Токены в env, rate limiting, input validation.
- **Логирование**: Structured logs с correlation ID, error tracking.
- **Качество кода**: Unit тесты >80% покрытия, интеграционные тесты.

## Архитектура

### Общая структура
Интеграция VK API вписывается в Clean Architecture с доменной организацией кода:
- **Delivery**: HTTP handlers в `internal/delivery/http/handlers/vk/`.
- **Use Cases**: `internal/usecase/vk/` — VKFetcherUseCase, VKAuthUseCase.
- **Domain**: Новые entities в `internal/domain/vk/` (VKComment, VKToken, VKUser).
- **Repository**: `internal/repository/vk/` — интерфейс VKRepository с HTTP client реализацией.

### Домены и компоненты
1. **VK Domain** (`internal/domain/vk/`):
   - VKComment, VKPost, VKUser entities
   - VKToken value object
   - VK API error types

2. **VK Use Cases** (`internal/usecase/vk/`):
   - VKAuthUseCase: OAuth аутентификация
   - VKCommentsUseCase: Получение и обработка комментариев
   - VKPostsUseCase: Получение постов

3. **VK Repository** (`internal/repository/vk/`):
   - VKRepository interface
   - HTTPClient реализация с rate limiting
   - Response mapping на доменные модели

4. **Asynq Tasks**:
   - Task type: "vk:fetch_comments" — получение комментариев
   - Task type: "vk:process_comments" — обработка и анализ
   - Payload: JSON с post_id, owner_id, options


### Диаграмма архитектуры
```
Frontend → API Handler (Gin) → VK Use Cases → VK Repository (HTTP to VK API)
                      ↓
                 Asynq Queue → Worker → Morphological Analysis → PostgreSQL
                      ↓                    ↓
                 Redis Cache ← Comments Domain → Keywords Domain
```

## Реализация

### Текущий прогресс и приоритеты
Проект находится на стадии реализации базовых компонентов (backend готовность ~40%). Приоритет №1 - реализация API endpoints для комментариев, приоритет №2 - морфологический анализ русского языка.

### Шаги разработки
1. **Базовая инфраструктура** (Приоритет: Высокий):
   - Настроена Clean Architecture с доменами
   - Подключены PostgreSQL, Redis, Asynq
   - Middleware для CORS, логирования, метрик

2. **Реализовать VK Domain и Repository** (Приоритет: Высокий):
   - Создать VK models в `internal/domain/vk/`
   - Реализовать VKRepository interface в `internal/repository/vk/`
   - Добавить HTTP client с rate limiting
   - Добавить зависимости: `go get github.com/go-resty/resty/v2`

3. **Создать Use Cases для VK** (Приоритет: Высокий):
   - VKAuthUseCase в `internal/usecase/vk/`
   - VKCommentsUseCase для получения комментариев
   - VKPostsUseCase для получения постов

4. **Реализовать API Handlers** (Приоритет: Высокий):
   - VK handlers в `internal/delivery/http/handlers/vk/`
   - Routes в `cmd/api/main.go`
   - JWT middleware для аутентификации

5. **Настроить Asynq Tasks** (Приоритет: Высокий):
   - Task "vk:fetch_comments" в `cmd/worker/main.go`
   - Task "vk:process_comments" для обработки
   - Интеграция с морфологическим анализом

6. **Интегрировать морфологический анализ** (Приоритет: Высокий):
   - Использовать `internal/domain/morphological/`
   - Асинхронная обработка через Asynq
   - Кеширование результатов в Redis

7. **Написать тесты** (Приоритет: Средний):
   - Unit тесты для VK client (>80% покрытие)
   - Integration тесты для API endpoints
   - Load тесты для производительности

### Конфигурация
- **VK API**: VK_CLIENT_ID, VK_CLIENT_SECRET, VK_REDIRECT_URI, VK_COMMUNITY_ID, VK_ACCESS_TOKEN=your_token_here
- **База данных**: DATABASE_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
- **Redis**: REDIS_URL, REDIS_HOST, REDIS_PORT
- **JWT**: JWT_SECRET, JWT_EXPIRATION
- **Сервер**: SERVER_PORT=8080, GIN_MODE=release

## Тестирование

### Текущее состояние и приоритеты
Тестирование имеет **средний приоритет** в проекте (текущее покрытие: 0%). Планируется внедрение TDD подхода и достижение >80% покрытия кода тестами.

### Стратегия тестирования
- **Unit тесты**: Изолированное тестирование функций и методов (>80% покрытие)
- **Integration тесты**: Тестирование взаимодействия между компонентами
- **E2E тесты**: Сквозное тестирование API endpoints
- **Load тесты**: Нагрузочное тестирование производительности

### Компоненты для тестирования
1. **VK Client** (`internal/repository/vk/`):
   - Unit: Mock HTTP client для VK API
   - Integration: Testcontainers для Redis/PostgreSQL
   - Цель: 100% покрытие VKRepository методов

2. **Use Cases** (`internal/usecase/vk/`):
   - Unit: Mock репозиториев и внешних зависимостей
   - Integration: Тестирование бизнес-логики с реальными компонентами
   - Цель: Валидация обработки данных и ошибок

3. **API Handlers** (`internal/delivery/http/handlers/vk/`):
   - Unit: Тестирование HTTP handlers с mock context
   - Integration: E2E тесты API endpoints
   - Цель: 100% покрытие всех endpoint'ов

4. **Asynq Tasks** (`cmd/worker/`):
   - Unit: Тестирование обработчиков задач
   - Integration: Тестирование очереди задач с Redis
   - Цель: Валидация асинхронной обработки

5. **Морфологический анализ**:
   - Unit: Mock анализатора для быстрого тестирования
   - Performance: Бенчмарки производительности
   - Цель: Обеспечение качества анализа русского языка

### Инструменты тестирования
- **Backend**: testify (Go testing toolkit), testcontainers
- **Load testing**: k6 для API endpoints (цель: 100 req/s)
- **Coverage**: Инструменты для измерения покрытия кода
- **CI/CD**: Автоматическое тестирование в пайплайне

### Метрики качества
- **Покрытие кода**: >80% unit тестами
- **Время выполнения**: <30 сек для полного тестового набора
- **Надежность**: <1% flaky тестов
- **Документирование**: README для каждого модуля с примерами тестирования

## Мониторинг и Observability

### Текущее состояние и приоритеты
Мониторинг имеет **низкий приоритет** в проекте (текущее состояние: 0%). Планируется настройка комплексной системы мониторинга для обеспечения стабильности и производительности VK интеграции.

### Метрики для отслеживания

#### HTTP и API метрики
- **Request/Response метрики**: latency, throughput, error rates по endpoint'ам
- **VK API использование**: rate limits, quota usage, API response times
- **Аутентификация**: JWT токены, login/logout статистика

#### Бизнес-метрики
- **Обработка комментариев**: comments processed, average processing time
- **Пользовательская активность**: active users, API usage patterns
- **Качество данных**: successful vs failed comment retrievals
- **Морфологический анализ**: analysis completion rates, accuracy metrics

#### Системные метрики
- **Инфраструктура**: CPU, memory, disk usage, network I/O
- **База данных**: connection pool usage, query performance, slow queries
- **Redis**: hit/miss rates, memory usage, key eviction rates
- **Asynq очереди**: task queue length, processing time, retry rates

#### Кастомные метрики VK интеграции
- **VK API health**: API availability, response times, error rates
- **Comment processing pipeline**: fetch → process → store success rates
- **Rate limiting**: VK API quota usage, throttling events
- **Data quality**: comment text quality, encoding issues, size distribution

### Инструменты мониторинга

#### Основные инструменты
- **Prometheus** - сбор метрик с автоматическим обнаружением сервисов
- **Grafana** - визуализация с готовыми дашбордами для Go приложений
- **Alertmanager** - централизованная система алертинга
- **Structured logging** - JSON логи с correlation IDs и trace context

#### Дополнительные инструменты
- **Jaeger/OpenTelemetry** - distributed tracing для запросов к VK API
- **Loki** - централизованный сбор и поиск логов
- **VictoriaMetrics** - long-term storage для метрик
- **Blackbox exporter** - мониторинг доступности VK API endpoints

### Дашборды и алертинг

#### Основные дашборды
1. **VK Integration Overview**:
   - API usage и health status
   - Comment processing statistics
   - Error rates и retry statistics

2. **Performance Dashboard**:
   - Response times по всем endpoint'ам
   - Database и Redis performance
   - System resources usage

3. **Business Metrics**:
   - Daily/weekly comment processing volumes
   - User activity patterns
   - VK API quota consumption

4. **Error Analysis**:
   - Top errors по типам и endpoint'ам
   - VK API error patterns
   - Failed task analysis

#### Правила алертинга
- **Критические**: VK API недоступен >5 мин, error rate >5%
- **Важные**: Queue length >100, processing time >30 сек
- **Информационные**: High memory usage, quota usage >80%

### Логирование

#### Структурированное логирование
- **Уровни**: DEBUG, INFO, WARN, ERROR, FATAL
- **Correlation IDs**: для трейсинга запросов через все слои
- **Context**: user_id, request_id, trace_id, span_id
- **VK API логи**: API calls, response times, error details

#### Лог-файлы
- **Application logs**: `/var/log/app/vk-integration.log`
- **VK API logs**: `/var/log/app/vk-api.log`
- **Asynq worker logs**: `/var/log/app/worker.log`
- **Error logs**: `/var/log/app/errors.log`

### Настройка мониторинга

#### Конфигурационные файлы
- `monitoring/prometheus.yml` - правила сбора метрик
- `monitoring/alerts.yml` - правила алертинга
- `backend/grafana-dashboard.json` - готовые дашборды
- `docker-compose.monitoring.yml` - сервисы мониторинга

#### Метрики приложения
```go
// HTTP метрики
httpRequestsTotal{endpoint="/api/v1/vk/comments", method="GET", status="200"}
httpRequestDuration{endpoint="/api/v1/vk/comments", method="GET", quantile="0.95"}

// Бизнес-метрики
vkCommentsProcessedTotal{status="success"}
vkCommentsProcessedTotal{status="failed"}
vkApiCallsTotal{api="comments.get", status="200"}

// Системные метрики
dbConnectionsActive{name="postgres"}
redisMemoryUsage{name="comments_cache"}
asynqQueueLength{name="vk_processing"}
```

### Процедуры реагирования

#### Runbook для инцидентов
1. **VK API недоступен**: проверить статус VK API, переключиться на fallback
2. **High error rate**: проверить логи, проанализировать ошибки, откатить изменения
3. **Queue backlog**: масштабировать worker'ы, проверить processing логику
4. **Database issues**: проверить connection pool, оптимизировать запросы

#### Post-mortem процесс
- Автоматический сбор метрик и логов инцидента
- Анализ root cause с timeline событий
- Рекомендации по предотвращению повторения
- Обновление документации и процедур

## Риски и ограничения
- Rate limits VK (3 req/s без токена, 5000/dzień с).
- Изменения в VK API — мониторить docs.
- Обработка ошибок: 429 Too Many Requests — retry с backoff.

## Заключение
Интеграция обеспечит сбор данных из VK для анализа. Срок: 2 недели. Ответственный: Backend team.