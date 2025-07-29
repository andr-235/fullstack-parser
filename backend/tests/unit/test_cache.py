"""
Unit tests for cache service.
"""

import pytest
import json
import pickle
from unittest.mock import AsyncMock, MagicMock
from structlog import get_logger

from app.core.cache import CacheService, CacheManager
from app.core.exceptions import CacheError

logger = get_logger()


class TestCacheService:
    """Test cache service functionality."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.get = AsyncMock()
        mock.setex = AsyncMock()
        mock.delete = AsyncMock()
        mock.keys = AsyncMock()
        mock.mget = AsyncMock()
        mock.pipeline = MagicMock()
        mock.exists = AsyncMock()
        mock.ttl = AsyncMock()
        mock.ping = AsyncMock()
        return mock

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create cache service with mock Redis."""
        return CacheService(mock_redis)

    def test_get_key_valid_prefix(self, cache_service):
        """Test getting cache key with valid prefix."""
        key = cache_service._get_key("user", "123")
        assert key == "user:123"

    def test_get_key_invalid_prefix(self, cache_service):
        """Test getting cache key with invalid prefix."""
        with pytest.raises(CacheError, match="Invalid cache prefix"):
            cache_service._get_key("invalid", "123")

    @pytest.mark.asyncio
    async def test_get_cache_hit_json(self, cache_service, mock_redis):
        """Test getting value from cache with JSON data."""
        test_data = {"id": 123, "name": "test"}
        mock_redis.get.return_value = json.dumps(test_data)

        result = await cache_service.get("user", "123")

        assert result == test_data
        mock_redis.get.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_get_cache_hit_pickle(self, cache_service, mock_redis):
        """Test getting value from cache with pickle data."""
        test_data = {"id": 123, "name": "test"}
        mock_redis.get.return_value = pickle.dumps(test_data)

        result = await cache_service.get("user", "123")

        assert result == test_data
        mock_redis.get.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_service, mock_redis):
        """Test getting value from cache miss."""
        mock_redis.get.return_value = None

        result = await cache_service.get("user", "123", default="default")

        assert result == "default"
        mock_redis.get.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_get_cache_error(self, cache_service, mock_redis):
        """Test getting value from cache with error."""
        mock_redis.get.side_effect = Exception("Redis error")

        with pytest.raises(CacheError, match="Failed to get from cache"):
            await cache_service.get("user", "123")

    @pytest.mark.asyncio
    async def test_set_cache_success(self, cache_service, mock_redis):
        """Test setting value in cache successfully."""
        test_data = {"id": 123, "name": "test"}
        mock_redis.setex.return_value = True

        result = await cache_service.set("user", "123", test_data, ttl=3600)

        assert result is True
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "user:123"  # key
        assert call_args[0][1] == 3600  # ttl
        assert json.loads(call_args[0][2]) == test_data  # value

    @pytest.mark.asyncio
    async def test_set_cache_with_default_ttl(self, cache_service, mock_redis):
        """Test setting value in cache with default TTL."""
        test_data = {"id": 123}
        mock_redis.setex.return_value = True

        result = await cache_service.set("user", "123", test_data)

        assert result is True
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 3600  # default TTL

    @pytest.mark.asyncio
    async def test_set_cache_error(self, cache_service, mock_redis):
        """Test setting value in cache with error."""
        mock_redis.setex.side_effect = Exception("Redis error")

        with pytest.raises(CacheError, match="Failed to set cache"):
            await cache_service.set("user", "123", {"test": "data"})

    @pytest.mark.asyncio
    async def test_delete_cache_success(self, cache_service, mock_redis):
        """Test deleting value from cache successfully."""
        mock_redis.delete.return_value = 1

        result = await cache_service.delete("user", "123")

        assert result is True
        mock_redis.delete.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_delete_cache_not_found(self, cache_service, mock_redis):
        """Test deleting value from cache that doesn't exist."""
        mock_redis.delete.return_value = 0

        result = await cache_service.delete("user", "123")

        assert result is False
        mock_redis.delete.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_invalidate_pattern_success(self, cache_service, mock_redis):
        """Test invalidating cache pattern successfully."""
        mock_redis.keys.return_value = ["user:123", "user:456"]
        mock_redis.delete.return_value = 2

        result = await cache_service.invalidate_pattern("user:*")

        assert result == 2
        mock_redis.keys.assert_called_once_with("user:*")
        mock_redis.delete.assert_called_once_with("user:123", "user:456")

    @pytest.mark.asyncio
    async def test_invalidate_pattern_no_keys(self, cache_service, mock_redis):
        """Test invalidating cache pattern with no matching keys."""
        mock_redis.keys.return_value = []

        result = await cache_service.invalidate_pattern("user:*")

        assert result == 0
        mock_redis.keys.assert_called_once_with("user:*")
        mock_redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalidate_prefix_success(self, cache_service, mock_redis):
        """Test invalidating cache prefix successfully."""
        mock_redis.keys.return_value = ["user:123", "user:456"]
        mock_redis.delete.return_value = 2

        result = await cache_service.invalidate_prefix("user")

        assert result == 2
        mock_redis.keys.assert_called_once_with("user:*")

    @pytest.mark.asyncio
    async def test_invalidate_prefix_invalid(self, cache_service):
        """Test invalidating cache prefix with invalid prefix."""
        with pytest.raises(CacheError, match="Invalid prefix"):
            await cache_service.invalidate_prefix("invalid")

    @pytest.mark.asyncio
    async def test_get_many_success(self, cache_service, mock_redis):
        """Test getting multiple values from cache successfully."""
        identifiers = ["123", "456", "789"]
        values = [
            json.dumps({"id": "123", "name": "user1"}),
            json.dumps({"id": "456", "name": "user2"}),
            None,  # cache miss
        ]
        mock_redis.mget.return_value = values

        result = await cache_service.get_many("user", identifiers)

        assert len(result) == 3
        assert result["123"] == {"id": "123", "name": "user1"}
        assert result["456"] == {"id": "456", "name": "user2"}
        assert result["789"] is None

        expected_keys = ["user:123", "user:456", "user:789"]
        mock_redis.mget.assert_called_once_with(expected_keys)

    @pytest.mark.asyncio
    async def test_set_many_success(self, cache_service, mock_redis):
        """Test setting multiple values in cache successfully."""
        data = {
            "123": {"id": "123", "name": "user1"},
            "456": {"id": "456", "name": "user2"},
        }
        mock_pipeline = AsyncMock()
        mock_redis.pipeline.return_value = mock_pipeline

        result = await cache_service.set_many("user", data, ttl=1800)

        assert result is True
        mock_redis.pipeline.assert_called_once()
        assert mock_pipeline.setex.call_count == 2

    @pytest.mark.asyncio
    async def test_exists_success(self, cache_service, mock_redis):
        """Test checking if key exists in cache."""
        mock_redis.exists.return_value = 1

        result = await cache_service.exists("user", "123")

        assert result is True
        mock_redis.exists.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_ttl_success(self, cache_service, mock_redis):
        """Test getting TTL for key."""
        mock_redis.ttl.return_value = 1800

        result = await cache_service.ttl("user", "123")

        assert result == 1800
        mock_redis.ttl.assert_called_once_with("user:123")

    @pytest.mark.asyncio
    async def test_health_check_success(self, cache_service, mock_redis):
        """Test Redis health check success."""
        mock_redis.ping.return_value = True

        result = await cache_service.health_check()

        assert result is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, cache_service, mock_redis):
        """Test Redis health check failure."""
        mock_redis.ping.side_effect = Exception("Connection failed")

        result = await cache_service.health_check()

        assert result is False


class TestCacheManager:
    """Test cache manager functionality."""

    @pytest.fixture
    def mock_cache_service(self):
        """Create mock cache service."""
        mock = MagicMock()
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.invalidate_pattern = AsyncMock()
        return mock

    @pytest.fixture
    def cache_manager(self, mock_cache_service):
        """Create cache manager with mock cache service."""
        return CacheManager(mock_cache_service)

    def test_cache_enabled_property(self, cache_manager):
        """Test cache enabled property."""
        assert cache_manager.cache_enabled is True

        cache_manager.cache_enabled = False
        assert cache_manager.cache_enabled is False

    @pytest.mark.asyncio
    async def test_get_with_fallback_cache_hit(
        self, cache_manager, mock_cache_service
    ):
        """Test get with fallback when cache hit."""
        cached_data = {"id": "123", "name": "test"}
        mock_cache_service.get.return_value = cached_data

        async def fallback_func():
            return {"id": "123", "name": "from_db"}

        result = await cache_manager.get_with_fallback(
            "user", "123", fallback_func
        )

        assert result == cached_data
        mock_cache_service.get.assert_called_once_with("user", "123")
        mock_cache_service.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_with_fallback_cache_miss(
        self, cache_manager, mock_cache_service
    ):
        """Test get with fallback when cache miss."""
        mock_cache_service.get.return_value = None

        async def fallback_func():
            return {"id": "123", "name": "from_db"}

        result = await cache_manager.get_with_fallback(
            "user", "123", fallback_func
        )

        assert result == {"id": "123", "name": "from_db"}
        mock_cache_service.get.assert_called_once_with("user", "123")
        mock_cache_service.set.assert_called_once_with(
            "user", "123", {"id": "123", "name": "from_db"}, 3600
        )

    @pytest.mark.asyncio
    async def test_get_with_fallback_cache_disabled(
        self, cache_manager, mock_cache_service
    ):
        """Test get with fallback when cache is disabled."""
        cache_manager.cache_enabled = False

        async def fallback_func():
            return {"id": "123", "name": "from_db"}

        result = await cache_manager.get_with_fallback(
            "user", "123", fallback_func
        )

        assert result == {"id": "123", "name": "from_db"}
        mock_cache_service.get.assert_not_called()
        mock_cache_service.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_with_fallback_cache_error(
        self, cache_manager, mock_cache_service
    ):
        """Test get with fallback when cache error occurs."""
        mock_cache_service.get.side_effect = CacheError("Redis error")

        async def fallback_func():
            return {"id": "123", "name": "from_db"}

        result = await cache_manager.get_with_fallback(
            "user", "123", fallback_func
        )

        assert result == {"id": "123", "name": "from_db"}
        mock_cache_service.get.assert_called_once()
        mock_cache_service.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalidate_user_data(
        self, cache_manager, mock_cache_service
    ):
        """Test invalidating user data."""
        mock_cache_service.invalidate_pattern.return_value = 3

        result = await cache_manager.invalidate_user_data("123")

        assert result == 3
        mock_cache_service.invalidate_pattern.assert_called_once_with(
            "user:123*"
        )

    @pytest.mark.asyncio
    async def test_invalidate_group_data(
        self, cache_manager, mock_cache_service
    ):
        """Test invalidating group data."""
        mock_cache_service.invalidate_pattern.return_value = 2

        result = await cache_manager.invalidate_group_data("456")

        assert result == 2
        mock_cache_service.invalidate_pattern.assert_called_once_with(
            "group:456*"
        )

    @pytest.mark.asyncio
    async def test_invalidate_parse_results(
        self, cache_manager, mock_cache_service
    ):
        """Test invalidating parse results."""
        mock_cache_service.invalidate_pattern.return_value = 1

        result = await cache_manager.invalidate_parse_results("parse_789")

        assert result == 1
        mock_cache_service.invalidate_pattern.assert_called_once_with(
            "parse:parse_789*"
        )
