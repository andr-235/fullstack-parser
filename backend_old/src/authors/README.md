# Модуль авторов

## Описание

Модуль предоставляет REST API для управления авторами в системе. Поддерживает создание, обновление и удаление авторов.

## Структура файлов

- `api.py` - API роутеры FastAPI
- `models.py` - Модели базы данных
- `schemas.py` - Pydantic схемы для валидации
- `services.py` - Бизнес-логика
- `repository.py` - Работа с базой данных
- `exceptions.py` - Кастомные исключения
- `tests.py` - Тесты

## API эндпоинты

### Создать автора
- **Метод**: POST
- **Путь**: `/authors/`
- **Тело запроса**:
  ```json
  {
    "name": "Имя автора",
    "email": "author@example.com"
  }
  ```
- **Ответ**: 201 Created

### Обновить автора
- **Метод**: PUT
- **Путь**: `/authors/{author_id}`
- **Тело запроса** (опционально):
  ```json
  {
    "name": "Новое имя",
    "email": "newemail@example.com"
  }
  ```
- **Ответ**: 200 OK

### Удалить автора
- **Метод**: DELETE
- **Путь**: `/authors/{author_id}`
- **Ответ**: 204 No Content

## Примеры использования

### Создание автора
```bash
curl -X POST "http://localhost:8000/authors/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Иван Петров", "email": "ivan@example.com"}'
```

### Обновление автора
```bash
curl -X PUT "http://localhost:8000/authors/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Иван Иванов"}'
```

### Удаление автора
```bash
curl -X DELETE "http://localhost:8000/authors/1"