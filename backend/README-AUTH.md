# Модуль Auth - Полная интеграция в VK Comments Parser API

## ✅ **Статус: ГОТОВ К ИСПОЛЬЗОВАНИЮ**

Модуль аутентификации полностью интегрирован в основное приложение VK Comments Parser API.

## 🏗️ **Архитектура**

### **Clean Architecture + DDD:**
```
auth/
├── domain/              # 🏛️ Бизнес-логика
│   ├── entities/        # User entity
│   ├── value_objects/   # Email, Password, UserId, UserStatus
│   ├── interfaces/      # Repository, Service interfaces
│   └── exceptions.py    # Domain exceptions
├── application/         # 🎯 Use Cases
│   ├── dtos/           # Data Transfer Objects
│   ├── services/       # Business services
│   └── use_cases/      # Use cases
├── infrastructure/      # 🔧 Реализации
│   ├── repositories/   # SQLAlchemy + Cached repos
│   ├── services/       # Password + JWT services
│   ├── adapters/       # Cache adapters
│   └── di/            # DI container
└── presentation/        # 🌐 API слой
    ├── schemas/        # Pydantic schemas
    ├── dependencies/   # FastAPI dependencies
    └── routers/        # API endpoints
```

## 🚀 **Быстрый старт**

### **1. Установка зависимостей:**
```bash
cd backend
poetry install
```

### **2. Настройка окружения:**
```bash
# .env файл
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vk_parser
REDIS_CACHE_URL=redis://localhost:6379/0
```

### **3. Запуск приложения:**
```bash
poetry run uvicorn src.main:app --reload
```

### **4. Доступ к API:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📋 **API Endpoints**

### **Аутентификация** (`/api/v1/auth`):
```bash
# Вход в систему
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Обновление токена
POST /api/v1/auth/refresh
{
  "refresh_token": "refresh_token_here"
}

# Смена пароля
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
{
  "current_password": "old_password",
  "new_password": "new_password123"
}

# Сброс пароля
POST /api/v1/auth/reset-password
{
  "email": "user@example.com"
}

# Выход из системы
POST /api/v1/auth/logout
{
  "refresh_token": "refresh_token_here"
}
```

### **Пользователи** (`/api/v1/users`):
```bash
# Создание пользователя
POST /api/v1/users/
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User",
  "is_superuser": false
}

# Текущий пользователь
GET /api/v1/users/me
Authorization: Bearer <access_token>

# Обновление профиля
PUT /api/v1/users/me
Authorization: Bearer <access_token>
{
  "full_name": "Updated Name",
  "email": "updated@example.com"
}

# Список пользователей (суперпользователи)
GET /api/v1/users/?limit=50&offset=0
Authorization: Bearer <access_token>

# Статистика пользователей (суперпользователи)
GET /api/v1/users/stats
Authorization: Bearer <access_token>

# Пользователь по ID (суперпользователи)
GET /api/v1/users/1
Authorization: Bearer <access_token>
```

## 🔧 **Использование в других модулях**

### **Защита эндпоинтов:**
```python
from fastapi import Depends
from auth import get_current_active_user

@router.get("/protected")
async def protected_endpoint(
    current_user = Depends(get_current_active_user)
):
    return {"user_id": current_user.id.value}
```

### **Опциональная аутентификация:**
```python
from auth import get_current_user

@router.get("/optional")
async def optional_auth(
    current_user = Depends(get_current_user)
):
    if current_user:
        return {"authenticated": True}
    return {"authenticated": False}
```

### **Права суперпользователя:**
```python
from auth import get_current_superuser

@router.get("/admin")
async def admin_only(
    current_user = Depends(get_current_superuser)
):
    return {"admin": True}
```

## 🧪 **Тестирование**

### **Запуск тестов:**
```bash
# Все тесты auth модуля
poetry run pytest tests/ -k "auth" -v

# Unit тесты
poetry run pytest tests/unit/test_auth_domain.py -v
poetry run pytest tests/unit/test_auth_application.py -v

# Integration тесты
poetry run pytest tests/integration/test_auth_integration.py -v

# С покрытием
poetry run pytest tests/ -k "auth" --cov=src/auth --cov-report=html
```

### **Тестовые данные:**
```python
# В conftest.py настроены фикстуры:
@pytest.fixture
def test_user_data():
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_superuser": False
    }

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
```

## ⚙️ **Конфигурация**

### **pyproject.toml:**
```toml
[tool.poetry.dependencies]
# JWT
python-jose = {extras = ["cryptography"], version = ">=3.5.0"}

# Пароли
passlib = ">=1.7.4"
password-validator = "^1.0"

# Email
email-validator = ">=2.3.0"
pydantic-extra-types = {extras = ["email"], version = "^2.10.5"}

# Redis
redis = ">=5.0.0"
```

### **Переменные окружения:**
```bash
# JWT
SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# База данных
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Redis
REDIS_CACHE_URL=redis://localhost:6379/0
```

## 🔒 **Безопасность**

### **Пароли:**
- ✅ Bcrypt с настраиваемыми раундами
- ✅ Валидация сложности паролей
- ✅ Никогда не возвращаются в API

### **JWT токены:**
- ✅ Access токены (30 мин)
- ✅ Refresh токены (7 дней)
- ✅ Валидация подписи и времени

### **Защита от атак:**
- ✅ Блокировка после 5 попыток
- ✅ Rate limiting
- ✅ CORS настройки
- ✅ Валидация входных данных

## 📊 **Мониторинг**

### **Логирование:**
- ✅ Структурированные JSON логи
- ✅ Correlation ID для трассировки
- ✅ Уровни: DEBUG, INFO, WARNING, ERROR

### **Метрики:**
- ✅ Время выполнения операций
- ✅ Количество входов/выходов
- ✅ Использование кэша
- ✅ Статистика пользователей

## 🚀 **Деплой**

### **Docker:**
```dockerfile
FROM python:3.11-slim

# Установка Poetry
RUN pip install poetry

# Копирование зависимостей
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Копирование кода
COPY . .

# Запуск
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose:**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser
      - REDIS_CACHE_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: vk_parser
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
  
  redis:
    image: redis:7-alpine
```

## 📚 **Документация**

- [Архитектура модуля](src/auth/README.md)
- [Интеграция в приложение](src/auth/INTEGRATION.md)
- [Infrastructure слой](src/auth/infrastructure/README.md)
- [API схемы](src/auth/presentation/schemas/README.md)
- [DI контейнер](src/auth/infrastructure/di/README.md)

## 🎉 **Готово к использованию!**

Модуль Auth полностью интегрирован в VK Comments Parser API:
- ✅ **Clean Architecture** - соблюдение принципов DDD
- ✅ **Dependency Injection** - централизованное управление
- ✅ **Type Safety** - полная типизация
- ✅ **Тестирование** - unit, integration, e2e тесты
- ✅ **Безопасность** - современные практики
- ✅ **Производительность** - асинхронность, кэширование
- ✅ **Мониторинг** - логи, метрики, трейсы
- ✅ **Документация** - подробные README

**Используйте модуль Auth для защиты эндпоинтов в других модулях!**
