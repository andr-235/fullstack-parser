# Модуль авторов VK

Современный модуль для работы с авторами VK с архитектурой Clean Architecture и best practices 2025.

## 🏗️ Архитектура

Модуль построен по принципу **Clean Architecture** с разделением на слои:

```
authors/
├── domain/              # Доменный слой
│   ├── entities.py      # Бизнес-сущности
│   ├── exceptions.py    # Доменные исключения
│   └── interfaces.py    # Интерфейсы репозиториев
├── application/         # Слой приложения
│   ├── use_cases.py     # Use cases (бизнес-логика)
│   └── services.py      # Сервисы приложения
├── infrastructure/      # Инфраструктурный слой
│   ├── repositories.py  # Репозитории (SQLAlchemy)
│   ├── cache.py         # Кэш (Redis)
│   └── task_queue.py    # Очереди задач (Celery)
├── presentation/        # Слой представления
│   └── routers.py       # FastAPI роутеры
├── schemas.py           # Pydantic схемы
├── dependencies.py      # FastAPI зависимости
└── celery_tasks.py      # Celery задачи
```

## 🚀 Возможности

### ✅ Основной функционал
- **CRUD операции** с авторами VK
- **Upsert операции** (создание или обновление)
- **Get or Create** для автоматического создания
- **Поиск авторов** по имени и screen_name
- **Массовые операции** для обработки множества авторов
- **Связь с комментариями** (один ко многим)
- **Статистика комментариев** для каждого автора
- **Топ авторов** по количеству комментариев

### ✅ Производительность
- **Кэширование** с Redis (TTL 1 час)
- **Асинхронные операции** с SQLAlchemy 2.0
- **Фоновые задачи** с Celery
- **Пагинация** для больших списков

### ✅ Надежность
- **Валидация данных** с Pydantic v2
- **Обработка ошибок** с типизированными исключениями
- **Логирование** всех операций
- **Транзакции** для целостности данных

## 📋 API Эндпоинты

### Создание автора
```http
POST /authors/
Content-Type: application/json

{
  "vk_id": 123456789,
  "first_name": "Иван",
  "last_name": "Иванов",
  "screen_name": "ivan_ivanov",
  "photo_url": "https://example.com/photo.jpg"
}
```

### Получение автора
```http
GET /authors/{vk_id}
```

### Обновление автора
```http
PUT /authors/{vk_id}
Content-Type: application/json

{
  "first_name": "Петр",
  "last_name": "Петров"
}
```

### Удаление автора
```http
DELETE /authors/{vk_id}
```

### Список авторов
```http
GET /authors/?limit=100&offset=0
```

### Upsert автора
```http
POST /authors/upsert
Content-Type: application/json

{
  "vk_id": 123456789,
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

### Get or Create автора
```http
POST /authors/get-or-create
Content-Type: application/json

{
  "vk_id": 123456789,
  "author_name": "Иван",
  "author_screen_name": "ivan_ivanov"
}
```

### Поиск авторов
```http
GET /authors/search?q=Иван&limit=50
```

### Массовое создание
```http
POST /authors/bulk
Content-Type: application/json

[
  {
    "vk_id": 123456789,
    "first_name": "Иван",
    "last_name": "Иванов"
  },
  {
    "vk_id": 987654321,
    "first_name": "Петр",
    "last_name": "Петров"
  }
]
```

### Количество комментариев автора
```http
GET /authors/{vk_id}/comments-count
```

### Топ авторов по комментариям
```http
GET /authors/top-by-comments?limit=10&min_comments=5
```

### Авторы со статистикой комментариев
```http
GET /authors/with-comments-stats?limit=100&offset=0&min_comments=10
```

## 🔧 Использование

### В коде приложения

```python
from authors import AuthorService, get_author_service_dependency
from fastapi import Depends

# В FastAPI роутере
@app.get("/my-endpoint")
async def my_endpoint(
    service: AuthorService = Depends(get_author_service_dependency)
):
    # Создание автора
    author = await service.create_author({
        "vk_id": 123456789,
        "first_name": "Иван",
        "last_name": "Иванов"
    })
    
    # Получение автора
    author = await service.get_author(123456789)
    
    # Поиск авторов
    authors = await service.search_authors("Иван")
    
    return {"author": author.to_dict() if author else None}
```

### Прямое использование сервиса

```python
from authors import AuthorService, AuthorRepository
from sqlalchemy.ext.asyncio import AsyncSession

# Создание сервиса
async def create_service(db: AsyncSession):
    repository = AuthorRepository(db)
    service = AuthorService(repository)
    return service

# Использование
async def main():
    service = await create_service(db)
    
    # Создание автора
    author = await service.create_author({
        "vk_id": 123456789,
        "first_name": "Иван"
    })
    
    print(f"Создан автор: {author.display_name}")
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты модуля
pytest src/authors/tests/

# Конкретный файл тестов
pytest src/authors/tests/test_domain.py

# С покрытием кода
pytest src/authors/tests/ --cov=authors --cov-report=html
```

### Структура тестов

- `test_domain.py` - тесты доменного слоя (сущности, исключения)
- `test_application.py` - тесты application слоя (use cases, сервисы)
- `test_infrastructure.py` - тесты инфраструктурного слоя (репозитории, кэш)
- `test_presentation.py` - тесты presentation слоя (роутеры, API)

## 🔄 Celery задачи

### Доступные задачи

- `authors.notify_author_created` - уведомление о создании автора
- `authors.notify_author_updated` - уведомление об обновлении автора
- `authors.update_author_photo` - обновление фото автора из VK API
- `authors.sync_author_data` - синхронизация данных с VK API
- `authors.bulk_author_processing` - массовая обработка авторов
- `authors.cleanup_old_authors` - очистка старых авторов

### Запуск воркера

```bash
celery -A src.celery_app worker -l info -Q authors_notifications,authors_photo_updates,authors_data_sync
```

## 📊 Мониторинг

### Логирование

Все операции логируются с уровнем INFO/ERROR:

```python
import logging
logger = logging.getLogger("authors")

# В коде автоматически логируются:
# - Создание авторов
# - Обновление авторов
# - Ошибки операций
# - Celery задачи
```

### Метрики

Рекомендуется добавить метрики для:
- Количество созданных авторов
- Время выполнения операций
- Ошибки валидации
- Использование кэша

## 🛠️ Конфигурация

### Переменные окружения

```env
# Redis для кэша
REDIS_CACHE_URL=redis://localhost:6379/0

# Redis для Celery
REDIS_CELERY_URL=redis://localhost:6379/1

# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Логирование
LOG_LEVEL=INFO
```

### Настройка кэша

```python
# TTL для кэша авторов (по умолчанию 1 час)
AUTHOR_CACHE_TTL=3600

# Паттерн ключей кэша
AUTHOR_CACHE_KEY_PATTERN="author:vk_id:{vk_id}"
```

## 🔒 Безопасность

### Валидация данных

- Все входные данные валидируются через Pydantic схемы
- VK ID проверяется на положительность
- URL фото проверяется на корректность
- Длина строк ограничена разумными пределами

### Обработка ошибок

- Типизированные исключения для разных типов ошибок
- HTTP статус коды соответствуют семантике REST API
- Детальные сообщения об ошибках для разработчиков
- Логирование всех ошибок для мониторинга

## 📈 Производительность

### Оптимизации

- **Кэширование**: Авторы кэшируются в Redis на 1 час
- **Асинхронность**: Все операции асинхронные
- **Пагинация**: Ограничение размера выборок
- **Индексы**: Индексы на vk_id и другие поля

### Рекомендации

- Используйте кэш для часто запрашиваемых авторов
- Применяйте пагинацию для больших списков
- Настройте мониторинг производительности
- Регулярно очищайте старые данные

## 🚀 Развертывание

### Docker

```dockerfile
# В Dockerfile уже включены зависимости
RUN pip install -r requirements.txt
```

### Миграции

```bash
# Создание миграции
alembic revision --autogenerate -m "Add authors table"

# Применение миграций
alembic upgrade head
```

### Health checks

```http
GET /health/authors
```

Проверяет:
- Подключение к базе данных
- Доступность Redis
- Работоспособность Celery

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
