"""
Pydantic схемы для модуля Groups

Определяет входные и выходные модели данных для API групп VK
"""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class GroupBase(BaseModel):
    """Базовая схема группы"""

    vk_id: int = Field(..., description="ID группы в VK")
    screen_name: str = Field(
        ..., description="Короткое имя группы (@group_name)"
    )
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")


class GroupCreate(GroupBase):
    """Схема для создания группы"""

    pass


class GroupUpdate(BaseModel):
    """Схема для обновления группы"""

    name: Optional[str] = Field(None, description="Новое название группы")
    screen_name: Optional[str] = Field(None, description="Новое короткое имя")
    description: Optional[str] = Field(None, description="Новое описание")
    is_active: Optional[bool] = Field(
        None, description="Активировать/деактивировать группу"
    )
    max_posts_to_check: Optional[int] = Field(
        None, description="Максимум постов для проверки"
    )


class GroupResponse(GroupBase):
    """Схема ответа с информацией о группе"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID в базе данных")
    is_active: bool = Field(default=True, description="Активна ли группа")
    max_posts_to_check: int = Field(
        default=100, description="Максимум постов для проверки"
    )
    members_count: int = Field(default=0, description="Количество участников")
    total_posts_parsed: int = Field(default=0, description="Обработано постов")
    total_comments_found: int = Field(
        default=0, description="Найдено комментариев"
    )
    last_parsed_at: Optional[datetime] = Field(
        None, description="Время последней обработки"
    )
    photo_url: Optional[str] = Field(None, description="URL фото группы")
    is_closed: bool = Field(default=False, description="Закрыта ли группа")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(
        ..., description="Время последнего обновления"
    )


class GroupListResponse(PaginatedResponse[GroupResponse]):
    """Схема ответа со списком групп"""

    pass


class GroupFilter(BaseModel):
    """Фильтры для поиска групп"""

    is_active: Optional[bool] = Field(
        None, description="Показать только активные группы"
    )
    search: Optional[str] = Field(
        None, description="Поиск по названию или screen_name"
    )
    has_monitoring: Optional[bool] = Field(
        None, description="Показать группы с мониторингом"
    )
    min_members: Optional[int] = Field(
        None, description="Минимальное количество участников"
    )
    max_members: Optional[int] = Field(
        None, description="Максимальное количество участников"
    )


class GroupStats(BaseModel):
    """Статистика группы"""

    id: int = Field(..., description="ID группы")
    vk_id: int = Field(..., description="VK ID группы")
    name: str = Field(..., description="Название группы")
    total_comments: int = Field(
        ..., description="Общее количество комментариев"
    )
    active_comments: int = Field(
        ..., description="Количество активных комментариев"
    )
    parsed_posts_count: int = Field(
        ..., description="Количество обработанных постов"
    )
    avg_comments_per_post: float = Field(
        ..., description="Среднее комментариев на пост"
    )
    last_activity: Optional[datetime] = Field(
        None, description="Время последней активности"
    )


class GroupsStats(BaseModel):
    """Общая статистика по группам"""

    total_groups: int = Field(..., description="Общее количество групп")
    active_groups: int = Field(..., description="Количество активных групп")
    total_comments: int = Field(
        ..., description="Общее количество комментариев"
    )
    total_parsed_posts: int = Field(
        ..., description="Общее количество обработанных постов"
    )
    avg_comments_per_group: float = Field(
        ..., description="Среднее комментариев на группу"
    )


class GroupBulkAction(BaseModel):
    """Массовые действия с группами"""

    group_ids: List[int] = Field(..., description="Список ID групп")
    action: str = Field(
        ...,
        description="Действие: activate, deactivate, enable_monitoring, disable_monitoring",
    )


class GroupBulkResponse(BaseModel):
    """Ответ на массовое действие"""

    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Список ошибок"
    )


class GroupMonitoringConfig(BaseModel):
    """Конфигурация мониторинга группы"""

    enabled: bool = Field(default=True, description="Включен ли мониторинг")
    interval_minutes: int = Field(
        default=60, description="Интервал проверки в минутах"
    )
    max_posts_to_check: int = Field(
        default=100, description="Максимум постов для проверки"
    )
    priority: int = Field(default=5, description="Приоритет группы (1-10)")


class GroupCreateWithMonitoring(GroupCreate):
    """Создание группы с настройками мониторинга"""

    monitoring_config: Optional[GroupMonitoringConfig] = Field(
        None, description="Конфигурация мониторинга"
    )


# Экспорт всех схем
__all__ = [
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupResponse",
    "GroupListResponse",
    "GroupFilter",
    "GroupStats",
    "GroupsStats",
    "GroupBulkAction",
    "GroupBulkResponse",
    "GroupMonitoringConfig",
    "GroupCreateWithMonitoring",
]
