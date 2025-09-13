"""
VK Parser Backend

FastAPI backend для парсинга комментариев VK
Clean Architecture implementation
"""

# Базовый класс для SQLAlchemy моделей
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

__all__ = ["Base"]
