# Auth Module

Упрощенный модуль аутентификации для FastAPI приложения.

## Структура

```
auth/
├── __init__.py          # Экспорты модуля
├── schemas.py           # Pydantic схемы для API
├── dependencies.py      # FastAPI зависимости
├── router.py           # API роутеры
├── config.py           # Конфигурация
├── exceptions.py       # Исключения
├── setup.py           # Настройка DI
└── services/          # Сервисы
    ├── __init__.py
    ├── service.py      # Основной сервис аутентификации
    ├── password_service.py # Сервис паролей (bcrypt)
    └── jwt_service.py  # JWT сервис
```

## Использование

### 1. Настройка

```python
from auth.setup import setup_auth
from user.infrastructure.repositories import UserRepository

# Настройка модуля
setup_auth(
    user_repository=UserRepository(),
    redis_url="redis://localhost:6379/0",
    secret_key="your-secret-key",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)
```

### 2. Подключение роутера

```python
from fastapi import FastAPI
from auth.router import router

app = FastAPI()
app.include_router(router)
```

### 3. Использование зависимостей

```python
from fastapi import Depends
from auth.dependencies import get_current_user, get_current_active_user
from user.domain.entities.user import User

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id.value}

@app.get("/admin")
async def admin_route(current_user: User = Depends(get_current_active_user)):
    return {"message": "Admin only"}
```

## API Endpoints

- `POST /auth/login` - Вход в систему
- `POST /auth/refresh` - Обновление токена
- `POST /auth/change-password` - Смена пароля
- `POST /auth/reset-password` - Запрос сброса пароля
- `POST /auth/reset-password/confirm` - Подтверждение сброса пароля
- `POST /auth/logout` - Выход из системы
- `GET /auth/me` - Информация о текущем пользователе

## Особенности

- **Упрощенная архитектура**: Убраны избыточные Use Cases и сложный DI
- **Прямые зависимости**: Используется FastAPI Depends напрямую
- **Единые схемы**: DTO и API схемы объединены
- **Минимум абстракций**: Только необходимые интерфейсы
- **Безопасность**: Защита от timing attacks, rate limiting, кэширование
- **Логирование**: Структурированные логи с correlation ID

## Конфигурация

Все настройки в `config.py`:

```python
class AuthConfig(BaseModel):
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    user_cache_ttl_seconds: int = 3600
    max_login_attempts: int = 5
    password_min_length: int = 8
    # ... другие настройки
```
