# Модуль морфологического анализа

Простой и эффективный модуль для анализа русских текстов с использованием pymorphy2.

## Структура

```
morphological/
├── __init__.py      # Экспорты модуля
├── schemas.py       # Pydantic схемы для API
├── service.py       # Бизнес-логика анализа
├── router.py        # FastAPI эндпоинты
└── README.md        # Документация
```

## Основные возможности

- **Анализ слов**: Морфологический разбор отдельных слов
- **Анализ текста**: Полный анализ текста с разбивкой на предложения
- **Извлечение ключевых слов**: Автоматическое извлечение ключевых слов
- **Определение языка**: Простое определение языка текста
- **Кеширование**: In-memory кеш для ускорения повторных запросов

## API эндпоинты

- `POST /morphological/analyze-word` - Анализ слова
- `GET /morphological/word/{word}` - Анализ слова (GET)
- `POST /morphological/analyze-text` - Анализ текста
- `POST /morphological/extract-keywords` - Извлечение ключевых слов
- `POST /morphological/detect-language` - Определение языка
- `GET /morphological/stats` - Статистика анализа
- `GET /morphological/health` - Проверка здоровья

## Использование

```python
from morphological import MorphologicalService

service = MorphologicalService()

# Анализ слова
word_info = await service.analyze_word("привет")

# Анализ текста
text_info = await service.analyze_text("Привет, как дела?")

# Извлечение ключевых слов
keywords = await service.extract_keywords("Текст для анализа")
```

## Зависимости

- `pymorphy2` - Морфологический анализатор
- `fastapi` - Web фреймворк
- `pydantic` - Валидация данных
