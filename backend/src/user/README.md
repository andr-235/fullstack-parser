# User Module

Модуль управления пользователями системы.

## Архитектура

Модуль построен по принципу Clean Architecture с разделением на слои:

```
user/
├── domain/              # Бизнес-логика и сущности
│   ├── entities/        # Domain entities
│   ├── value_objects/   # Value objects
│   ├── interfaces/      # Интерфейсы репозиториев
│   └── exceptions.py    # Domain исключения
├── application/         # Use cases и сервисы
│   ├── services/        # Application сервисы
│   ├── use_cases/       # Use cases
│   └── dtos/           # Data Transfer Objects
├── infrastructure/      # Реализации внешних зависимостей
│   ├── repositories/    # Репозитории
│   └── di/             # DI контейнер
└── presentation/        # API слой
    ├── routers/         # FastAPI роутеры
    ├── schemas/         # Pydantic схемы
    └── dependencies/    # FastAPI зависимости
```

## Компоненты

### Domain Layer

- **User** - основная сущность пользователя
- **Value Objects**: Email, UserId, Password, UserStatus
- **Interfaces**: UserRepositoryInterface, PasswordServiceInterface
- **Exceptions**: UserNotFoundError, UserAlreadyExistsError

### Application Layer

- **UserService** - основной сервис для работы с пользователями
- **Use Cases**:
  - CreateUserUseCase - создание пользователя
  - GetUserUseCase - получение пользователя
  - UpdateUserUseCase - обновление пользователя
  - GetUsersListUseCase - получение списка пользователей
  - GetUserStatsUseCase - получение статистики

### Infrastructure Layer

- **SQLAlchemyUserRepository** - реализация репозитория на SQLAlchemy
- **CachedUserRepository** - кэшированная обертка репозитория
- **UserContainer** - DI контейнер для управления зависимостями

### Presentation Layer

- **user_router** - FastAPI роутер с эндпоинтами
- **Schemas** - Pydantic схемы для API
- **Dependencies** - FastAPI зависимости для инъекции

## API Endpoints

- `POST /users/` - создание пользователя
- `GET /users/{user_id}` - получение пользователя по ID
- `GET /users/me` - получение текущего пользователя
- `PUT /users/me` - обновление профиля
- `GET /users/` - список пользователей (с пагинацией)
- `GET /users/stats` - статистика пользователей

## Использование

### Инициализация

```python
from user.infrastructure.factory import setup_user_infrastructure

# Настройка инфраструктуры
user_container = setup_user_infrastructure(
    session=async_session,
    password_service=password_service,
    cache=cache_adapter,
    use_cache=True
)
```

### Использование сервисов

```python
from user import get_user_service, get_create_user_use_case

# Получение сервиса
user_service = get_user_service()

# Использование use case
create_use_case = get_create_user_use_case()
user = await create_use_case.execute(create_request)
```

## Зависимости

- **Auth Module** - для аутентификации и авторизации
- **Shared Module** - для общих компонентов (логирование, БД)
- **SQLAlchemy** - для работы с БД
- **Redis** - для кэширования (опционально)

## Особенности

- Полная изоляция от auth модуля
- Асинхронная архитектура
- Кэширование на уровне репозитория
- Dependency Injection через контейнер
- Валидация через Pydantic v2
- Логирование всех операций
