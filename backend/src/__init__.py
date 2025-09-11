"""
VK Parser Backend

FastAPI backend для парсинга комментариев VK
"""

# Импортируем все модели для регистрации в metadata
from .models import *
from .parser.models import ParsingTaskModel

# Экспортируем Base для использования в других модулях
from .models import Base

__all__ = ["Base"]
