# VK API Module - Simplified Implementation

## 🎯 Обзор

Простой и эффективный модуль для работы с VK API. Убрана избыточная сложность Clean Architecture, оставлена только необходимая функциональность.

## 🚀 Быстрый старт

### 1. Базовое использование

```python
from vk_api import VKAPIService, VKSearchGroupsRequest, VKGetGroupPostsRequest

# Создание сервиса
vk_service = VKAPIService(access_token="your_token")

# Получить группу
group = await vk_service.get_group(12345)

# Поиск групп
groups = await vk_service.search_groups(
    VKSearchGroupsRequest(query="python", count=10)
)

# Получить посты группы
posts = await vk_service.get_group_posts(
    VKGetGroupPostsRequest(group_id=12345, count=50)
)
```

### 2. Использование с FastAPI

```python
from fastapi import FastAPI
from vk_api.router import router as vk_api_router

app = FastAPI()
app.include_router(vk_api_router)
```

### 3. Использование через зависимости

```python
from fastapi import Depends
from vk_api.service import VKAPIService

def get_vk_service() -> VKAPIService:
    return VKAPIService()

async def my_endpoint(vk_service: VKAPIService = Depends(get_vk_service)):
    group = await vk_service.get_group(12345)
    return group
```

## 📚 API Эндпоинты

- `GET /vk-api/groups/{group_id}` - Получить группу по ID
- `POST /vk-api/groups/search` - Поиск групп
- `POST /vk-api/groups/{group_id}/posts` - Посты группы
- `POST /vk-api/groups/{group_id}/posts/{post_id}/comments` - Комментарии к посту
- `GET /vk-api/users/{user_id}` - Пользователь по ID
- `GET /vk-api/stats` - Статистика сервиса
- `POST /vk-api/cache/clear` - Очистить кеш

## 🔧 Конфигурация

### Переменные окружения

```bash
VK_API_ACCESS_TOKEN=your_access_token
VK_API_VERSION=5.131
VK_API_BASE_URL=https://api.vk.com/method
VK_API_TIMEOUT=30.0
VK_API_MAX_REQUESTS_PER_SECOND=2.0
VK_API_CACHE_TTL=300
```

### Программная конфигурация

```python
from vk_api import VKAPIService

vk_service = VKAPIService(
    access_token="your_token",
    cache={},  # Словарь для кеширования
    cache_ttl=600  # TTL в секундах
)
```

## 🧪 Тестирование

```python
import pytest
from unittest.mock import Mock
from vk_api import VKAPIService

@pytest.fixture
def vk_service():
    return VKAPIService()

async def test_get_group(vk_service):
    # Мокаем клиент
    vk_service.client = Mock()
    vk_service.client.get_group.return_value = {"id": 12345, "name": "Test Group"}
    
    group = await vk_service.get_group(12345)
    assert group is not None
    assert group.id == 12345
```

## 📈 Производительность

- **Кеширование**: Автоматическое кеширование всех запросов
- **Rate Limiting**: Встроенное ограничение частоты запросов (2 запроса/сек)
- **Async/await**: Полностью асинхронная архитектура
- **Connection Pooling**: Переиспользование HTTP соединений

## 🔒 Безопасность

- **Валидация входных данных**: Pydantic схемы для всех запросов
- **Обработка ошибок**: Централизованная система исключений
- **Rate Limiting**: Защита от злоупотреблений API

## 📝 Логирование

```python
import logging

# Логирование автоматически включено
logger = logging.getLogger("vk_api")
```

## 🤝 Вклад в разработку

1. Следуйте принципу KISS (Keep It Simple, Stupid)
2. Покрывайте код тестами
3. Используйте type hints
4. Документируйте публичные методы

## 📄 Лицензия

MIT License