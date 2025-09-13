# Связь между авторами и комментариями

## Обзор

Реализована связь "один-ко-многим" между моделями `AuthorModel` и `Comment`:
- Один автор может иметь много комментариев
- Каждый комментарий принадлежит одному автору

## Изменения в моделях

### AuthorModel (`src/authors/models.py`)
```python
# Добавлена связь с комментариями
comments = relationship("Comment", back_populates="author", lazy="select")
```

### Comment (`src/comments/models.py`)
```python
# Добавлен внешний ключ
author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

# Добавлена связь с автором
author = relationship("AuthorModel", back_populates="comments")
```

## Изменения в схемах

### CommentResponse (`src/comments/schemas.py`)
```python
# Добавлено поле для информации об авторе
author: Optional[AuthorResponse] = Field(None, description="Информация об авторе")
```

### AuthorWithCommentsResponse (`src/authors/schemas.py`)
```python
# Новая схема для автора с комментариями
class AuthorWithCommentsResponse(AuthorResponse):
    comments: List[dict] = Field(default_factory=list, description="Комментарии автора")
```

## Новые API эндпоинты

### Комментарии
- `GET /comments/?include_author=true` - получить комментарии с информацией об авторе
- `GET /comments/{comment_id}?include_author=true` - получить комментарий с автором
- `GET /comments/author/{author_id}` - получить комментарии конкретного автора

### Авторы
- `GET /authors/{author_id}/with-comments` - получить автора с его комментариями

## Миграция базы данных

Создана миграция `2025_09_13_1537-add_author_comment_relationship.py`:
- Добавляет внешний ключ `author_id` в таблицу `comments`
- Создает индекс для оптимизации запросов
- Настраивает каскадное удаление

## Использование

### Получение комментариев с авторами
```python
# В сервисе
comments = await comment_service.get_comments(include_author=True)

# В API
GET /comments/?include_author=true&limit=20&offset=0
```

### Получение автора с комментариями
```python
# В сервисе
author = await author_service.get_author_with_comments(author_id=1)

# В API
GET /authors/1/with-comments?comments_limit=20&comments_offset=0
```

## Производительность

- Используется `lazy="select"` для связи автора с комментариями
- При загрузке комментариев с авторами используется `joinedload` для оптимизации запросов
- Создан индекс на `author_id` для быстрого поиска комментариев по автору

## Безопасность

- Внешний ключ настроен с `CASCADE DELETE` - при удалении автора удаляются все его комментарии
- Валидация данных через Pydantic схемы
- Проверка существования автора при создании комментария
