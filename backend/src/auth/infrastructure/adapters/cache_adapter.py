"""
Адаптер для сервиса кеширования
"""

from typing import Any, Optional

from ..interfaces import ICacheService


class RedisCacheAdapter(ICacheService):
    """Адаптер для Redis кеширования"""

    def __init__(self, redis_client: Any):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        try:
            value = await self.redis_client.get(key)
            return value
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кеш"""
        try:
            if ttl:
                await self.redis_client.setex(key, ttl, value)
            else:
                await self.redis_client.set(key, value)
        except Exception:
            pass  # Игнорируем ошибки кеширования

    async def delete(self, key: str) -> None:
        """Удалить значение из кеша"""
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass

    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception:
            return False


class InMemoryCacheAdapter(ICacheService):
    """Адаптер для in-memory кеширования"""

    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кеш"""
        self._cache[key] = value
        # Для простоты не реализуем TTL

    async def delete(self, key: str) -> None:
        """Удалить значение из кеша"""
        self._cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        return key in self._cache