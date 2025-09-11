"""
Кэш авторов - инфраструктурный слой

Реализация кэширования с использованием Redis
"""

from __future__ import annotations
from typing import Optional
import json
import logging
from datetime import datetime

from ..domain.entities import AuthorEntity
from ..domain.interfaces import AuthorCacheInterface

logger = logging.getLogger(__name__)


class AuthorRedisCache(AuthorCacheInterface):
    """Redis кэш для авторов."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[AuthorEntity]:
        """Получить автора из кэша."""
        try:
            cached_data = await self.redis.get(key)
            if not cached_data:
                return None

            data = json.loads(cached_data)
            return self._dict_to_entity(data)
        except Exception as e:
            logger.error(f"Error getting author from cache {key}: {e}")
            return None

    async def set(self, key: str, author: AuthorEntity, ttl: int = 3600) -> None:
        """Сохранить автора в кэш."""
        try:
            data = self._entity_to_dict(author)
            await self.redis.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Error setting author to cache {key}: {e}")

    async def delete(self, key: str) -> None:
        """Удалить автора из кэша."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Error deleting author from cache {key}: {e}")

    async def invalidate_pattern(self, pattern: str) -> None:
        """Инвалидировать кэш по паттерну."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")

    def _entity_to_dict(self, author: AuthorEntity) -> dict:
        """Преобразовать сущность в словарь для сериализации."""
        return {
            "id": author.id,
            "vk_id": author.vk_id,
            "first_name": author.first_name,
            "last_name": author.last_name,
            "screen_name": author.screen_name,
            "photo_url": author.photo_url,
            "created_at": author.created_at.isoformat() if author.created_at else None,
            "updated_at": author.updated_at.isoformat() if author.updated_at else None,
        }

    def _dict_to_entity(self, data: dict) -> AuthorEntity:
        """Преобразовать словарь в сущность."""
        return AuthorEntity(
            id=data["id"],
            vk_id=data["vk_id"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            screen_name=data.get("screen_name"),
            photo_url=data.get("photo_url"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
