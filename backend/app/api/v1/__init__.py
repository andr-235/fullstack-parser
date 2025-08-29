"""
API v1 модуль

Этот пакет содержит все API эндпоинты версии 1.5
для VK Comments Parser с улучшенной архитектурой.
"""

# Импортируем только основной API роутер
from . import api

# Импортируем новые компоненты
from . import schemas, handlers, middleware

__all__ = [
    "api",
    "schemas",
    "handlers",
    "middleware",
]
