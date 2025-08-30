# Docker Setup for FastAPI Backend

Этот документ описывает Docker конфигурацию для FastAPI backend с поддержкой Poetry и ARQ worker.

## Структура файлов

- `Dockerfile` - Оптимизированный Dockerfile для production
- `docker-entrypoint.sh` - Entrypoint скрипт для запуска приложения или worker
- `.dockerignore` - Исключения для Docker контекста
- `docker-compose.prod.yml` - Production конфигурация в корне проекта

## Dockerfile особенности

### Multi-stage build

- **Builder stage**: Установка зависимостей через Poetry
- **Runtime stage**: Минимальный образ для production

### Безопасность

- Non-root пользователь (UID 10001)
- Минимальные системные зависимости
- Использование virtual environment

### Оптимизация

- Кеширование pip зависимостей
- Исключение ненужных файлов через .dockerignore
- Health checks для приложения
- PYTHONUNBUFFERED=1 для корректного логирования

## Использование

### Запуск только backend сервисов

```bash
docker-compose --profile backend up -d
```

### Запуск всех сервисов

```bash
docker-compose up -d
```

### Просмотр логов

```bash
# Backend
docker-compose logs backend

# ARQ Worker
docker-compose logs arq_worker

# Все сервисы
docker-compose logs
```

### Масштабирование ARQ Worker

```bash
docker-compose up -d --scale arq_worker=3
```

## Переменные окружения

### Backend сервис

```bash
ENVIRONMENT=production
DEBUG=false
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://postgres:5432/vk_parser
CORS_ORIGINS=["http://localhost:3000", "http://nginx:80"]
```

### ARQ Worker

```bash
ENVIRONMENT=production
DEBUG=false
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://postgres:5432/vk_parser
```

## Health Checks

### Backend

- URL: `http://localhost:8000/health`
- Интервал: 30 секунд
- Таймаут: 10 секунд
- Попытки: 3

### ARQ Worker

- Команда: `pgrep -f arq`
- Интервал: 60 секунд

## Профили Docker Compose

- `backend` - только backend и arq_worker сервисы
- `admin` - включает pgadmin для управления БД

## Команды для разработки

### Сборка образов

```bash
docker-compose build backend arq_worker
```

### Запуск в development режиме

```bash
docker-compose --profile backend up --build
```

### Остановка и удаление

```bash
docker-compose --profile backend down -v
```

## Мониторинг

### Проверка состояния

```bash
docker-compose ps
docker stats
```

### Просмотр метрик

```bash
# Redis
docker exec -it fullstack_prod_redis redis-cli info

# PostgreSQL
docker exec -it fullstack_prod_postgres pg_isready -U postgres -d vk_parser
```

## Troubleshooting

### Backend не запускается

1. Проверить логи: `docker-compose logs backend`
2. Проверить переменные окружения
3. Проверить подключение к БД и Redis

### ARQ Worker не обрабатывает задачи

1. Проверить логи: `docker-compose logs arq_worker`
2. Проверить подключение к Redis
3. Проверить конфигурацию очереди в `src/arq/config.py`

### Высокое потребление памяти

1. Проверить настройки worker в `src/arq/worker.py`
2. Уменьшить `max_jobs` и `max_burst_jobs`
3. Добавить ограничения памяти в docker-compose

## Оптимизация производительности

### Для CPU-bound задач

```yaml
deploy:
  resources:
    limits:
      cpus: "2.0"
    reservations:
      cpus: "1.0"
```

### Для I/O-bound задач

```yaml
deploy:
  resources:
    limits:
      cpus: "0.5"
    reservations:
      cpus: "0.25"
```

## Безопасность

- Все сервисы запускаются под non-root пользователем
- Используются минимальные базовые образы
- Секреты передаются через переменные окружения
- Нет экспозиции внутренних портов наружу
