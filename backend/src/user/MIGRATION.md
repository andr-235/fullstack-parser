# Миграция User модуля из Auth

## Что было сделано

### 1. Создан отдельный user модуль
- Полная структура Clean Architecture
- Все user-связанные компоненты перенесены из auth модуля

### 2. Перенесенные компоненты

#### Domain Layer
- `User` entity
- Value Objects: `Email`, `UserId`, `Password`, `UserStatus`
- `UserRepositoryInterface`, `PasswordServiceInterface`
- Domain exceptions

#### Application Layer
- `UserService`
- User use cases: `CreateUserUseCase`, `GetUserUseCase`, `UpdateUserUseCase`, `GetUsersListUseCase`, `GetUserStatsUseCase`
- User DTOs

#### Infrastructure Layer
- `SQLAlchemyUserRepository`, `CachedUserRepository`
- `UserContainer` для DI
- Factory для настройки инфраструктуры

#### Presentation Layer
- `user_router` с эндпоинтами
- User schemas и dependencies

### 3. Обновлен auth модуль
- Удалены user-связанные компоненты
- Оставлена только аутентификация и авторизация
- Обновлены импорты и экспорты

### 4. Обновлен main.py
- Подключен user модуль
- Настроена инициализация user инфраструктуры
- Обновлена документация

## Структура после миграции

```
src/
├── auth/           # Только аутентификация и авторизация
│   ├── domain/     # Auth-specific entities и value objects
│   ├── application/# Auth services и use cases
│   ├── infrastructure/# Auth repositories и DI
│   └── presentation/# Auth router и schemas
├── user/           # Управление пользователями
│   ├── domain/     # User entities и value objects
│   ├── application/# User services и use cases
│   ├── infrastructure/# User repositories и DI
│   └── presentation/# User router и schemas
└── shared/         # Общие компоненты
```

## Преимущества разделения

1. **Четкое разделение ответственности**
   - Auth: аутентификация, авторизация, токены
   - User: управление пользователями, профили, статистика

2. **Независимое развитие**
   - Модули можно развивать независимо
   - Разные команды могут работать с разными модулями

3. **Лучшая тестируемость**
   - Изолированное тестирование каждого модуля
   - Моки только нужных зависимостей

4. **Масштабируемость**
   - Возможность вынести модули в отдельные сервисы
   - Независимое масштабирование

## Использование

### Импорт user модуля
```python
from user import user_router, get_user_service
```

### Импорт auth модуля
```python
from auth import auth_router, get_current_user
```

### Настройка в main.py
```python
# Auth модуль
auth_container = setup_auth_infrastructure(...)

# User модуль (использует password_service из auth)
user_container = setup_user_infrastructure(
    session=async_session(),
    password_service=auth_container.get_password_service(),
    cache=auth_container.get_cache(),
    use_cache=True
)
```

## API Endpoints

- **Auth**: `/api/v1/auth/*` - аутентификация
- **Users**: `/api/v1/users/*` - управление пользователями

## Следующие шаги

1. Обновить тесты для работы с новой структурой
2. Обновить документацию API
3. Рассмотреть возможность дальнейшего разделения модулей
4. Добавить интеграционные тесты между модулями
