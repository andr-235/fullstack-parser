"""
Enhanced Redis cache service with TTL, invalidation, and error handling.
Provides structured caching with automatic fallback to database.
"""

import json
import pickle
from typing import Any, Dict, List, Optional

from redis.asyncio import Redis
from structlog import get_logger

from .exceptions import CacheError

logger = get_logger()


class CacheService:
    """Enhanced Redis cache service with error handling and structured operations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour default

        # Cache key prefixes for different data types
        self.prefixes = {
            "user": "user:",
            "group": "group:",
            "comment": "comment:",
            "parse_result": "parse:",
            "config": "config:",
            "stats": "stats:",
        }

    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix."""
        if prefix not in self.prefixes:
            raise CacheError(f"Invalid cache prefix: {prefix}")
        return f"{self.prefixes[prefix]}{identifier}"

    async def get(
        self, prefix: str, identifier: str, default: Any = None
    ) -> Any:
        """
        Get value from cache with error handling.

        Args:
            prefix: Cache key prefix (user, group, comment, etc.)
            identifier: Unique identifier for the data
            default: Default value if not found

        Returns:
            Cached value or default
        """
        try:
            key = self._get_key(prefix, identifier)
            value = await self.redis.get(key)

            if value is None:
                logger.debug(
                    "Cache miss", key=key, prefix=prefix, identifier=identifier
                )
                return default

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value)
                except (pickle.UnpicklingError, TypeError):
                    logger.warning(
                        "Failed to deserialize cached value", key=key
                    )
                    return default

        except Exception as e:
            logger.error(
                "Cache get error",
                prefix=prefix,
                identifier=identifier,
                error=str(e),
            )
            raise CacheError(
                f"Failed to get from cache: {str(e)}", cache_key=key
            )

    async def set(
        self,
        prefix: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            prefix: Cache key prefix
            identifier: Unique identifier
            value: Value to cache
            ttl: Time to live in seconds (None for default)
            serialize: Whether to serialize the value

        Returns:
            True if successful
        """
        try:
            key = self._get_key(prefix, identifier)

            if serialize:
                # Try JSON first, fallback to pickle
                try:
                    serialized = json.dumps(value)
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)
            else:
                serialized = value

            ttl = ttl or self.default_ttl
            result = await self.redis.setex(key, ttl, serialized)

            logger.debug("Cache set", key=key, ttl=ttl, success=result)

            return result

        except Exception as e:
            logger.error(
                "Cache set error",
                prefix=prefix,
                identifier=identifier,
                error=str(e),
            )
            raise CacheError(f"Failed to set cache: {str(e)}", cache_key=key)

    async def delete(self, prefix: str, identifier: str) -> bool:
        """Delete value from cache."""
        try:
            key = self._get_key(prefix, identifier)
            result = await self.redis.delete(key)

            logger.debug("Cache delete", key=key, success=result > 0)
            return result > 0

        except Exception as e:
            logger.error(
                "Cache delete error",
                prefix=prefix,
                identifier=identifier,
                error=str(e),
            )
            raise CacheError(
                f"Failed to delete from cache: {str(e)}", cache_key=key
            )

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                result = await self.redis.delete(*keys)
                logger.info(
                    "Cache pattern invalidation",
                    pattern=pattern,
                    keys_deleted=result,
                )
                return result
            return 0

        except Exception as e:
            logger.error(
                "Cache pattern invalidation error",
                pattern=pattern,
                error=str(e),
            )
            raise CacheError(f"Failed to invalidate pattern: {str(e)}")

    async def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all keys with specific prefix."""
        if prefix not in self.prefixes:
            raise CacheError(f"Invalid prefix: {prefix}")

        pattern = f"{self.prefixes[prefix]}*"
        return await self.invalidate_pattern(pattern)

    async def get_many(
        self, prefix: str, identifiers: List[str]
    ) -> Dict[str, Any]:
        """Get multiple values from cache."""
        try:
            keys = [
                self._get_key(prefix, identifier) for identifier in identifiers
            ]
            values = await self.redis.mget(keys)

            result = {}
            for identifier, value in zip(identifiers, values, strict=False):
                if value is not None:
                    try:
                        result[identifier] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        try:
                            result[identifier] = pickle.loads(value)
                        except (pickle.UnpicklingError, TypeError):
                            logger.warning(
                                "Failed to deserialize cached value",
                                identifier=identifier,
                            )
                            continue
                else:
                    result[identifier] = None

            logger.debug(
                "Cache get_many",
                prefix=prefix,
                requested=len(identifiers),
                found=len([v for v in result.values() if v is not None]),
            )
            return result

        except Exception as e:
            logger.error(
                "Cache get_many error",
                prefix=prefix,
                identifiers=identifiers,
                error=str(e),
            )
            raise CacheError(f"Failed to get many from cache: {str(e)}")

    async def set_many(
        self, prefix: str, data: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Set multiple values in cache."""
        try:
            ttl = ttl or self.default_ttl
            pipeline = self.redis.pipeline()

            for identifier, value in data.items():
                key = self._get_key(prefix, identifier)
                try:
                    serialized = json.dumps(value)
                except (TypeError, ValueError):
                    serialized = pickle.dumps(value)

                pipeline.setex(key, ttl, serialized)

            await pipeline.execute()
            logger.debug(
                "Cache set_many", prefix=prefix, count=len(data), ttl=ttl
            )
            return True

        except Exception as e:
            logger.error("Cache set_many error", prefix=prefix, error=str(e))
            raise CacheError(f"Failed to set many in cache: {str(e)}")

    async def exists(self, prefix: str, identifier: str) -> bool:
        """Check if key exists in cache."""
        try:
            key = self._get_key(prefix, identifier)
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(
                "Cache exists error",
                prefix=prefix,
                identifier=identifier,
                error=str(e),
            )
            return False

    async def ttl(self, prefix: str, identifier: str) -> int:
        """Get remaining TTL for key."""
        try:
            key = self._get_key(prefix, identifier)
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(
                "Cache TTL error",
                prefix=prefix,
                identifier=identifier,
                error=str(e),
            )
            return -1

    async def health_check(self) -> bool:
        """Check if Redis is available."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False


class CacheManager:
    """Manager for multiple cache services with fallback strategies."""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self._cache_enabled = True

    @property
    def cache_enabled(self) -> bool:
        return self._cache_enabled

    @cache_enabled.setter
    def cache_enabled(self, value: bool):
        self._cache_enabled = value
        logger.info("Cache enabled", enabled=value)

    async def get_with_fallback(
        self,
        prefix: str,
        identifier: str,
        fallback_func: callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Get from cache with automatic fallback to database.

        Args:
            prefix: Cache key prefix
            identifier: Unique identifier
            fallback_func: Function to call if cache miss
            ttl: Cache TTL
            *args, **kwargs: Arguments for fallback function

        Returns:
            Value from cache or fallback
        """
        if not self.cache_enabled:
            return await fallback_func(*args, **kwargs)

        try:
            # Try cache first
            cached_value = await self.cache.get(prefix, identifier)
            if cached_value is not None:
                return cached_value

            # Fallback to database
            value = await fallback_func(*args, **kwargs)

            # Cache the result
            if value is not None:
                await self.cache.set(prefix, identifier, value, ttl)

            return value

        except CacheError as e:
            logger.warning("Cache error, using fallback", error=str(e))
            return await fallback_func(*args, **kwargs)
        except Exception as e:
            logger.error("Unexpected error in get_with_fallback", error=str(e))
            return await fallback_func(*args, **kwargs)

    async def invalidate_user_data(self, user_id: str) -> int:
        """Invalidate all cache entries for a specific user."""
        return await self.cache.invalidate_pattern(f"user:{user_id}*")

    async def invalidate_group_data(self, group_id: str) -> int:
        """Invalidate all cache entries for a specific group."""
        return await self.cache.invalidate_pattern(f"group:{group_id}*")

    async def invalidate_parse_results(self, parse_id: str) -> int:
        """Invalidate parse results for a specific parse operation."""
        return await self.cache.invalidate_pattern(f"parse:{parse_id}*")
