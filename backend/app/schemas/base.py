"""
Базовые Pydantic схемы для VK Comments Parser
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Базовая схема Pydantic с общей конфигурацией."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class TimestampMixin(BaseModel):
    """Миксин для добавления временных меток created_at и updated_at."""

    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(
        ..., description="Время последнего обновления"
    )


class IDMixin(BaseModel):
    """Миксин для добавления поля ID."""

    id: int = Field(..., description="Уникальный идентификатор")


class PaginationParams(BaseModel):
    """Параметры для пагинации."""

    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(10000, ge=1, le=10000, description="Размер страницы")

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Обобщенная схема для пагинированных ответов."""

    total: int = Field(..., description="Общее количество записей")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Количество записей на странице")
    items: List[T] = Field(..., description="Список элементов на странице")


class StatusResponse(BaseSchema):
    """Схема для стандартного ответа со статусом."""

    status: str
    message: Optional[str] = None
