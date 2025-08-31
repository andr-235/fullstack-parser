"""
Tests for VKAPIRepository

Comprehensive test suite for the VK API repository component.
Tests cover caching functionality, request logging, error logging,
statistics collection, and data persistence operations.

Test Coverage:
- Cache operations (save, retrieve, delete, cleanup)
- Request logging and statistics
- Error logging and analysis
- Cache expiration and TTL handling
- Memory management and cleanup
- Health checks and diagnostics
- Statistics aggregation and reporting

Uses:
- pytest for test framework
- pytest-asyncio for async test support
- Freezegun for time manipulation in tests
- Mock objects for database interactions
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List

from src.vk_api.models import VKAPIRepository
from src.exceptions import ValidationError


@pytest.fixture
def repository():
    """Create VKAPIRepository instance for testing"""
    return VKAPIRepository()


@pytest.fixture
def mock_db():
    """Create mock database session"""
    db = Mock()
    return db


class TestVKAPIRepositoryCache:
    """Test suite for cache operations"""

    def test_initialization(self, repository):
        """Test repository initialization"""
        assert repository.db is None
        assert isinstance(repository._cache, dict)
        assert isinstance(repository._cache_expiry, dict)

    @pytest.mark.asyncio
    async def test_save_and_retrieve_cache(self, repository):
        """Test saving and retrieving data from cache"""
        cache_key = "test:key"
        test_data = {"id": 1, "name": "test"}
        ttl_seconds = 300

        # Save to cache
        await repository.save_cached_result(cache_key, test_data, ttl_seconds)

        # Retrieve from cache
        result = await repository.get_cached_result(cache_key)

        assert result == test_data

    @pytest.mark.asyncio
    async def test_cache_expiration(self, repository):
        """Test cache expiration"""
        cache_key = "test:expired"
        test_data = {"id": 1, "name": "test"}
        ttl_seconds = 1  # 1 second TTL

        # Save to cache
        await repository.save_cached_result(cache_key, test_data, ttl_seconds)

        # Verify it's cached
        result = await repository.get_cached_result(cache_key)
        assert result == test_data

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        result = await repository.get_cached_result(cache_key)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_cached_result(self, repository):
        """Test deleting cached result"""
        cache_key = "test:delete"
        test_data = {"id": 1, "name": "test"}

        # Save to cache
        await repository.save_cached_result(cache_key, test_data, 300)

        # Verify it's cached
        result = await repository.get_cached_result(cache_key)
        assert result == test_data

        # Delete from cache
        deleted = await repository.delete_cached_result(cache_key)
        assert deleted is True

        # Verify it's deleted
        result = await repository.get_cached_result(cache_key)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_cache(self, repository):
        """Test deleting nonexistent cache entry"""
        result = await repository.delete_cached_result("nonexistent:key")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_cache(self, repository):
        """Test clearing entire cache"""
        # Add multiple entries
        entries = [
            ("key1", {"data": 1}, 300),
            ("key2", {"data": 2}, 300),
            ("key3", {"data": 3}, 300),
        ]

        for key, data, ttl in entries:
            await repository.save_cached_result(key, data, ttl)

        # Verify entries exist
        assert len(repository._cache) == 3
        assert len(repository._cache_expiry) == 3

        # Clear cache
        deleted_count = await repository.clear_cache()
        assert deleted_count == 3

        # Verify cache is empty
        assert len(repository._cache) == 0
        assert len(repository._cache_expiry) == 0

    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self, repository):
        """Test automatic cleanup of expired entries"""
        # Add entries with different TTL
        await repository.save_cached_result(
            "short", {"data": 1}, 1
        )  # 1 second
        await repository.save_cached_result(
            "long", {"data": 2}, 300
        )  # 5 minutes

        # Wait for short TTL to expire
        await asyncio.sleep(1.1)

        # Save another entry (triggers cleanup)
        await repository.save_cached_result("new", {"data": 3}, 300)

        # Short entry should be cleaned up
        result = await repository.get_cached_result("short")
        assert result is None

        # Long entry should still exist
        result = await repository.get_cached_result("long")
        assert result == {"data": 2}


class TestVKAPIRepositoryCacheStats:
    """Test suite for cache statistics"""

    @pytest.mark.asyncio
    async def test_get_cache_stats_empty(self, repository):
        """Test cache stats for empty cache"""
        stats = await repository.get_cache_stats()

        assert stats["total_entries"] == 0
        assert stats["active_entries"] == 0
        assert stats["expired_entries"] == 0
        assert stats["group_entries"] == 0
        assert stats["post_entries"] == 0
        assert stats["user_entries"] == 0
        assert stats["search_entries"] == 0

    @pytest.mark.asyncio
    async def test_get_cache_stats_with_entries(self, repository):
        """Test cache stats with various entry types"""
        # Add entries of different types
        entries = [
            ("group:123:posts:10:0", {"posts": []}, 300),
            ("post:456:comments:20:0:asc", {"comments": []}, 300),
            ("user:789:info", {"user": {}}, 300),
            ("search:groups:test:10:0", {"groups": []}, 300),
            ("group:999:info", {"group": {}}, 300),
        ]

        for key, data, ttl in entries:
            await repository.save_cached_result(key, data, ttl)

        stats = await repository.get_cache_stats()

        assert stats["total_entries"] == 5
        assert stats["active_entries"] == 5
        assert stats["expired_entries"] == 0
        assert stats["group_entries"] == 2  # group:123 and group:999
        assert stats["post_entries"] == 1
        assert stats["user_entries"] == 1
        assert stats["search_entries"] == 1

    @pytest.mark.asyncio
    async def test_get_cache_stats_with_expired(self, repository):
        """Test cache stats with expired entries"""
        # Add entries with short TTL
        await repository.save_cached_result("active", {"data": 1}, 300)
        await repository.save_cached_result("expired1", {"data": 2}, 1)
        await repository.save_cached_result("expired2", {"data": 3}, 1)

        # Wait for expiration
        await asyncio.sleep(1.1)

        stats = await repository.get_cache_stats()

        assert stats["total_entries"] == 3
        assert stats["active_entries"] == 1
        assert stats["expired_entries"] == 2


class TestVKAPIRepositoryRequestLogging:
    """Test suite for request logging"""

    @pytest.mark.asyncio
    async def test_save_request_log_success(self, repository):
        """Test saving successful request log"""
        method = "wall.get"
        params = {"owner_id": -12345, "count": 10}
        response_time = 0.5
        success = True

        await repository.save_request_log(
            method, params, response_time, success
        )

        # Verify log was saved
        assert hasattr(repository, "_request_logs")
        assert len(repository._request_logs) == 1

        log = repository._request_logs[0]
        assert log["method"] == method
        assert log["params_count"] == len(params)
        assert log["response_time"] == response_time
        assert log["success"] == success

    @pytest.mark.asyncio
    async def test_save_request_log_failure(self, repository):
        """Test saving failed request log"""
        method = "wall.get"
        params = {"owner_id": -12345}
        response_time = 2.0
        success = False
        error_message = "Rate limit exceeded"

        await repository.save_request_log(
            method, params, response_time, success, error_message
        )

        assert len(repository._request_logs) == 1

        log = repository._request_logs[0]
        assert log["method"] == method
        assert log["success"] == success
        assert log["error_message"] == error_message

    @pytest.mark.asyncio
    async def test_get_request_logs_empty(self, repository):
        """Test getting request logs when none exist"""
        logs = await repository.get_request_logs()

        assert logs == []

    @pytest.mark.asyncio
    async def test_get_request_logs_with_data(self, repository):
        """Test getting request logs with data"""
        # Add multiple logs
        for i in range(5):
            await repository.save_request_log(
                f"method{i}", {"param": i}, 0.1 * i, i % 2 == 0
            )

        logs = await repository.get_request_logs(limit=10)

        assert len(logs) == 5
        # Should be in reverse order (newest first)
        assert logs[0]["method"] == "method4"
        assert logs[-1]["method"] == "method0"

    @pytest.mark.asyncio
    async def test_get_request_logs_pagination(self, repository):
        """Test request logs pagination"""
        # Add 10 logs
        for i in range(10):
            await repository.save_request_log(f"method{i}", {}, 0.1, True)

        # Get first page
        logs_page1 = await repository.get_request_logs(limit=3, offset=0)
        assert len(logs_page1) == 3
        assert logs_page1[0]["method"] == "method9"

        # Get second page
        logs_page2 = await repository.get_request_logs(limit=3, offset=3)
        assert len(logs_page2) == 3
        assert logs_page2[0]["method"] == "method6"

    @pytest.mark.asyncio
    async def test_request_logs_limit(self, repository):
        """Test request logs storage limit"""
        # Add more than 1000 logs
        for i in range(1010):
            await repository.save_request_log(f"method{i}", {}, 0.1, True)

        # Should only keep last 1000
        assert len(repository._request_logs) == 1000
        assert (
            repository._request_logs[0]["method"] == "method10"
        )  # oldest remaining
        assert repository._request_logs[-1]["method"] == "method1009"  # newest


class TestVKAPIRepositoryErrorLogging:
    """Test suite for error logging"""

    @pytest.mark.asyncio
    async def test_save_error_log(self, repository):
        """Test saving error log"""
        method = "wall.get"
        error_code = 6
        error_message = "Too many requests per second"
        params = {"owner_id": -12345}

        await repository.save_error_log(
            method, error_code, error_message, params
        )

        assert hasattr(repository, "_error_logs")
        assert len(repository._error_logs) == 1

        error_log = repository._error_logs[0]
        assert error_log["method"] == method
        assert error_log["error_code"] == error_code
        assert error_log["error_message"] == error_message
        assert error_log["params"] == params

    @pytest.mark.asyncio
    async def test_get_error_logs_empty(self, repository):
        """Test getting error logs when none exist"""
        logs = await repository.get_error_logs()

        assert logs == []

    @pytest.mark.asyncio
    async def test_get_error_logs_with_data(self, repository):
        """Test getting error logs with data"""
        # Add error logs with different codes
        error_codes = [6, 5, 6, 10, 6]
        for i, code in enumerate(error_codes):
            await repository.save_error_log(
                f"method{i}", code, f"Error {i}", {"param": i}
            )

        logs = await repository.get_error_logs(limit=10)

        assert len(logs) == 5
        # Should be in reverse order
        assert logs[0]["method"] == "method4"
        assert logs[-1]["method"] == "method0"

    @pytest.mark.asyncio
    async def test_error_logs_limit(self, repository):
        """Test error logs storage limit"""
        # Add more than 1000 error logs
        for i in range(1010):
            await repository.save_error_log(f"method{i}", 6, f"Error {i}", {})

        # Should only keep last 1000
        assert len(repository._error_logs) == 1000


class TestVKAPIRepositoryStatistics:
    """Test suite for statistics aggregation"""

    @pytest.mark.asyncio
    async def test_get_request_stats_empty(self, repository):
        """Test request stats when no logs exist"""
        stats = await repository.get_request_stats()

        assert stats["total_requests"] == 0
        assert stats["successful_requests"] == 0
        assert stats["failed_requests"] == 0
        assert stats["avg_response_time"] == 0
        assert stats["error_rate"] == 0

    @pytest.mark.asyncio
    async def test_get_request_stats_with_data(self, repository):
        """Test request stats with various request data"""
        # Add mix of successful and failed requests
        request_data = [
            (True, 0.1),  # success, 0.1s
            (True, 0.2),  # success, 0.2s
            (False, 0.5),  # failure, 0.5s
            (True, 0.3),  # success, 0.3s
            (False, 0.1),  # failure, 0.1s
        ]

        for success, response_time in request_data:
            await repository.save_request_log(
                "test_method", {}, response_time, success
            )

        stats = await repository.get_request_stats()

        assert stats["total_requests"] == 5
        assert stats["successful_requests"] == 3
        assert stats["failed_requests"] == 2
        assert (
            abs(stats["avg_response_time"] - 0.24) < 0.01
        )  # (0.1+0.2+0.5+0.3+0.1)/5 = 1.2/5 = 0.24
        assert stats["error_rate"] == 0.4  # 2/5 = 0.4

    @pytest.mark.asyncio
    async def test_get_error_stats_empty(self, repository):
        """Test error stats when no errors exist"""
        stats = await repository.get_error_stats()

        assert stats["total_errors"] == 0
        assert stats["unique_error_codes"] == []
        assert stats["most_common_error"] is None

    @pytest.mark.asyncio
    async def test_get_error_stats_with_data(self, repository):
        """Test error stats with various error codes"""
        error_codes = [6, 5, 6, 10, 6, 5, 6]
        for code in error_codes:
            await repository.save_error_log(
                "test_method", code, f"Error {code}", {}
            )

        stats = await repository.get_error_stats()

        assert stats["total_errors"] == 7
        assert set(stats["unique_error_codes"]) == {5, 6, 10}
        assert stats["unique_error_codes"] == [5, 6, 10]  # Should be sorted

        # Error code 6 should be most common (appears 4 times)
        most_common = stats["most_common_error"]
        assert most_common[0] == 6  # error code
        assert most_common[1] == 4  # count

    @pytest.mark.asyncio
    async def test_get_stats_combined(self, repository):
        """Test combined statistics"""
        # Add some cache entries
        await repository.save_cached_result("test:key", {"data": 1}, 300)

        # Add some request logs
        await repository.save_request_log("test_method", {}, 0.1, True)

        # Add some error logs
        await repository.save_error_log("test_method", 6, "Error", {})

        stats = await repository.get_stats()

        assert "cache" in stats
        assert "requests" in stats
        assert "errors" in stats
        assert "timestamp" in stats

        assert stats["cache"]["total_entries"] == 1
        assert stats["requests"]["total_requests"] == 1
        assert stats["errors"]["total_errors"] == 1


class TestVKAPIRepositoryHealth:
    """Test suite for health checks"""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, repository):
        """Test health check when everything is working"""
        # Add some data to make it look healthy
        await repository.save_cached_result("test:key", {"data": 1}, 300)
        await repository.save_request_log("test_method", {}, 0.1, True)

        health = await repository.health_check()

        assert health["status"] == "healthy"
        assert health["cache_entries"] == 1
        assert health["total_requests"] == 1
        assert "timestamp" in health

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, repository):
        """Test health check when there are issues"""
        # Test with exception during cache stats
        with patch.object(
            repository, "get_cache_stats", side_effect=Exception("DB error")
        ):
            health = await repository.health_check()

            assert health["status"] == "unhealthy"
            assert "DB error" in health["error"]
            assert "timestamp" in health


class TestVKAPIRepositoryDatabase:
    """Test suite for database integration"""

    @pytest.mark.asyncio
    async def test_get_db_with_provided_session(self, repository, mock_db):
        """Test getting database session when provided"""
        repository.db = mock_db

        db = await repository.get_db()
        assert db == mock_db

    @pytest.mark.asyncio
    async def test_get_db_with_none_session(self, repository):
        """Test getting database session when none provided"""
        repository.db = None

        with patch("src.vk_api.models.get_db_session") as mock_get_db:
            mock_get_db.return_value = mock_db

            db = await repository.get_db()
            mock_get_db.assert_called_once()


class TestVKAPIRepositoryEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_large_cache_operations(self, repository):
        """Test cache operations with large amounts of data"""
        # Add many cache entries
        for i in range(100):
            await repository.save_cached_result(
                f"key{i}", {"data": f"value{i}"}, 300
            )

        # Verify all entries are cached
        assert len(repository._cache) == 100

        # Retrieve all entries
        for i in range(100):
            result = await repository.get_cached_result(f"key{i}")
            assert result == {"data": f"value{i}"}

        # Clear all
        deleted_count = await repository.clear_cache()
        assert deleted_count == 100

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, repository):
        """Test concurrent cache operations"""

        async def cache_worker(worker_id: int):
            for i in range(10):
                key = f"worker{worker_id}:item{i}"
                await repository.save_cached_result(
                    key, {"worker": worker_id, "item": i}, 300
                )

                result = await repository.get_cached_result(key)
                assert result == {"worker": worker_id, "item": i}

        # Run multiple workers concurrently
        tasks = [cache_worker(i) for i in range(5)]
        await asyncio.gather(*tasks)

        # Verify total entries
        assert len(repository._cache) == 50

    @pytest.mark.asyncio
    async def test_memory_cleanup_under_load(self, repository):
        """Test memory cleanup with many expired entries"""
        # Add entries with very short TTL
        for i in range(50):
            await repository.save_cached_result(f"short{i}", {"data": i}, 1)

        # Add some long-lived entries
        for i in range(10):
            await repository.save_cached_result(
                f"long{i}", {"data": f"long{i}"}, 300
            )

        # Wait for short entries to expire
        await asyncio.sleep(1.1)

        # Trigger cleanup by adding one more entry
        await repository.save_cached_result(
            "trigger", {"data": "cleanup"}, 300
        )

        # Short entries should be cleaned up
        stats = await repository.get_cache_stats()
        assert stats["active_entries"] == 11  # 10 long + 1 trigger
