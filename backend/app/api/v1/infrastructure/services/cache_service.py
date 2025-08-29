"""
Сервис кеширования с Redis (DDD Infrastructure Service)

Реализация CacheService для работы с Redis в рамках DDD архитектуры.
"""

import json
import pickle
import logging
from typing import Any, Optional, Dict
from datetime import timedelta

import redis.asyncio as redis

from .base import CacheService
from ...domain.base import Entity

logger = logging.getLogger(__name__)


class RedisCacheService(CacheService):
    """
    Redis реализация сервиса кеширования

    Предоставляет высокопроизводительное кеширование для Domain Entities
    и других данных в рамках DDD архитектуры.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,  # 1 час по умолчанию
        max_connections: int = 10,
        key_prefix: str = "vk_comments:",
    ):
        """
        Инициализация Redis кеша

        Args:
            redis_url: URL Redis сервера
            default_ttl: Время жизни ключа по умолчанию (секунды)
            max_connections: Максимальное количество соединений
            key_prefix: Префикс для ключей
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.max_connections = max_connections
        self.key_prefix = key_prefix
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """Получить Redis клиент (ленивая инициализация)"""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                decode_responses=False,  # Для работы с байтами
            )
        return self._redis

    def _make_key(self, key: str) -> str:
        """Создать полный ключ с префиксом"""
        return f"{self.key_prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кеша

        Args:
            key: Ключ

        Returns:
            Значение или None если ключ не найден
        """
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)

            value = await redis_client.get(full_key)
            if value is None:
                return None

            # Декодируем JSON для простых типов
            try:
                return json.loads(value.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Если не JSON, возвращаем как есть
                return pickle.loads(value)

        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """
        Установить значение в кеш

        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни (секунды)
        """
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)

            # Сериализуем значение
            if isinstance(value, (str, int, float, bool, list, dict)):
                serialized_value = json.dumps(value).encode("utf-8")
            else:
                # Для сложных объектов используем pickle
                serialized_value = pickle.dumps(value)

            # Устанавливаем TTL
            ttl_value = ttl or self.default_ttl

            await redis_client.setex(full_key, ttl_value, serialized_value)

        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")

    async def delete(self, key: str) -> bool:
        """
        Удалить значение из кеша

        Args:
            key: Ключ

        Returns:
            True если ключ был удален
        """
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)

            result = await redis_client.delete(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Проверить существование ключа

        Args:
            key: Ключ

        Returns:
            True если ключ существует
        """
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)

            result = await redis_client.exists(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Установить время жизни ключа

        Args:
            key: Ключ
            ttl: Время жизни (секунды)

        Returns:
            True если операция успешна
        """
        try:
            redis_client = await self._get_redis()
            full_key = self._make_key(key)

            result = await redis_client.expire(full_key, ttl)
            return result

        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Удалить все ключи по паттерну

        Args:
            pattern: Паттерн для поиска ключей

        Returns:
            Количество удаленных ключей
        """
        try:
            redis_client = await self._get_redis()
            full_pattern = self._make_key(pattern)

            # Получаем все ключи по паттерну
            keys = await redis_client.keys(full_pattern)

            if not keys:
                return 0

            # Удаляем ключи
            result = await redis_client.delete(*keys)
            logger.info(
                f"Cleared {result} cache keys with pattern '{pattern}'"
            )
            return result

        except Exception as e:
            logger.error(
                f"Cache clear pattern error for pattern '{pattern}': {e}"
            )
            return 0

    # Специфические методы для Domain Entities

    async def get_domain_entity(
        self, entity_type: str, entity_id: str
    ) -> Optional[Entity]:
        """
        Получить Domain Entity из кеша

        Args:
            entity_type: Тип сущности (comment, group, etc.)
            entity_id: ID сущности

        Returns:
            Domain Entity или None
        """
        key = f"{entity_type}:{entity_id}"
        return await self.get(key)

    async def set_domain_entity(
        self,
        entity_type: str,
        entity_id: str,
        entity: Entity,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Сохранить Domain Entity в кеш

        Args:
            entity_type: Тип сущности
            entity_id: ID сущности
            entity: Domain Entity
            ttl: Время жизни
        """
        key = f"{entity_type}:{entity_id}"
        await self.set(key, entity, ttl)

    async def invalidate_domain_entity(
        self, entity_type: str, entity_id: str
    ) -> bool:
        """
        Инвалидировать кеш Domain Entity

        Args:
            entity_type: Тип сущности
            entity_id: ID сущности

        Returns:
            True если ключ был удален
        """
        key = f"{entity_type}:{entity_id}"
        return await self.delete(key)

    async def invalidate_entity_collection(self, entity_type: str) -> int:
        """
        Инвалидировать кеш коллекции сущностей

        Args:
            entity_type: Тип сущности

        Returns:
            Количество удаленных ключей
        """
        pattern = f"{entity_type}:*"
        return await self.clear_pattern(pattern)

    async def get_cached_query_result(
        self, query_hash: str, entity_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить кешированный результат запроса

        Args:
            query_hash: Хеш запроса
            entity_type: Тип сущности

        Returns:
            Кешированный результат или None
        """
        key = f"query:{entity_type}:{query_hash}"
        return await self.get(key)

    async def set_cached_query_result(
        self,
        query_hash: str,
        entity_type: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """
        Сохранить результат запроса в кеш

        Args:
            query_hash: Хеш запроса
            entity_type: Тип сущности
            result: Результат запроса
            ttl: Время жизни
        """
        key = f"query:{entity_type}:{query_hash}"
        await self.set(key, result, ttl)

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья Redis соединения

        Returns:
            Словарь с информацией о здоровье сервиса
        """
        try:
            redis_client = await self._get_redis()

            # Проверяем соединение
            pong = await redis_client.ping()
            if pong:
                # Получаем базовую информацию
                info = await redis_client.info()
                return {
                    "status": "healthy",
                    "redis_version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "uptime_days": info.get("uptime_in_days", 0),
                }

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

        return {"status": "unknown"}
