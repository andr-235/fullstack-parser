"""
Адаптер для сервиса кеширования
"""

from typing import Any, Optional

from ..interfaces import ICacheService


class CacheServiceAdapter(ICacheService):
    """Адаптер для сервиса кеширования"""

    def __init__(self, cache_service):
        self.service = cache_service

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        return await self.service.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кеш"""
        await self.service.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        """Удалить значение из кеша"""
        await self.service.delete(key)