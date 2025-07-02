"""
Базовые Pydantic схемы для VK Comments Parser
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема с общими настройками"""

    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Миксин для временных меток"""

    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """Миксин для ID"""

    id: int


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    """Ответ с пагинацией"""

    total: int
    skip: int
    limit: int
    items: list


class StatusResponse(BaseModel):
    """Стандартный ответ о статусе"""

    success: bool
    message: str
    data: Optional[dict] = None
