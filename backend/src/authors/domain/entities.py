"""
Доменные сущности модуля авторов

Бизнес-объекты без привязки к инфраструктуре
"""

from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorEntity:
    """Доменная сущность автора VK."""
    
    id: int
    vk_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    screen_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    comments_count: int = 0

    def __post_init__(self):
        """Валидация после инициализации."""
        if self.vk_id <= 0:
            raise ValueError("VK ID должен быть положительным числом")
        
        if self.photo_url and not self.photo_url.startswith(('http://', 'https://')):
            raise ValueError("URL фото должен начинаться с http:// или https://")

    @property
    def full_name(self) -> str:
        """Полное имя автора."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else str(self.vk_id)

    @property
    def display_name(self) -> str:
        """Отображаемое имя автора."""
        if self.screen_name:
            return self.screen_name
        return self.full_name

    def is_updated(self) -> bool:
        """Проверка, был ли автор обновлен."""
        return self.updated_at is not None

    def to_dict(self) -> dict[str, any]:
        """Преобразование в словарь для сериализации."""
        return {
            "id": self.id,
            "vk_id": self.vk_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "screen_name": self.screen_name,
            "photo_url": self.photo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "comments_count": self.comments_count,
        }
