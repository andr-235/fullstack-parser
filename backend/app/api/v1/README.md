# API v1 - VK Comments Parser

## Обзор

API v1 предоставляет RESTful интерфейс для работы с VK Comments Parser. Все эндпоинты следуют стандартам REST и возвращают данные в формате JSON.

## Базовый URL

```
/api/v1
```

## Аутентификация

В текущей версии API аутентификация не требуется. Все эндпоинты публично доступны.

## Общие заголовки

```
Content-Type: application/json
Accept: application/json
```

## Стандартные ответы

### Успешный ответ

```json
{
  "success": true,
  "data": {...},
  "message": "Операция выполнена успешно",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Ответ с пагинацией

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Ответ с ошибкой

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Описание ошибки",
    "status_code": 400,
    "details": {
      "field": "field_name"
    }
  }
}
```

## Эндпоинты

### 1. Информация об API

#### GET `/`

Получить информацию об API и доступных эндпоинтах.

**Ответ:**

```json
{
  "service": "VK Comments Parser API",
  "version": "1.0.0",
  "description": "API для парсинга и анализа комментариев VK",
  "endpoints": {...},
  "documentation": {...}
}
```

### 2. Health Checks

#### GET `/health`

Базовая проверка состояния сервиса.

#### GET `/health/detailed`

Детальная проверка состояния с проверкой компонентов (БД, кеш).

#### GET `/health/ready`

Проверка готовности для Kubernetes/контейнерной оркестрации.

#### GET `/health/live`

Проверка жизнеспособности процесса.

### 3. Комментарии

#### GET `/comments`

Получить список комментариев с пагинацией и фильтрацией.

**Параметры запроса:**

- `page` (int, default: 1) - Номер страницы
- `size` (int, default: 20, max: 100) - Размер страницы
- `is_viewed` (bool, optional) - Фильтр по просмотренности
- `keyword_id` (int, optional) - Фильтр по ключевому слову
- `group_id` (int, optional) - Фильтр по группе

**Пример:**

```bash
GET /api/v1/comments?page=1&size=10&is_viewed=false
```

#### GET `/comments/{comment_id}`

Получить комментарий по ID.

**Параметры пути:**

- `comment_id` (int) - ID комментария

### 4. Группы VK

#### GET `/groups`

Получить список групп VK.

#### POST `/groups`

Создать новую группу VK.

#### PUT `/groups/{group_id}`

Обновить группу VK.

#### DELETE `/groups/{group_id}`

Удалить группу VK.

### 5. Ключевые слова

#### GET `/keywords`

Получить список ключевых слов.

#### POST `/keywords`

Создать новое ключевое слово.

#### PUT `/keywords/{keyword_id}`

Обновить ключевое слово.

#### DELETE `/keywords/{keyword_id}`

Удалить ключевое слово.

### 6. Парсер

#### GET `/parser`

Получить статус парсера.

#### POST `/parser/start`

Запустить парсинг.

#### POST `/parser/stop`

Остановить парсинг.

### 7. Статистика

#### GET `/stats`

Получить статистику системы.

#### GET `/stats/comments`

Получить статистику по комментариям.

#### GET `/stats/groups`

Получить статистику по группам.

### 8. Мониторинг

#### GET `/monitoring`

Получить список задач мониторинга.

#### POST `/monitoring`

Создать новую задачу мониторинга.

#### PUT `/monitoring/{task_id}`

Обновить задачу мониторинга.

#### DELETE `/monitoring/{task_id}`

Удалить задачу мониторинга.

### 9. Морфологический анализ

#### GET `/morphological`

Получить результаты морфологического анализа.

#### POST `/morphological/analyze`

Выполнить морфологический анализ текста.

### 10. Настройки

#### GET `/settings`

Получить настройки приложения.

#### PUT `/settings`

Обновить настройки приложения.

### 11. Отчеты об ошибках

#### GET `/errors/reports`

Получить список отчетов об ошибках.

**Параметры запроса:**

- `page` (int, default: 1) - Номер страницы
- `size` (int, default: 20, max: 100) - Размер страницы
- `error_type` (string, optional) - Тип ошибки
- `severity` (string, optional) - Уровень серьезности
- `operation` (string, optional) - Операция
- `start_date` (datetime, optional) - Начальная дата
- `end_date` (datetime, optional) - Конечная дата
- `is_acknowledged` (bool, optional) - Статус подтверждения

#### GET `/errors/reports/{report_id}`

Получить отчет об ошибке по ID.

### 12. Фоновые задачи

#### GET `/background-tasks`

Получить список фоновых задач.

#### POST `/background-tasks`

Создать новую фоновую задачу.

#### DELETE `/background-tasks/{task_id}`

Удалить фоновую задачу.

## Коды ошибок

| Код | Описание                                          |
| --- | ------------------------------------------------- |
| 400 | Bad Request - Неверный запрос                     |
| 401 | Unauthorized - Требуется авторизация              |
| 403 | Forbidden - Доступ запрещен                       |
| 404 | Not Found - Ресурс не найден                      |
| 409 | Conflict - Конфликт данных                        |
| 422 | Unprocessable Entity - Ошибка валидации           |
| 429 | Too Many Requests - Превышен лимит запросов       |
| 500 | Internal Server Error - Внутренняя ошибка сервера |
| 503 | Service Unavailable - Сервис недоступен           |

## Пагинация

Все эндпоинты, возвращающие списки, поддерживают пагинацию:

- `page` - Номер страницы (начиная с 1)
- `size` - Размер страницы (от 1 до 100)
- `total` - Общее количество элементов
- `pages` - Общее количество страниц
- `has_next` - Есть ли следующая страница
- `has_prev` - Есть ли предыдущая страница

## Фильтрация

Многие эндпоинты поддерживают фильтрацию по различным параметрам:

- По дате (start_date, end_date)
- По статусу (is_viewed, is_archived)
- По категории (group_id, keyword_id)
- По типу (error_type, severity)

## Сортировка

Эндпоинты поддерживают сортировку по различным полям:

- `sort_by` - Поле для сортировки
- `sort_order` - Порядок сортировки (asc/desc)

## Примеры использования

### Получение комментариев с фильтрацией

```bash
curl -X GET "http://localhost:8000/api/v1/comments?page=1&size=20&is_viewed=false&group_id=123" \
  -H "Accept: application/json"
```

### Создание новой группы

```bash
curl -X POST "http://localhost:8000/api/v1/groups" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "vk_id": 12345,
    "name": "Test Group",
    "screen_name": "test_group"
  }'
```

### Получение статистики

```bash
curl -X GET "http://localhost:8000/api/v1/stats" \
  -H "Accept: application/json"
```

## Лимиты и ограничения

- Максимальный размер страницы: 100 элементов
- Максимальная длина текста комментария: 10000 символов
- Максимальное количество ключевых слов: 1000
- Максимальное количество групп: 1000

## Версионирование

API использует семантическое версионирование (SemVer). Текущая версия: 1.0.0

При внесении изменений, нарушающих обратную совместимость, будет создана новая мажорная версия.

## Поддержка

При возникновении проблем с API:

1. Проверьте логи сервера
2. Убедитесь в корректности запроса
3. Проверьте статус сервиса через `/health` эндпоинты
4. Обратитесь к документации или создайте issue в репозитории

## Дополнительные ресурсы

- [Swagger UI](/docs) - Интерактивная документация API
- [ReDoc](/redoc) - Альтернативная документация API
- [OpenAPI Schema](/openapi.json) - Схема API в формате OpenAPI
