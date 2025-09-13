# Интеграция анализа ключевых слов в комментариях

## Обзор

Модуль `morphological` интегрирован с модулем `comments` для автоматического извлечения ключевых слов из комментариев и создания связей для поиска.

## Архитектура

```
comments/
├── services/
│   └── keyword_analysis_service.py  # Сервис интеграции
├── routers/
│   └── keyword_analysis_router.py   # API эндпоинты
├── schemas/
│   └── keyword_analysis_schemas.py  # Pydantic схемы
└── models.py                        # Модели с методом to_dict()
```

## Функциональность

### 1. Анализ ключевых слов в комментарии
- Извлечение ключевых слов с помощью `morphological` модуля
- Автоматическое создание/обновление ключевых слов в `keywords` модуле
- Создание связей между комментариями и ключевыми словами

### 2. Массовый анализ
- Обработка нескольких комментариев одновременно
- Статистика по результатам анализа

### 3. Поиск комментариев
- Поиск комментариев по ключевым словам
- Фильтрация и пагинация результатов

### 4. Статистика
- Статистика по ключевым словам
- Группировка по категориям
- Топ ключевых слов

## API Эндпоинты

### POST `/api/v1/comments/keyword-analysis/analyze`
Анализ ключевых слов в одном комментарии

**Запрос:**
```json
{
  "comment_id": 123,
  "min_confidence": 0.3,
  "max_keywords": 10
}
```

**Ответ:**
```json
{
  "comment_id": 123,
  "keywords_found": 5,
  "keywords_created": 3,
  "keywords_updated": 2,
  "status": "success"
}
```

### POST `/api/v1/comments/keyword-analysis/analyze-batch`
Массовый анализ ключевых слов

**Запрос:**
```json
{
  "comment_ids": [123, 124, 125],
  "min_confidence": 0.3,
  "max_keywords": 10
}
```

### POST `/api/v1/comments/keyword-analysis/search`
Поиск комментариев по ключевым словам

**Запрос:**
```json
{
  "keywords": ["политика", "экономика"],
  "limit": 20,
  "offset": 0
}
```

### GET `/api/v1/comments/keyword-analysis/statistics`
Статистика ключевых слов

### POST `/api/v1/comments/keyword-analysis/analyze-recent`
Анализ недавних комментариев

## Использование

### 1. Анализ нового комментария
```python
from comments.services.keyword_analysis_service import CommentKeywordAnalysisService

service = CommentKeywordAnalysisService(
    morphological_service=morphological_service,
    keywords_repository=keywords_repository,
    comments_repository=comments_repository
)

result = await service.analyze_comment_keywords(comment_id=123)
```

### 2. Поиск комментариев
```python
comments = await service.search_comments_by_keywords(
    keywords=["политика", "экономика"],
    limit=20
)
```

## Модели данных

### CommentKeywordMatch
Связь между комментарием и ключевым словом:
- `comment_id` - ID комментария
- `keyword` - ключевое слово
- `confidence` - уверенность (0-100)

### Автоматически создаваемые ключевые слова
- Категория: `auto_extracted`
- Приоритет: 3 (низкий)
- Описание: "Автоматически извлечено из комментария {id}"

## Настройки

- `min_confidence` - минимальная уверенность для ключевого слова (0.0-1.0)
- `max_keywords` - максимальное количество ключевых слов (1-50)
- `min_keyword_length` - минимальная длина ключевого слова (3 символа)

## Логирование

Все операции логируются с уровнем INFO/ERROR:
- Успешный анализ комментариев
- Ошибки обработки
- Статистика по результатам

## Интеграция с существующими модулями

- **morphological** - извлечение ключевых слов из текста
- **keywords** - управление ключевыми словами
- **comments** - хранение комментариев и связей
