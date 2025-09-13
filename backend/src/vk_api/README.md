# VK API Module - Clean Architecture Implementation

## 🎯 Обзор

Модуль VK API предоставляет высокоуровневый интерфейс для работы с VK API с применением принципов Clean Architecture. Модуль полностью рефакторен в соответствии с best practices 2025 года.

## 🏗️ Архитектура

### Domain Layer (Доменный слой)
- **Entities**: `VKGroup`, `VKPost`, `VKComment` - основные сущности
- **Value Objects**: `VKGroupID`, `VKPostID`, `VKUserID` - объекты-значения
- **Repositories**: `VKAPIRepositoryInterface` - интерфейсы репозиториев
- **Services**: `VKAPIDomainService` - доменные сервисы

### Application Layer (Слой приложения)
- **Use Cases**: Сценарии использования для работы с VK API
- **DTO**: Data Transfer Objects для API
- **Interfaces**: Интерфейсы сервисов
- **Services**: Реализации сервисов

### Infrastructure Layer (Инфраструктурный слой)
- **Repositories**: Реализации репозиториев с кешированием
- **Clients**: HTTP клиенты для VK API
- **Adapters**: Адаптеры внешних сервисов

### Presentation Layer (Слой представления)
- **API Routers**: REST API эндпоинты
- **Schemas**: Pydantic схемы для валидации
- **Dependencies**: FastAPI зависимости

## 🚀 Быстрый старт

### 1. Использование через FastAPI зависимости (рекомендуемый способ)

```python
from fastapi import Depends
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep

async def my_endpoint(vk_service: VKAPIServiceInterface = VKAPIServiceDep):
    # Получить группу
    group = await vk_service.get_group(12345)
    
    # Поиск групп
    groups = await vk_service.search_groups(
        VKSearchGroupsRequestDTO(query="python", count=10)
    )
    
    # Получить посты группы
    posts = await vk_service.get_group_posts(
        VKGetGroupPostsRequestDTO(group_id=12345, count=50)
    )
    
    return {"group": group, "groups": groups, "posts": posts}
```

### 2. Подключение роутеров

```python
from fastapi import FastAPI
from vk_api.presentation.api.vk_api_router import router as vk_api_router

app = FastAPI()
app.include_router(vk_api_router)
```

### 3. Прямое создание сервиса

```python
from vk_api.infrastructure.clients.vk_api_client_impl import VKAPIClientImpl
from vk_api.infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl
from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl

# Создание клиента
vk_client = VKAPIClientImpl()

# Создание репозитория
repository = VKAPIRepositoryImpl(vk_client, cache)

# Создание сервиса
service = VKAPIServiceImpl(repository)
```

## 📚 API Эндпоинты

### Группы
- `GET /vk-api/groups/{group_id}` - Получить группу по ID
- `GET /vk-api/groups/search` - Поиск групп
- `POST /vk-api/groups/batch` - Получить группы по списку ID
- `GET /vk-api/groups/{group_id}/analytics` - Аналитика группы

### Посты
- `GET /vk-api/posts/groups/{group_id}` - Посты группы
- `GET /vk-api/posts/groups/{group_id}/posts/{post_id}` - Пост по ID
- `POST /vk-api/posts/groups/{group_id}/batch` - Посты по списку ID
- `GET /vk-api/posts/groups/{group_id}/posts/{post_id}/with-comments` - Пост с комментариями

### Комментарии
- `GET /vk-api/comments/groups/{group_id}/posts/{post_id}` - Комментарии к посту
- `GET /vk-api/comments/groups/{group_id}/posts/{post_id}/comments/{comment_id}` - Комментарий по ID

### Пользователи
- `GET /vk-api/users/{user_id}` - Пользователь по ID
- `POST /vk-api/users/batch` - Пользователи по списку ID

## 🔧 Конфигурация

### Переменные окружения

```bash
# VK API настройки
VK_API_ACCESS_TOKEN=your_access_token
VK_API_VERSION=5.131
VK_API_BASE_URL=https://api.vk.com/method
VK_API_TIMEOUT=30.0
VK_API_MAX_REQUESTS_PER_SECOND=2

# Кеширование
VK_API_CACHE_TTL=300  # 5 минут
```

### Настройка кеширования

```python
from vk_api.infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl

repository = VKAPIRepositoryImpl(
    vk_client=vk_client,
    cache=redis_cache,
    cache_ttl=600  # 10 минут
)
```

## 🧪 Тестирование

### Unit тесты

```python
import pytest
from unittest.mock import Mock
from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl

@pytest.fixture
def mock_repository():
    return Mock(spec=VKAPIRepositoryInterface)

@pytest.fixture
def vk_service(mock_repository):
    return VKAPIServiceImpl(mock_repository)

async def test_get_group(vk_service, mock_repository):
    # Arrange
    mock_repository.get_group_by_id.return_value = VKGroup(...)
    
    # Act
    result = await vk_service.get_group(12345)
    
    # Assert
    assert result is not None
    mock_repository.get_group_by_id.assert_called_once()
```

### Integration тесты

```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_get_group_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/vk-api/groups/12345")
        assert response.status_code == 200
        assert "id" in response.json()
```

## 🔄 Миграция с старой версии

### До (старая версия)
```python
from vk_api import create_vk_api_service

# Создание сервиса
vk_service = create_vk_api_service()

# Использование
posts = await vk_service.get_group_posts(12345)
```

### После (новая версия)
```python
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep

# Использование через DI
async def my_endpoint(vk_service: VKAPIServiceInterface = VKAPIServiceDep):
    posts = await vk_service.get_group_posts(
        VKGetGroupPostsRequestDTO(group_id=12345, count=100)
    )
```

## 🚨 Breaking Changes

1. **Изменена структура модуля** - теперь используется Clean Architecture
2. **Новые DTO** - все методы теперь принимают DTO вместо простых параметров
3. **Dependency Injection** - рекомендуется использовать FastAPI зависимости
4. **Новые интерфейсы** - все сервисы теперь имеют интерфейсы
5. **Улучшенная обработка ошибок** - используется централизованная система исключений

## 📈 Производительность

- **Кеширование**: Автоматическое кеширование всех запросов
- **Rate Limiting**: Встроенное ограничение частоты запросов
- **Async/await**: Полностью асинхронная архитектура
- **Connection Pooling**: Переиспользование HTTP соединений

## 🔒 Безопасность

- **Валидация входных данных**: Pydantic схемы для всех DTO
- **Обработка ошибок**: Централизованная система исключений
- **Логирование**: Структурированное логирование всех операций
- **Rate Limiting**: Защита от злоупотреблений API

## 📝 Логирование

```python
import logging

logger = logging.getLogger(__name__)

# Логирование автоматически включено для всех операций
# Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Вклад в разработку

1. Следуйте принципам Clean Architecture
2. Покрывайте код тестами (минимум 85%)
3. Используйте type hints везде
4. Документируйте все публичные методы
5. Следуйте PEP 8

## 📄 Лицензия

MIT License

## 👥 Авторы

- AI Assistant
- Development Team

## 🔗 Ссылки

- [VK API Documentation](https://dev.vk.com/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)