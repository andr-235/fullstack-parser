"""
Инфраструктурный сервис кеширования

Предоставляет унифицированный интерфейс для кеширования данных
"""

import json
import pickle
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import infrastructure_config
from .logging import get_loguru_logger


class CacheService:
    """
    Инфраструктурный сервис для работы с кешем Redis

    Предоставляет унифицированный интерфейс для кеширования
    во всех слоях архитектуры
    """

    def __init__(self):
        self._redis: Optional[Redis] = None
        self._initialized = False
        self.default_ttl = infrastructure_config.CACHE_DEFAULT_TTL
        self.logger = get_loguru_logger("cache")

        # Cache key prefixes для разных типов данных
        self.prefixes = {
            "user": "user:",
            "group": "group:",
            "comment": "comment:",
            "post": "post:",
            "keyword": "keyword:",
            "parse_result": "parse:",
            "config": "config:",
            "stats": "stats:",
            "domain": "domain:",
            "health": "health:",
            "error": "error:",
            "auth": "auth:",
            "settings": "settings:",
        }

        # Метрики
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_sets = 0
        self._cache_deletes = 0

    async def init_cache(self) -> None:
        """Инициализировать подключение к Redis"""
        if self._initialized:
            return

        cache_config = infrastructure_config.get_cache_config()

        try:
            # Попытка подключения к Redis
            self._redis = redis.from_url(
                cache_config["redis_url"],
                decode_responses=cache_config["decode_responses"],
                retry_on_timeout=cache_config["retry_on_timeout"],
                socket_timeout=cache_config["socket_timeout"],
                socket_connect_timeout=cache_config["socket_connect_timeout"],
            )

            # Проверяем подключение
            await self._redis.ping()
            self._initialized = True
            self.logger.info("Redis cache initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cache: {e}")
            # Fallback to in-memory cache
            self._redis = None

    async def close_cache(self) -> None:
        """Закрыть подключение к кешу"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._initialized = False

    def _get_key(self, prefix: str, identifier: str) -> str:
        """Генерировать ключ кеша с префиксом"""
        if prefix not in self.prefixes:
            raise ValueError(f"Invalid cache prefix: {prefix}")
        return f"{self.prefixes[prefix]}{identifier}"

    async def get(
        self, prefix: str, identifier: str, default: Any = None
    ) -> Any:
        """
        Получить значение из кеша

        Args:
            prefix: Префикс ключа (user, group, comment, etc.)
            identifier: Уникальный идентификатор
            default: Значение по умолчанию

        Returns:
            Значение из кеша или default
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return default

        try:
            key = self._get_key(prefix, identifier)
            value = await self._redis.get(key)

            if value is None:
                self._cache_misses += 1
                return default

            # Попытаться распарсить JSON
            try:
                result = json.loads(value)
                self._cache_hits += 1
                return result
            except (json.JSONDecodeError, TypeError):
                self._cache_hits += 1
                return value

        except Exception as e:
            self.logger.error(
                f"Cache get error for {prefix}:{identifier}: {e}"
            )
            return default

    async def set(
        self,
        prefix: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Сохранить значение в кеш

        Args:
            prefix: Префикс ключа
            identifier: Уникальный идентификатор
            value: Значение для сохранения
            ttl: Время жизни в секундах

        Returns:
            True если успешно сохранено
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return False

        try:
            key = self._get_key(prefix, identifier)

            # Сериализуем значение
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif isinstance(value, str):
                serialized_value = value
            else:
                # Для сложных объектов используем pickle
                serialized_value = pickle.dumps(value).decode("latin1")

            ttl_value = ttl or self.default_ttl
            success = await self._redis.set(
                key, serialized_value, ex=ttl_value
            )

            success = bool(success)
            if success:
                self._cache_sets += 1
            return success

        except Exception as e:
            self.logger.error(
                f"Cache set error for {prefix}:{identifier}: {e}"
            )
            return False

    async def delete(self, prefix: str, identifier: str) -> bool:
        """
        Удалить значение из кеша

        Args:
            prefix: Префикс ключа
            identifier: Уникальный идентификатор

        Returns:
            True если успешно удалено
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return False

        try:
            key = self._get_key(prefix, identifier)
            result = await self._redis.delete(key)
            return result > 0

        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def exists(self, prefix: str, identifier: str) -> bool:
        """
        Проверить существование ключа

        Args:
            prefix: Префикс ключа
            identifier: Уникальный идентификатор

        Returns:
            True если ключ существует
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return False

        try:
            key = self._get_key(prefix, identifier)
            result = await self._redis.exists(key)
            return result > 0

        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """
        Очистить все ключи с определенным префиксом

        Args:
            prefix: Префикс для очистки

        Returns:
            Количество удаленных ключей
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return 0

        try:
            if prefix not in self.prefixes:
                raise ValueError(f"Invalid cache prefix: {prefix}")

            pattern = f"{self.prefixes[prefix]}*"
            keys = await self._redis.keys(pattern)

            if keys:
                result = await self._redis.delete(*keys)
                return result
            return 0

        except Exception as e:
            print(f"Cache clear prefix error: {e}")
            return 0

    async def get_multiple(
        self, prefix: str, identifiers: List[str]
    ) -> Dict[str, Any]:
        """
        Получить несколько значений из кеша

        Args:
            prefix: Префикс ключей
            identifiers: Список идентификаторов

        Returns:
            Словарь идентификатор -> значение
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return {}

        try:
            keys = [
                self._get_key(prefix, identifier) for identifier in identifiers
            ]
            values = await self._redis.mget(keys)

            result = {}
            for identifier, value in zip(identifiers, values):
                if value is not None:
                    try:
                        result[identifier] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[identifier] = value

            return result

        except Exception as e:
            print(f"Cache get multiple error: {e}")
            return {}

    async def set_multiple(
        self, prefix: str, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> int:
        """
        Сохранить несколько значений в кеш

        Args:
            prefix: Префикс ключей
            data: Словарь идентификатор -> значение
            ttl: Время жизни в секундах

        Returns:
            Количество успешно сохраненных значений
        """
        if not self._initialized:
            await self.init_cache()

        if not self._redis:
            return 0

        try:
            pipeline = self._redis.pipeline()

            for identifier, value in data.items():
                key = self._get_key(prefix, identifier)

                # Сериализуем значение
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value)
                elif isinstance(value, str):
                    serialized_value = value
                else:
                    serialized_value = pickle.dumps(value).decode("latin1")

                ttl_value = ttl or self.default_ttl
                pipeline.set(key, serialized_value, ex=ttl_value)

            results = await pipeline.execute()
            return sum(1 for result in results if result)

        except Exception as e:
            print(f"Cache set multiple error: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья кеша

        Returns:
            Статус здоровья кеша
        """
        if not self._initialized:
            await self.init_cache()

        try:
            if not self._redis:
                return {
                    "status": "unhealthy",
                    "error": "Redis client not initialized",
                }

            # Проверяем подключение
            await self._redis.ping()

            # Получаем информацию о Redis
            info = await self._redis.info()

            return {
                "status": "healthy",
                "redis_url": "redis://localhost:6379",  # Можно вынести в настройки
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_keys": await self._redis.dbsize(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "redis_url": "redis://localhost:6379",
            }

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кеша

        Returns:
            Статистика использования кеша
        """
        if not self._initialized:
            await self.init_cache()

        try:
            if not self._redis:
                return {
                    "error": "Redis client not initialized",
                }

            # Получаем информацию о Redis
            info = await self._redis.info()

            # Подсчитываем ключи по префиксам
            prefix_stats = {}
            for prefix_name, prefix_value in self.prefixes.items():
                try:
                    pattern = f"{prefix_value}*"
                    keys = await self._redis.keys(pattern)
                    prefix_stats[prefix_name] = len(keys)
                except:
                    prefix_stats[prefix_name] = 0

            return {
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_keys": await self._redis.dbsize(),
                "keys_by_prefix": prefix_stats,
                "uptime_days": info.get("uptime_in_days", 0),
            }

        except Exception as e:
            return {
                "error": str(e),
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Получить метрики использования кеша

        Returns:
            Метрики кеширования
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (
            (self._cache_hits / total_requests) if total_requests > 0 else 0
        )

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_sets": self._cache_sets,
            "cache_deletes": self._cache_deletes,
            "hit_rate": round(hit_rate, 3),
            "total_requests": total_requests,
            "redis_enabled": self._redis is not None,
            "cache_initialized": self._initialized,
        }


# Глобальный экземпляр сервиса кеширования
@lru_cache(maxsize=1)
def get_cache_service() -> CacheService:
    """Получить экземпляр сервиса кеширования (кешируется)"""
    return CacheService()


# Глобальный объект для обратной совместимости
cache_service = get_cache_service()


# Экспорт
__all__ = [
    "CacheService",
    "get_cache_service",
    "cache_service",
]
