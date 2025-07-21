"""
Pydantic схемы для VK групп
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# 1. Базовая схема с общими, валидируемыми полями
class VKGroupBase(BaseSchema):
    """Базовая схема VK группы с полями, общими для создания и чтения."""

    screen_name: str = Field(
        ..., description="Короткое имя группы (@group_name)"
    )
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(
        default=True, description="Активен ли мониторинг группы"
    )
    max_posts_to_check: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Максимум постов для проверки",
    )


# 2. Схема для создания новой записи
class VKGroupCreate(BaseSchema):
    """Схема для создания VK группы в БД."""

    vk_id_or_screen_name: str = Field(
        ..., description="ID группы или короткое имя для поиска в VK"
    )
    name: Optional[str] = Field(
        None, description="Название группы (заполняется из VK API)"
    )
    screen_name: Optional[str] = Field(
        None, description="Короткое имя группы (заполняется из VK API)"
    )
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(
        default=True, description="Активен ли мониторинг группы"
    )
    max_posts_to_check: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Максимум постов для проверки",
    )


# 3. Схема для обновления существующей записи
class VKGroupUpdate(BaseSchema):
    """Схема для обновления VK группы. Все поля опциональны."""

    screen_name: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_posts_to_check: Optional[int] = Field(
        default=None,
        ge=1,
        le=10000,
        description="Максимум постов для проверки",
    )


# 4. Схема для возврата данных через API (Read)
class VKGroupRead(VKGroupBase, IDMixin, TimestampMixin):
    """Схема для представления VK группы в API ответах."""

    vk_id: int = Field(..., description="ID группы в ВК")
    last_parsed_at: Optional[datetime] = Field(
        None, description="Когда последний раз парсили группу"
    )
    total_posts_parsed: int = Field(
        default=0, description="Общее количество обработанных постов"
    )
    total_comments_found: int = Field(
        default=0, description="Общее количество найденных комментариев"
    )
    members_count: Optional[int] = Field(
        None, description="Количество участников"
    )
    is_closed: Optional[bool] = Field(None, description="Закрытая ли группа")
    photo_url: Optional[str] = Field(None, description="URL аватара группы")


# 5. Схема для представления данных в базе данных (InDB)
class VKGroupInDB(VKGroupRead):
    """Схема, представляющая полную модель группы в БД."""

    pass


# Статистика остается без изменений, так как у нее другая цель
class VKGroupStats(BaseSchema):
    """Статистика по группе"""

    group_id: int
    total_posts: int
    total_comments: int
    comments_with_keywords: int
    last_activity: Optional[datetime]
    top_keywords: list[str]


# --- Добавлено для корректного импорта в vk_comment.py ---
class VKGroupResponse(BaseSchema):
    """Минимальная схема для вложенного объекта group в комментарии."""

    id: int
    vk_id: int
    name: str
    screen_name: str
    photo_url: Optional[str] = None


class VKGroupUploadResponse(BaseModel):
    """Схема ответа при загрузке групп из файла"""

    status: str = Field(description="Статус операции")
    message: str = Field(description="Сообщение о результате")
    total_processed: int = Field(
        description="Общее количество обработанных строк"
    )
    created: int = Field(description="Количество созданных групп")
    skipped: int = Field(description="Количество пропущенных (дубликатов)")
    errors: list[str] = Field(
        default_factory=list, description="Список ошибок"
    )
    created_groups: list[VKGroupRead] = Field(
        default_factory=list, description="Созданные группы"
    )
