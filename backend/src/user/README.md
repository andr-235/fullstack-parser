# User Module

Упрощенный модуль управления пользователями.

## Структура

```
user/
├── __init__.py          # Экспорты модуля
├── models.py            # SQLAlchemy модели
├── schemas.py           # Pydantic схемы
├── exceptions.py        # Исключения
├── repository.py        # Репозиторий
├── services.py          # Бизнес-логика
├── dependencies.py      # FastAPI зависимости
├── routers.py           # API эндпоинты
└── README.md           # Документация
```

## Компоненты

### Models
- **User** - SQLAlchemy модель пользователя

### Schemas
- **UserCreateRequest** - создание пользователя
- **UserUpdateRequest** - обновление пользователя
- **UserResponse** - ответ с данными пользователя
- **UserListRequest/Response** - список пользователей
- **UserStatsResponse** - статистика

### Services
- **UserService** - основная бизнес-логика

### API Endpoints
- `POST /users/` - создание пользователя
- `GET /users/{user_id}` - получение пользователя
- `GET /users/me` - текущий пользователь
- `PUT /users/me` - обновление профиля
- `GET /users/` - список пользователей (admin)
- `GET /users/stats` - статистика (admin)
- `DELETE /users/{user_id}` - удаление (admin)

## Использование

```python
from user import user_router, UserService, UserCreateRequest

# Подключение роутера
app.include_router(user_router, prefix="/api/v1")

# Использование сервиса
user_service = UserService(repository, password_service)
user = await user_service.create_user(create_request)
```

## Зависимости

- SQLAlchemy 2.0+ для работы с БД
- Pydantic V2 для валидации
- FastAPI для API
- Auth модуль для паролей и JWT