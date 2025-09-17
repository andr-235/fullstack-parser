# Модуль Аутентификации (Auth Module)

## Обзор

Модуль аутентификации предоставляет комплексную систему управления пользователями, аутентификации и авторизации для FastAPI приложения. Модуль построен с использованием принципов чистой архитектуры, SOLID и лучших практик Python разработки.

## Архитектура

### Слои Архитектуры

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│         (Router, Schemas)           │
├─────────────────────────────────────┤
│         Application Layer           │
│         (Services, Use Cases)       │
├─────────────────────────────────────┤
│         Domain Layer                │
│         (Entities, Interfaces)      │
├─────────────────────────────────────┤
│         Infrastructure Layer        │
│         (Repositories, External)    │
└─────────────────────────────────────┘
```

### Компоненты

#### 1. Presentation Layer (Представление)
- **router.py**: FastAPI роутеры для обработки HTTP запросов
- **schemas.py**: Pydantic схемы для валидации данных
- **dependencies.py**: FastAPI зависимости для инъекции сервисов

#### 2. Application Layer (Приложение)
- **services/service.py**: Основной сервис аутентификации
- **services/jwt_service.py**: Сервис для работы с JWT токенами
- **services/password_service.py**: Сервис для хеширования паролей
- **services/validator_service.py**: Сервис валидации данных

#### 3. Domain Layer (Домен)
- **interfaces/**: Абстрактные интерфейсы для зависимостей
- **entities/**: Доменные сущности и бизнес-правила

#### 4. Infrastructure Layer (Инфраструктура)
- **repositories/**: Репозитории для работы с данными
- **external/**: Внешние сервисы (кеш, email и т.д.)

## Основные Функциональности

### 🔐 Аутентификация
- Регистрация новых пользователей
- Вход в систему с валидацией
- Выход из системы
- Обновление токенов

### 🔑 Управление Паролями
- Смена пароля
- Сброс пароля через email
- Валидация сложности паролей

### 👤 Управление Пользователями
- Получение информации о пользователе
- Валидация токенов
- Управление статусом пользователей

### 🛡️ Безопасность
- Rate limiting для предотвращения brute force
- Кеширование для оптимизации производительности
- Логирование событий безопасности
- Валидация входных данных

## Используемые Паттерны Проектирования

### 1. Dependency Injection (Внедрение Зависимостей)
```python
# Пример использования
auth_service = AuthService(
    user_repository=user_repo,
    password_service=password_svc,
    jwt_service=jwt_svc,
    cache_service=cache_svc
)
```

### 2. Repository Pattern (Паттерн Репозитория)
```python
class UserRepository:
    async def get_by_email(self, email: str) -> Optional[User]:
        # Логика получения пользователя из БД
        pass

    async def create(self, user_data: dict) -> User:
        # Логика создания пользователя
        pass
```

### 3. Strategy Pattern (Паттерн Стратегии)
```python
class PasswordService:
    def __init__(self, strategy: PasswordHashingStrategy):
        self.strategy = strategy

    async def hash_password(self, password: str) -> str:
        return await self.strategy.hash(password)
```

### 4. Factory Pattern (Паттерн Фабрики)
```python
class AuthServiceFactory:
    @staticmethod
    def create_service(config: AuthConfig) -> AuthService:
        # Создание и настройка сервиса
        pass
```

## Конфигурация

### Основные Настройки

```python
class AuthConfig(BaseModel):
    # JWT настройки
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Кеширование
    user_cache_ttl_seconds: int = 3600
    login_attempts_ttl_seconds: int = 900

    # Безопасность
    max_login_attempts: int = 5
    password_min_length: int = 8
    password_rounds: int = 12

    # Rate limiting
    login_rate_limit: str = "5/minute"
```

### Переменные Окружения

```bash
# JWT
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Redis (опционально)
REDIS_URL=redis://redis:6379/0

# Email (опционально)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## API Эндпоинты

### Регистрация
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### Вход в Систему
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Обновление Токена
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
Content-Type: application/json

{
  "refresh_token": "refresh_token_here"
}
```

### Смена Пароля
```http
POST /auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newsecurepassword123"
}
```

### Сброс Пароля
```http
POST /auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Информация о Пользователе
```http
GET /auth/me
Authorization: Bearer <access_token>
```

## Обработка Ошибок

### Стандартные Ошибки

| Код | Описание |
|-----|----------|
| 400 | Bad Request - некорректные данные |
| 401 | Unauthorized - неверные учетные данные |
| 403 | Forbidden - недостаточно прав |
| 404 | Not Found - пользователь не найден |
| 429 | Too Many Requests - превышен лимит запросов |
| 500 | Internal Server Error - внутренняя ошибка сервера |

### Кастомные Исключения

```python
class AuthException(Exception):
    """Базовое исключение модуля Auth"""
    pass

class InvalidCredentialsError(AuthException):
    """Неверные учетные данные"""
    pass

class InvalidTokenError(AuthException):
    """Неверный токен"""
    pass

class TokenExpiredError(AuthException):
    """Токен истек"""
    pass
```

## Тестирование

### Запуск Тестов

```bash
# Unit тесты
pytest backend/tests/unit/auth/ -v

# Интеграционные тесты
pytest backend/tests/integration/auth/ -v

# Все тесты модуля
pytest backend/tests/unit/auth/ backend/tests/integration/auth/ -v
```

### Покрытие Тестами

```bash
# С покрытием
pytest --cov=backend/src/auth --cov-report=html
```

## Мониторинг и Логирование

### Метрики

- Количество успешных/неудачных входов
- Время выполнения операций
- Количество активных пользователей
- Rate limiting события

### Логи

```python
# Структура логов
{
  "timestamp": "2023-12-01T10:00:00Z",
  "level": "INFO",
  "service": "auth",
  "user_id": "123",
  "action": "login",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "correlation_id": "abc-123-def"
}
```

## Производительность

### Оптимизации

1. **Кеширование**: Redis для хранения данных пользователей и токенов
2. **Rate Limiting**: Ограничение количества запросов
3. **Асинхронность**: Все операции асинхронные
4. **Индексы БД**: Оптимизированные запросы к базе данных

### Бенчмарки

- Регистрация: < 200ms
- Вход: < 150ms
- Валидация токена: < 50ms (с кешем)

## Безопасность

### Меры Безопасности

1. **Хеширование паролей**: bcrypt с солью
2. **JWT токены**: Подписанные с истечением
3. **Rate limiting**: Защита от brute force
4. **Валидация**: Строгая проверка входных данных
5. **Логирование**: Отслеживание подозрительной активности

### Рекомендации

- Регулярно менять SECRET_KEY
- Использовать HTTPS в продакшене
- Настраивать firewall правила
- Мониторить логи на подозрительную активность

## Развертывание

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth
        image: your-registry/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: secret-key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

## Разработка

### Добавление Новой Функциональности

1. Создать интерфейс в `domain/interfaces/`
2. Реализовать сервис в `services/`
3. Добавить роутер в `router.py`
4. Написать тесты
5. Обновить документацию

### Code Style

- Следовать PEP 8
- Использовать type hints
- Добавлять docstrings
- Максимальная длина строки: 88 символов

## Поддержка и Контрибьютинг

### Как Сообщить об Ошибке

1. Создать issue в GitHub
2. Описать проблему детально
3. Приложить логи и traceback

### Как Внести Вклад

1. Fork репозиторий
2. Создать feature branch
3. Написать тесты
4. Сделать pull request

## Лицензия

MIT License - см. файл LICENSE для деталей.

## Контакты

- **Email**: dev@company.com
- **Slack**: #auth-module
- **Документация**: [Ссылка на полную документацию]