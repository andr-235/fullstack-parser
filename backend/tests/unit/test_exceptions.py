"""
Unit tests for custom exceptions.
"""

from fastapi import status

from app.core.exceptions import (
    BaseAPIException,
    CacheError,
    DatabaseError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
    VKAPIError,
)


class TestBaseAPIException:
    """Test base API exception."""

    def test_base_exception_creation(self):
        """Test base exception creation with all parameters."""
        exc = BaseAPIException(
            status_code=400,
            detail="Test error",
            error_code="TEST_ERROR",
            context={"test": "value"},
        )

        assert exc.status_code == 400
        assert exc.detail == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.context == {"test": "value"}

    def test_base_exception_default_context(self):
        """Test base exception with default context."""
        exc = BaseAPIException(status_code=500, detail="Test error")

        assert exc.context == {}


class TestVKAPIError:
    """Test VK API exception."""

    def test_vk_api_error_creation(self):
        """Test VK API error creation."""
        exc = VKAPIError(
            detail="Rate limit exceeded",
            vk_error_code=29,
            context={"group_id": "123"},
        )

        assert exc.status_code == status.HTTP_502_BAD_GATEWAY
        assert "VK API Error: Rate limit exceeded" in exc.detail
        assert exc.error_code == "VK_API_ERROR"
        assert exc.vk_error_code == 29
        assert exc.context == {"group_id": "123"}

    def test_vk_api_error_defaults(self):
        """Test VK API error with defaults."""
        exc = VKAPIError("Network error")

        assert exc.status_code == status.HTTP_502_BAD_GATEWAY
        assert "VK API Error: Network error" in exc.detail
        assert exc.error_code == "VK_API_ERROR"
        assert exc.vk_error_code is None


class TestDatabaseError:
    """Test database exception."""

    def test_database_error_creation(self):
        """Test database error creation."""
        exc = DatabaseError(
            detail="Connection failed",
            db_error="connection_timeout",
            context={"query": "SELECT * FROM users"},
        )

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database Error: Connection failed" in exc.detail
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.db_error == "connection_timeout"
        assert exc.context == {"query": "SELECT * FROM users"}


class TestCacheError:
    """Test cache exception."""

    def test_cache_error_creation(self):
        """Test cache error creation."""
        exc = CacheError(
            detail="Redis connection failed",
            cache_key="user:123",
            context={"operation": "get"},
        )

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Cache Error: Redis connection failed" in exc.detail
        assert exc.error_code == "CACHE_ERROR"
        assert exc.cache_key == "user:123"
        assert exc.context == {"operation": "get"}


class TestValidationError:
    """Test validation exception."""

    def test_validation_error_creation(self):
        """Test validation error creation."""
        exc = ValidationError(
            detail="Invalid user ID",
            field="user_id",
            value="invalid_id",
            context={"request_data": {"user_id": "invalid_id"}},
        )

        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "Validation Error: Invalid user ID" in exc.detail
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field == "user_id"
        assert exc.value == "invalid_id"
        assert exc.context == {"request_data": {"user_id": "invalid_id"}}


class TestRateLimitError:
    """Test rate limit exception."""

    def test_rate_limit_error_creation(self):
        """Test rate limit error creation."""
        exc = RateLimitError(
            detail="Too many requests",
            retry_after=60,
            context={"endpoint": "/api/v1/vk/comments"},
        )

        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate Limit Error: Too many requests" in exc.detail
        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.retry_after == 60
        assert exc.context == {"endpoint": "/api/v1/vk/comments"}


class TestServiceUnavailableError:
    """Test service unavailable exception."""

    def test_service_unavailable_error_creation(self):
        """Test service unavailable error creation."""
        exc = ServiceUnavailableError(
            detail="VK API is down",
            service="vk_api",
            context={"health_check": "failed"},
        )

        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Service Unavailable: VK API is down" in exc.detail
        assert exc.error_code == "SERVICE_UNAVAILABLE"
        assert exc.service == "vk_api"
        assert exc.context == {"health_check": "failed"}
