# VK API Module - Только внутренние вызовы

Этот модуль предоставляет высокоуровневый интерфейс для работы с VK API **только для внутренних вызовов**. HTTP API эндпоинты удалены.

## 🚀 Быстрый старт

```python
from src.vk_api.dependencies import create_vk_api_service

# Создаем экземпляр
vk_service = create_vk_api_service()

# Используем
posts = await vk_service.get_group_posts(group_id=12345, count=10)
comments = await vk_service.get_post_comments(group_id=12345, post_id=67890)
```

## 📋 Основные возможности

- ✅ Получение постов групп с пагинацией
- ✅ Получение комментариев к постам
- ✅ Получение информации о группах и пользователях
- ✅ Поиск групп по запросам
- ✅ Кеширование результатов
- ✅ Rate limiting для защиты от перегрузки
- ✅ Circuit breaker для отказоустойчивости
- ✅ Автоматическое логирование

## 🔧 Интеграция в другие модули

### Способ 1: Простое использование

```python
from src.vk_api.dependencies import create_vk_api_service

class MyService:
    def __init__(self):
        self.vk_api = create_vk_api_service()

    async def get_group_data(self, group_id: int):
        # Получаем информацию о группе
        group_info = await self.vk_api.get_group_info(group_id)

        # Получаем посты
        posts = await self.vk_api.get_group_posts(group_id, count=20)

        return {
            'group': group_info,
            'posts': posts
        }
```

### Способ 2: Внедрение зависимостей

```python
from src.vk_api.service import VKAPIService

class AnalyticsService:
    def __init__(self, vk_api_service: VKAPIService = None):
        if vk_api_service:
            self.vk_api = vk_api_service
        else:
            from src.vk_api.dependencies import create_vk_api_service
            self.vk_api = create_vk_api_service()
```

### Способ 3: С существующим ParserService

```python
from src.parser.service import ParserService
from src.vk_api.dependencies import create_vk_api_service

# Создаем VK API сервис
vk_service = create_vk_api_service()

# Передаем в парсер
parser = ParserService(vk_api_service=vk_service)

# Парсер будет использовать VK API для получения данных
result = await parser.start_parsing(group_ids=[12345])
```

## 📚 Доступные методы

| Метод                                                       | Описание                            | Параметры                                                                         |
| ----------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------- |
| `get_group_posts(group_id, count, offset)`                  | Получить посты группы               | group_id: int, count: int = 20, offset: int = 0                                   |
| `get_post_comments(group_id, post_id, count, offset, sort)` | Получить комментарии к посту        | group_id: int, post_id: int, count: int = 100, offset: int = 0, sort: str = "asc" |
| `get_group_info(group_id)`                                  | Получить информацию о группе        | group_id: int                                                                     |
| `get_user_info(user_ids)`                                   | Получить информацию о пользователях | user_ids: List[int]                                                               |
| `get_post_by_id(group_id, post_id)`                         | Получить конкретный пост            | group_id: int, post_id: int                                                       |
| `search_groups(query, count, offset, country, city)`        | Поиск групп                         | query: str, count: int = 20, offset: int = 0                                      |
| `get_group_members(group_id, count, offset)`                | Получить участников группы          | group_id: int, count: int = 1000, offset: int = 0                                 |
| `validate_access_token()`                                   | Валидация токена доступа            | -                                                                                 |
| `health_check()`                                            | Проверка здоровья сервиса           | -                                                                                 |

## 🎯 Примеры использования

### Анализ вовлеченности группы

```python
from src.vk_api.dependencies import create_vk_api_service

async def analyze_group(group_id: int):
    vk_api = create_vk_api_service()

    # Получаем последние посты
    posts_result = await vk_api.get_group_posts(group_id, count=50)
    posts = posts_result.get('posts', [])

    # Считаем статистику
    total_likes = sum(p.get('likes', {}).get('count', 0) for p in posts)
    total_comments = sum(p.get('comments', {}).get('count', 0) for p in posts)

    return {
        'posts_count': len(posts),
        'avg_likes': total_likes / max(len(posts), 1),
        'avg_comments': total_comments / max(len(posts), 1)
    }
```

### Мониторинг комментариев

```python
from src.vk_api.dependencies import create_vk_api_service

async def monitor_comments(group_id: int, post_id: int):
    vk_api = create_vk_api_service()

    # Получаем комментарии
    comments_result = await vk_api.get_post_comments(
        group_id=group_id,
        post_id=post_id,
        count=100
    )

    comments = comments_result.get('comments', [])

    # Анализируем активность
    user_activity = {}
    for comment in comments:
        user_id = comment.get('from_id')
        if user_id and user_id > 0:  # Только пользователи
            user_activity[user_id] = user_activity.get(user_id, 0) + 1

    return user_activity
```

## 🔧 Запуск примеров

```bash
cd /opt/app/backend/src/vk_api
python3 usage.py
```

## ⚙️ Конфигурация

Сервис использует настройки из основного конфига приложения:

- `vk_api_config.cache.*` - настройки кеширования
- `vk_api_config.rate_limit.*` - настройки rate limiting
- `vk_api_config.circuit_breaker.*` - настройки circuit breaker

## 🛡️ Защитные механизмы

- **Rate Limiting**: Автоматическое ограничение запросов к VK API
- **Circuit Breaker**: Защита от каскадных сбоев
- **Timeout**: Защита от зависаний
- **Caching**: Кеширование результатов для производительности
- **Retry**: Повторные попытки при временных сбоях
- **Validation**: Валидация входных данных

## 📝 Логирование

Все операции автоматически логируются с использованием Winston-подобного логгера:

```python
# Логи пишутся автоматически при каждом вызове метода
posts = await vk_service.get_group_posts(12345)
# В логах появится запись о вызове wall.get с параметрами
```

## 🚫 Что было удалено

- ❌ HTTP API роутеры (`/api/v1/vk-api/*`)
- ❌ FastAPI зависимости (`Depends`)
- ❌ OpenAPI/Swagger документация эндпоинтов

Теперь модуль предназначен **только для внутреннего использования** в других модулях проекта.
