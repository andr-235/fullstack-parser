# Shared Application Layer

## Обзор

Модуль `shared/application` предоставляет общую инфраструктуру для реализации use cases в Clean Architecture. Включает в себя базовые классы, команды/запросы (CQRS), обработчики событий и сервисы валидации.

## Компоненты

### 1. Base Use Cases (`base_use_case.py`)

#### UseCaseResult
Результат выполнения use case с поддержкой:
- Успешных результатов с данными
- Ошибок с кодами
- Доменных событий

```python
# Успешный результат
result = UseCaseResult.success_result(data={"id": 1}, events=[event])

# Результат с ошибкой
result = UseCaseResult.error_result("Entity not found", "NOT_FOUND")
```

#### BaseCommandUseCase
Базовый класс для команд (запись данных):
- Валидация команды
- Выполнение бизнес-логики
- Обработка ошибок
- Сбор доменных событий

#### BaseQueryUseCase
Базовый класс для запросов (чтение данных):
- Валидация запроса
- Выполнение запроса
- Обработка ошибок

#### Пагинация и фильтрация
- `PaginationParams` - параметры пагинации
- `PaginatedResult` - результат с пагинацией
- `SortParams` - параметры сортировки
- `FilterParams` - базовые фильтры

### 2. Commands (`commands.py`)

Реализация CQRS для команд:

#### Базовые команды
- `CreateCommand` - создание сущности
- `UpdateCommand` - обновление сущности
- `DeleteCommand` - удаление сущности
- `BulkDeleteCommand` - массовое удаление
- `ActivateCommand` / `DeactivateCommand` - активация/деактивация
- `ImportCommand` / `ExportCommand` - импорт/экспорт

#### CommandBus
Диспетчер команд для маршрутизации к обработчикам:

```python
command_bus = CommandBus()
command_bus.register_handler(CreateUserCommand, CreateUserHandler())
result = await command_bus.dispatch(command)
```

### 3. Queries (`queries.py`)

Реализация CQRS для запросов:

#### Базовые запросы
- `GetByIdQuery` - получение по ID
- `GetByIdsQuery` - получение по списку ID
- `ListQuery` - список с пагинацией и фильтрацией
- `SearchQuery` - поиск
- `CountQuery` - подсчет
- `ExistsQuery` - проверка существования
- `AnalyticsQuery` - аналитические запросы

#### QueryBus
Диспетчер запросов:

```python
query_bus = QueryBus()
query_bus.register_handler(GetUserByIdQuery, GetUserByIdHandler())
result = await query_bus.dispatch(query)
```

### 4. Event Handlers (`event_handlers.py`)

Система обработки доменных событий:

#### EventHandler
Базовый класс для обработчиков событий:

```python
@event_handler(UserCreatedEvent, EventHandlerPriority.HIGH)
class UserCreatedHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        # Обработка события
        pass
```

#### EventBus
Диспетчер событий с поддержкой:
- Приоритетов обработчиков
- Синхронных и асинхронных обработчиков
- Middleware
- Batch обработки

#### EventStore
Хранилище событий с автоматической публикацией:

```python
await event_store.append(event)
await event_store.append_batch(events)
```

### 5. Validation Services (`validation_services.py`)

Комплексная система валидации:

#### Валидаторы полей
- `FieldValidator` - базовый валидатор
- `EmailValidator` - валидация email
- `PasswordValidator` - валидация паролей
- `UUIDValidator` - валидация UUID
- `DateValidator` - валидация дат

#### ValidationService
Сервис для сложной валидации:

```python
service = ValidationService()

# Валидация поля
rules = {"required": True, "min_length": 3, "type": "email"}
result = service.validate_field("email", "test@example.com", rules)

# Валидация объекта
schema = {
    "name": {"required": True, "min_length": 2},
    "email": {"required": True, "type": "email"}
}
result = service.validate_object(data, schema)
```

## Использование

### Создание Use Case

```python
class CreateUserCommand:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class CreateUserUseCase(BaseCommandUseCase[CreateUserCommand, User]):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def _validate_command(self, command: CreateUserCommand) -> None:
        # Валидация команды
        if not command.name:
            raise ValidationError("Name is required")
    
    async def _execute_command(self, command: CreateUserCommand) -> User:
        # Создание пользователя
        user = User(name=command.name, email=command.email)
        return await self.user_repository.save(user)
```

### Обработка событий

```python
@event_handler(UserCreatedEvent)
class UserCreatedHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        # Отправка welcome email
        await send_welcome_email(event.user_id)
```

### Валидация данных

```python
validator = EmailValidator("email", required=True)
result = validator.validate("test@example.com")

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Тестирование

Все компоненты покрыты unit-тестами в `tests/unit/shared/application/`:

- `test_base_use_case.py` - тесты базовых use cases
- `test_validation_services.py` - тесты валидации

Запуск тестов:
```bash
pytest tests/unit/shared/application/ -v
```

## Архитектурные принципы

1. **Single Responsibility** - каждый класс имеет одну ответственность
2. **Open/Closed** - открыт для расширения, закрыт для модификации
3. **Dependency Inversion** - зависимости через интерфейсы
4. **Command Query Separation** - разделение команд и запросов
5. **Event-Driven** - обработка через доменные события

## Интеграция

Модуль интегрируется с:
- `shared/domain` - доменные объекты и события
- `shared/infrastructure` - репозитории и внешние сервисы
- `shared/presentation` - API слой

## Расширение

Для добавления новых компонентов:

1. Создайте класс, наследующий от соответствующего базового класса
2. Реализуйте необходимые методы
3. Добавьте тесты
4. Обновите документацию
