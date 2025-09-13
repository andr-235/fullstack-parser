# VK Parser Backend

FastAPI приложение для парсинга и анализа данных из VK API.

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d
```

### Локальная разработка

```bash
# Установка зависимостей
poetry install

# Запуск приложения
poetry run uvicorn src.main:app --reload

# Запуск тестов
poetry run pytest

# Запуск миграций
poetry run alembic upgrade head
```

## 📁 Структура проекта

```
backend/
├── src/                    # Исходный код
│   ├── auth/              # Модуль аутентификации
│   ├── vk_api/            # VK API интеграция
│   └── shared/            # Общие компоненты
├── tests/                 # Тесты
├── alembic/              # Миграции БД
├── docs/                 # Документация
└── scripts/              # Утилиты
```

## 🔧 Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **Celery** - фоновые задачи
- **Pydantic v2** - валидация данных

## 📚 Документация

- [Аутентификация](docs/AUTH_REFACTOR_README.md)
- [Docker](docs/README.docker.md)
- [Alembic](docs/README.alembic.md)

## 🧪 Тестирование

```bash
# Unit тесты
poetry run pytest tests/unit/

# Integration тесты
poetry run pytest tests/integration/

# Все тесты с покрытием
poetry run pytest --cov=src
```
