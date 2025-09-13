# Celery и Redis интеграция

## Обзор

Проект интегрирован с Celery для асинхронной обработки задач и Redis для кеширования и брокера сообщений.

## Архитектура

### Компоненты
- **Redis**: Брокер сообщений и кеш
- **Celery Worker**: Обработка задач
- **Celery Beat**: Планировщик задач
- **Flower**: Мониторинг Celery

### Очереди
- `default` - Общие задачи
- `parser` - Парсинг VK данных
- `notifications` - Уведомления
- `high_priority` - Высокоприоритетные задачи
- `low_priority` - Низкоприоритетные задачи

## Установка

### Зависимости
```bash
poetry install
```

### Переменные окружения
```bash
# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/0
REDIS_CELERY_URL=redis://localhost:6379/1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## Запуск

### Локальная разработка

#### 1. Запуск Redis
```bash
# Через Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Или через Makefile
make -f Makefile.celery start-redis
```

#### 2. Запуск Celery Worker
```bash
# Прямой запуск
poetry run python scripts/start_celery_worker.py

# Или через Makefile
make -f Makefile.celery start-worker
```

#### 3. Запуск Celery Beat
```bash
# Прямой запуск
poetry run python scripts/start_celery_beat.py

# Или через Makefile
make -f Makefile.celery start-beat
```

#### 4. Запуск Flower
```bash
# Прямой запуск
poetry run python scripts/start_flower.py

# Или через Makefile
make -f Makefile.celery start-flower
```

#### 5. Запуск всех сервисов
```bash
make -f Makefile.celery start-all
```

### Docker Compose

#### Development
```bash
docker-compose up -d
```

#### Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Использование

### Создание задач

```python
from src.common.tasks import health_check_task
from src.parser.tasks import parse_group_posts_task
from src.notifications.tasks import send_notification_task

# Простая задача
result = health_check_task.delay()
print(result.get())

# Задача с параметрами
result = parse_group_posts_task.delay(
    group_id=12345,
    count=100,
    offset=0
)

# Асинхронная задача
result = send_notification_task.delay(
    user_id=1,
    message="Test notification",
    notification_type="info"
)
```

### Мониторинг

#### Flower Web UI
- URL: http://localhost:5555
- Логин: admin
- Пароль: admin

#### API Endpoints
- `GET /api/v1/tasks/health` - Статус системы
- `GET /api/v1/tasks/` - Активные задачи
- `GET /api/v1/tasks/{task_id}` - Информация о задаче
- `POST /api/v1/tasks/{task_id}/cancel` - Отмена задачи

### Логирование

```bash
# Логи воркера
make -f Makefile.celery logs

# Логи Beat
make -f Makefile.celery logs-beat

# Логи Flower
make -f Makefile.celery logs-flower
```

## Доступные задачи

### Общие задачи
- `common.health_check` - Проверка здоровья
- `common.cache_cleanup` - Очистка кеша
- `common.send_notification` - Отправка уведомления
- `common.batch_process` - Пакетная обработка
- `common.periodic_cleanup` - Периодическая очистка

### Парсинг
- `parser.parse_group_posts` - Парсинг постов группы
- `parser.parse_post_comments` - Парсинг комментариев
- `parser.parse_group_info` - Информация о группе
- `parser.batch_parse_groups` - Пакетный парсинг
- `parser.cleanup_old_data` - Очистка старых данных

### Уведомления
- `notifications.send_email` - Отправка email
- `notifications.send_websocket` - WebSocket уведомления
- `notifications.send_push` - Push уведомления
- `notifications.send_bulk` - Массовые уведомления
- `notifications.cleanup_old_notifications` - Очистка уведомлений

### Морфологический анализ
- `morphological.analyze_text` - Анализ текста
- `morphological.analyze_batch` - Пакетный анализ
- `morphological.extract_keywords` - Извлечение ключевых слов
- `morphological.analyze_sentiment` - Анализ тональности
- `morphological.cleanup_old_analysis` - Очистка результатов

## Конфигурация

### Настройки Celery
```python
# src/common/celery_config.py
CELERY_CONFIG = {
    "broker_url": "redis://localhost:6379/1",
    "result_backend": "redis://localhost:6379/1",
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
}
```

### Настройки Redis
```python
# src/common/redis_client.py
REDIS_CONFIG = {
    "url": "redis://localhost:6379/0",
    "encoding": "utf-8",
    "decode_responses": True,
    "socket_connect_timeout": 5,
    "socket_timeout": 5,
    "retry_on_timeout": True,
}
```

## Мониторинг и отладка

### Проверка статуса
```bash
# Статус всех сервисов
make -f Makefile.celery status

# Тестирование задач
make -f Makefile.celery test-tasks

# Мониторинг в реальном времени
make -f Makefile.celery monitor
```

### Очистка
```bash
# Очистка очередей
make -f Makefile.celery purge

# Очистка логов
make -f Makefile.celery clean
```

## Troubleshooting

### Проблемы с Redis
```bash
# Проверка подключения
redis-cli ping

# Проверка очередей
redis-cli llen celery
```

### Проблемы с Celery
```bash
# Проверка воркеров
celery -A src.common.celery_config.celery_app inspect active

# Проверка статистики
celery -A src.common.celery_config.celery_app inspect stats
```

### Логи
```bash
# Логи Docker
docker-compose logs celery-worker
docker-compose logs celery-beat
docker-compose logs flower

# Логи приложения
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log
tail -f logs/flower.log
```

## Производительность

### Рекомендации
- Используйте отдельные Redis базы для кеша и Celery
- Настройте мониторинг памяти Redis
- Регулярно очищайте старые данные
- Используйте правильные очереди для разных типов задач

### Масштабирование
- Увеличьте количество воркеров
- Используйте несколько Redis инстансов
- Настройте кластеризацию для production
