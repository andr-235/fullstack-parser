"""
Presentation слой модуля авторов

Содержит FastAPI роутеры и обработчики запросов
"""

from .routers import authors_router

__all__ = [
    "authors_router"
]
