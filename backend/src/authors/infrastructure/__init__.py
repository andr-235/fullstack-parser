"""
Infrastructure слой модуля авторов

Содержит реализации репозиториев, кэша и внешних сервисов
"""

from .models import Author
from .repositories import AuthorRepository
from .cache import AuthorRedisCache
from .task_queue import AuthorCeleryTaskQueue

__all__ = [
    "Author",
    "AuthorRepository",
    "AuthorRedisCache", 
    "AuthorCeleryTaskQueue"
]
