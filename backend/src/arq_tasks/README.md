# ARQ Модуль - Асинхронные Задачи

Модуль для управления асинхронными задачами через ARQ (Async Redis Queue) в приложении VK Comments Parser.

## Обзор

ARQ модуль предоставляет:

- ✅ Управление очередью задач через Redis
- ✅ Асинхронное выполнение тяжелых операций
- ✅ Мониторинг статуса задач
- ✅ Повторные попытки выполнения
- ✅ Интеграцию с FastAPI
- ✅ Docker поддержку для воркера

## Архитектура

```
src/arq/
├── __init__.py          # Экспорт основных компонентов
├── service.py           # Функции задач ARQ
├── config.py            # Конфигурация ARQ
├── schemas.py           # Pydantic модели API
├── router.py            # REST API эндпоинты
├── worker.py            # Настройки воркера ARQ
├── models.py            # Модели базы данных
├── dependencies.py      # FastAPI зависимости
├── exceptions.py        # Исключения модуля
├── utils.py            # Вспомогательные функции
└── README.md           # Эта документация
```

## Доступные Задачи

### Парсинг и Обработка Данных

- `parse_vk_comments` - Парсинг комментариев VK
- `analyze_text_morphology` - Морфологический анализ текста
- `extract_keywords` - Извлечение ключевых слов
- `process_batch_comments` - Пакетная обработка комментариев

### Система и Администрирование

- `send_notification` - Отправка уведомлений
- `generate_report` - Генерация отчетов
- `cleanup_old_data` - Очистка старых данных
- `update_statistics` - Обновление статистики
- `backup_database` - Создание резервной копии БД

## Быстрый Старт

### 1. Запуск Воркера

```bash
# Через Docker Compose (рекомендуется)
docker-compose -f docker-compose.prod.yml up arq_worker

# Или напрямую через arq CLI
arq src.arq_tasks.worker.worker_settings

# С дополнительными опциями
arq src.arq_tasks.worker.worker_settings --watch /app/src --verbose
```

### 2. Добавление Задачи

```python
from src.infrastructure.arq_service import arq_service

# Добавить задачу в очередь
job_id = await arq_service.enqueue_job(
    function_name="parse_vk_comments",
    group_id=12345,
    limit=100
)
```

### 3. Проверка Статуса Задачи

```python
# Через API
GET /api/v1/arq/status/{job_id}

# Или через сервис
status = await arq_service.get_job_status(job_id)
```

## API Эндпоинты

### Основные Эндпоинты ARQ

- `POST /api/v1/arq/enqueue` - Добавить задачу в очередь
- `GET /api/v1/arq/status/{job_id}` - Получить статус задачи
- `GET /api/v1/arq/result/{job_id}` - Получить результат задачи
- `DELETE /api/v1/arq/abort/{job_id}` - Отменить задачу
- `GET /api/v1/arq/queue/info` - Информация об очереди
- `GET /api/v1/arq/health` - Проверка здоровья ARQ

### Специализированные Эндпоинты

#### Комментарии

- `POST /api/v1/comments/parse/vk/async` - Асинхронный парсинг VK
- `POST /api/v1/comments/analyze/async` - Анализ комментариев
- `POST /api/v1/comments/report/async` - Генерация отчетов
- `POST /api/v1/comments/cleanup/async` - Очистка данных

## Примеры Использования

### Парсинг Комментариев VK

```python
# Быстрый способ через API комментариев
POST /api/v1/comments/parse/vk/async?group_id=12345&limit=100

# Ответ
{
    "success": true,
    "message": "Задача парсинга добавлена в очередь",
    "data": {
        "job_id": "01hxyz...",
        "function": "parse_vk_comments",
        "group_id": 12345,
        "limit": 100,
        "status_url": "/api/v1/arq/status/01hxyz...",
        "result_url": "/api/v1/arq/result/01hxyz..."
    }
}
```

### Мониторинг Задачи

```python
# Проверить статус
GET /api/v1/arq/status/01hxyz...

# Ответ
{
    "job_id": "01hxyz...",
    "status": "complete",
    "result": {
        "comments_parsed": 100,
        "comments_saved": 95
    },
    "finished_at": "2024-01-15T10:30:00Z"
}
```

### Пакетная Обработка

```python
# Анализ нескольких комментариев
POST /api/v1/comments/analyze/async?comment_ids=1,2,3,4,5&analysis_type=morphology
```

## Конфигурация

### Основные Настройки

```python
# В config.py или через переменные окружения
ARQ_MAX_JOBS=10              # Максимум одновременных задач
ARQ_JOB_TIMEOUT=300          # Таймаут задачи (секунды)
ARQ_MAX_TRIES=3              # Максимум попыток
ARQ_POLL_DELAY=0.5           # Задержка опроса очереди
ARQ_QUEUE_NAME=arq:queue     # Имя очереди Redis
```

### Переменные Окружения

```bash
# ARQ настройки
ARQ_MAX_JOBS=10
ARQ_JOB_TIMEOUT=300
ARQ_MAX_TRIES=3
ARQ_POLL_DELAY=0.5
ARQ_QUEUE_NAME=arq:queue
ARQ_BURST_MODE=false

# Redis подключение
REDIS_URL=redis://redis:6379/0
```

## Мониторинг и Отладка

### Health Check

```bash
# Проверка здоровья ARQ
GET /api/v1/arq/health

# Ответ
{
    "service": "ARQ",
    "healthy": true,
    "timestamp": "2024-01-15T10:30:00Z",
    "details": {
        "redis_connected": true,
        "queue_info": {
            "queue_name": "arq:queue",
            "queued_jobs_count": 5
        }
    }
}
```

### Логи Воркера

```bash
# Логи воркера показывают:
# - Добавление задач в очередь
# - Начало/завершение выполнения
# - Ошибки и повторные попытки
# - Статистику производительности
```

### Отладка

```bash
# Запуск воркера в verbose режиме
arq src.arq_tasks.worker.worker_settings --verbose

# Использование --watch для авто-перезапуска при изменениях
arq src.arq_tasks.worker.worker_settings --watch /app/src
```

## Производительность

### Оптимизация

1. **Настройка количества воркеров**: Увеличьте `ARQ_MAX_JOBS` для CPU-bound задач
2. **Burst режим**: Используйте для быстрой обработки очередей
3. **Redis кластер**: Для высокой доступности и производительности
4. **Мониторинг**: Отслеживайте очередь и производительность

### Рекомендации

- **Маленькие задачи**: Группируйте в батчи для снижения overhead
- **Большие задачи**: Разбивайте на подзадачи
- **Повторные попытки**: Настраивайте для сетевых операций
- **Мониторинг**: Внедряйте алерты на ошибки

## Безопасность

### Лучшие Практики

1. **Валидация входных данных**: Все параметры задач проверяются
2. **Ограничение ресурсов**: Таймауты и лимиты предотвращают злоупотребления
3. **Логирование**: Все действия логируются для аудита
4. **Rate limiting**: Защита от перегрузки через API

### Безопасные Функции

- ✅ Параметры задач валидируются через Pydantic
- ✅ Таймауты предотвращают зависание
- ✅ Redis подключение защищено
- ✅ Логи не содержат чувствительные данные

## Разработка и Тестирование

### Добавление Новой Задачи

1. **Создайте функцию в `service.py`**:

```python
async def my_new_task(ctx, param1: str, param2: int) -> dict:
    """Моя новая задача"""
    # Логика задачи
    return {"result": "success"}
```

2. **Добавьте в `ALL_TASKS`**:

```python
ALL_TASKS = [
    # ... существующие задачи
    my_new_task,
]
```

3. **Создайте API эндпоинт в `router.py`**:

```python
@router.post("/my-task")
async def run_my_task(param1: str, param2: int):
    job_id = await arq_service.enqueue_job(
        "my_new_task",
        param1=param1,
        param2=param2
    )
    return {"job_id": job_id}
```

### Тестирование

```bash
# Запуск воркера для разработки
arq src.arq_tasks.worker.worker_settings --watch /app/src

# Тестирование через API
curl -X POST "http://localhost:8000/api/v1/arq/enqueue" \
  -H "Content-Type: application/json" \
  -d '{"function_name": "my_new_task", "args": ["test", 123]}'
```

## Troubleshooting

### Распространенные Проблемы

1. **Воркер не запускается**

   - Проверьте Redis подключение
   - Проверьте PYTHONPATH
   - Проверьте импорты функций

2. **Задачи не выполняются**

   - Проверьте очередь в Redis: `redis-cli LLEN arq:queue`
   - Проверьте логи воркера
   - Проверьте функцию на ошибки

3. **Redis соединение теряется**
   - Проверьте настройки Redis
   - Используйте Redis Sentinel для HA
   - Настройте переподключение

### Диагностика

```bash
# Проверить очередь
redis-cli LLEN arq:queue

# Проверить активные задачи
redis-cli KEYS "arq:*"

# Посмотреть логи
docker logs arq_worker
```

## Контрибьютинг

При добавлении новых задач:

1. Следуйте паттернам существующих задач
2. Добавляйте документацию и примеры
3. Тестируйте с различными параметрами
4. Обновляйте эту документацию

---

📚 **Документация**: Используйте context7 для получения дополнительной информации об ARQ
🐛 **Баги**: Создавайте issues в репозитории проекта
💡 **Идеи**: Предлагайте улучшения через PR
