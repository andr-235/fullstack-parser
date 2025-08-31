"""
Tests for Base Functionality and Decorators

Comprehensive test suite for base classes, decorators, and utility functions
in the VK API module. Tests cover validation, caching, rate limiting,
circuit breaker patterns, and other core functionality.

Test Coverage:
- Parameter validation decorators
- Caching decorators with TTL
- Circuit breaker functionality
- Rate limiting decorators
- Timeout handling
- Retry mechanisms
- Logging decorators
- Base service class functionality

Uses:
- pytest for test framework
- pytest-asyncio for async test support
- pytest-mock for mocking dependencies
- Freezegun for time manipulation
"""

import pytest
import asyncio
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch, call
from typing import Dict, Any, Optional

from src.vk_api.base import (
    BaseVKAPIService,
    validate_id,
    validate_count,
    cached,
    log_request,
    circuit_breaker,
    rate_limit,
    timeout,
    retry,
    CircuitBreakerState,
    CircuitBreakerConfig,
    RateLimiterConfig,
    RateLimitStrategy,
)
from src.vk_api.models import VKAPIRepository
from src.vk_api.client import VKAPIClient
from src.exceptions import ValidationError, ServiceUnavailableError


@pytest.fixture
def mock_repository():
    """Create mock repository"""
    repo = Mock(spec=VKAPIRepository)
    repo.get_cached_result = AsyncMock(return_value=None)
    repo.save_cached_result = AsyncMock()
    repo.save_request_log = AsyncMock()
    repo.save_error_log = AsyncMock()
    return repo


@pytest.fixture
def mock_client():
    """Create mock client"""
    client = Mock(spec=VKAPIClient)
    client.make_request = AsyncMock(return_value={"response": {}})
    return client


@pytest.fixture
def base_service(mock_repository, mock_client):
    """Create BaseVKAPIService instance"""
    return BaseVKAPIService(mock_repository, mock_client)


class TestParameterValidation:
    """Test suite for parameter validation decorators"""

    def test_validate_id_positive_integer(self):
        """Test validate_id with positive integer"""

        @validate_id("test_param")
        def test_func(test_param: int):
            return test_param

        result = test_func(12345)
        assert result == 12345

    def test_validate_id_negative_integer(self):
        """Test validate_id with negative integer (should pass)"""

        @validate_id("test_param")
        def test_func(test_param: int):
            return test_param

        result = test_func(-12345)
        assert result == -12345

    def test_validate_id_zero(self):
        """Test validate_id with zero (should fail)"""

        @validate_id("test_param")
        def test_func(test_param: int):
            return test_param

        with pytest.raises(ValidationError):
            test_func(0)

    def test_validate_id_string(self):
        """Test validate_id with string (should fail)"""

        @validate_id("test_param")
        def test_func(test_param: int):
            return test_param

        with pytest.raises(ValidationError):
            test_func("123")

    def test_validate_count_valid(self):
        """Test validate_count with valid count"""

        @validate_count(100)
        def test_func(count: int):
            return count

        result = test_func(50)
        assert result == 50

    def test_validate_count_too_large(self):
        """Test validate_count with count exceeding maximum"""

        @validate_count(100)
        def test_func(count: int):
            return count

        with pytest.raises(ValidationError):
            test_func(150)

    def test_validate_count_zero(self):
        """Test validate_count with zero (should fail)"""

        @validate_count(100)
        def test_func(count: int):
            return count

        with pytest.raises(ValidationError):
            test_func(0)

    def test_validate_count_negative(self):
        """Test validate_count with negative value (should fail)"""

        @validate_count(100)
        def test_func(count: int):
            return count

        with pytest.raises(ValidationError):
            test_func(-5)


class TestCachingDecorator:
    """Test suite for caching decorator"""

    @pytest.mark.asyncio
    async def test_cached_decorator_hit(self, mock_repository):
        """Test caching decorator with cache hit"""
        mock_repository.get_cached_result.return_value = {"cached": "data"}

        @cached("test:{param}", 300)
        async def test_func(param: str):
            return {"fresh": "data"}

        result = await test_func("value")

        assert result == {"cached": "data"}
        mock_repository.get_cached_result.assert_called_once_with("test:value")
        mock_repository.save_cached_result.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_decorator_miss(self, mock_repository):
        """Test caching decorator with cache miss"""
        mock_repository.get_cached_result.return_value = None

        @cached("test:{param}", 300)
        async def test_func(param: str):
            return {"fresh": "data"}

        result = await test_func("value")

        assert result == {"fresh": "data"}
        mock_repository.get_cached_result.assert_called_once_with("test:value")
        mock_repository.save_cached_result.assert_called_once_with(
            "test:value", {"fresh": "data"}, 300
        )

    @pytest.mark.asyncio
    async def test_cached_decorator_with_exception(self, mock_repository):
        """Test caching decorator when function raises exception"""
        mock_repository.get_cached_result.return_value = None

        @cached("test:{param}", 300)
        async def test_func(param: str):
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await test_func("value")

        # Should not cache error results
        mock_repository.save_cached_result.assert_not_called()


class TestLoggingDecorator:
    """Test suite for logging decorator"""

    @pytest.mark.asyncio
    async def test_log_request_success(self, mock_repository, mock_client):
        """Test logging decorator with successful request"""
        mock_client.make_request.return_value = {"response": {"data": "test"}}

        # Делаем mock_repository доступным в глобальной области видимости теста
        # чтобы декоратор log_request мог его найти через inspect
        import builtins

        builtins.mock_repository = mock_repository

        @log_request("test.method")
        async def test_func():
            return await mock_client.make_request("test.method", {})

        result = await test_func()

        assert result == {"response": {"data": "test"}}
        mock_repository.save_request_log.assert_called_once()
        call_args = mock_repository.save_request_log.call_args
        assert call_args[0][0] == "test.method"  # method
        assert call_args[0][3] == True  # success

    @pytest.mark.asyncio
    async def test_log_request_failure(self, mock_repository, mock_client):
        """Test logging decorator with failed request"""
        mock_client.make_request.side_effect = ValueError("Test error")

        # Делаем mock_repository доступным в глобальной области видимости теста
        # чтобы декоратор log_request мог его найти через inspect
        import builtins

        builtins.mock_repository = mock_repository

        @log_request("test.method")
        async def test_func():
            return await mock_client.make_request("test.method", {})

        with pytest.raises(ValueError):
            await test_func()

        # Для ошибок декоратор вызывает save_error_log, а не save_request_log
        mock_repository.save_error_log.assert_called_once()
        call_args = mock_repository.save_error_log.call_args
        assert call_args[0][0] == "test.method"  # method
        assert call_args[0][1] == 0  # error_code (0 для ValueError)
        assert "Test error" in call_args[0][2]  # error_message


class TestCircuitBreakerDecorator:
    """Test suite for circuit breaker decorator"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self, mock_repository):
        """Test circuit breaker in closed state (normal operation)"""

        @circuit_breaker()
        async def test_func():
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_state(self, mock_repository):
        """Test circuit breaker opening after failures"""
        call_count = 0

        @circuit_breaker(failure_threshold=2, recovery_timeout=1.0)
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ServiceUnavailableError("Service down")

        # First failure
        with pytest.raises(ServiceUnavailableError):
            await test_func()

        # Second failure - should open circuit
        with pytest.raises(ServiceUnavailableError):
            await test_func()

        # Third call - should be blocked by circuit breaker
        with pytest.raises(ServiceUnavailableError):
            await test_func()

        assert call_count == 2  # Function should only be called twice

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, mock_repository):
        """Test circuit breaker recovery after timeout"""
        call_count = 0

        @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ServiceUnavailableError("Service down")
            return "recovered"

        # Fail twice to open circuit
        with pytest.raises(ServiceUnavailableError):
            await test_func()
        with pytest.raises(ServiceUnavailableError):
            await test_func()

        # Wait for recovery timeout
        await asyncio.sleep(0.2)

        # Next call should succeed (half-open -> closed)
        result = await test_func()
        assert result == "recovered"
        assert call_count == 3


class TestRateLimitDecorator:
    """Test suite for rate limiting decorator"""

    @pytest.mark.asyncio
    async def test_rate_limit_within_limits(self):
        """Test rate limiting within allowed limits"""

        @rate_limit(max_calls=3, time_window=1.0)
        async def test_func():
            return "success"

        # Make calls within limits
        for _ in range(3):
            result = await test_func()
            assert result == "success"

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limiting when limit exceeded"""

        @rate_limit(max_calls=2, time_window=0.5)
        async def test_func():
            return "success"

        # Use up the limit
        await test_func()
        await test_func()

        # Next call should be rate limited
        start_time = time.time()
        with pytest.raises(ServiceUnavailableError):
            await test_func()
        elapsed = time.time() - start_time

        # Should wait at least the time window
        assert elapsed >= 0.5

    @pytest.mark.asyncio
    async def test_rate_limit_reset_after_window(self):
        """Test rate limit reset after time window"""

        @rate_limit(max_calls=1, time_window=0.1)
        async def test_func():
            return "success"

        # Use the limit
        await test_func()

        # Wait for reset
        await asyncio.sleep(0.15)

        # Should work again
        result = await test_func()
        assert result == "success"


class TestTimeoutDecorator:
    """Test suite for timeout decorator"""

    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """Test timeout decorator with successful completion"""

        @timeout(1.0)
        async def test_func():
            await asyncio.sleep(0.1)
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Test timeout decorator when timeout exceeded"""

        @timeout(0.1)
        async def test_func():
            await asyncio.sleep(0.2)  # Longer than timeout
            return "success"

        with pytest.raises(ServiceUnavailableError):
            await test_func()


class TestRetryDecorator:
    """Test suite for retry decorator"""

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test retry decorator with success on first attempt"""

        @retry(max_attempts=3)
        async def test_func():
            return "success"

        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test retry decorator with success after failures"""
        attempt_count = 0

        @retry(max_attempts=3, backoff_factor=0.1)
        async def test_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary failure")
            return "success"

        result = await test_func()
        assert result == "success"
        assert attempt_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test retry decorator when all attempts fail"""

        @retry(max_attempts=2, backoff_factor=0.1)
        async def test_func():
            raise ValueError("Persistent failure")

        with pytest.raises(ValueError):
            await test_func()


class TestDecoratorCombinations:
    """Test suite for decorator combinations"""

    @pytest.mark.asyncio
    async def test_multiple_decorators_order(
        self, mock_repository, mock_client
    ):
        """Test multiple decorators applied in correct order"""
        call_order = []

        # Mock to track call order
        original_make_request = mock_client.make_request

        async def tracked_make_request(*args, **kwargs):
            call_order.append("client_call")
            return await original_make_request(*args, **kwargs)

        mock_client.make_request = tracked_make_request

        @validate_id("param")
        @cached("test:{param}", 300)
        @log_request("test.method")
        async def test_func(param: int):
            call_order.append("function_body")
            return {"result": param}

        result = await test_func(123)

        # Verify correct execution order
        assert call_order == ["function_body"]
        assert result == {"result": 123}

    @pytest.mark.asyncio
    async def test_decorator_error_propagation(self, mock_repository):
        """Test error propagation through decorators"""

        @validate_id("param")
        @cached("test:{param}", 300)
        async def test_func(param: int):
            raise ValueError("Function error")

        with pytest.raises(ValueError):
            await test_func(123)


class TestBaseServiceClass:
    """Test suite for BaseVKAPIService class"""

    def test_base_service_initialization(
        self, base_service, mock_repository, mock_client
    ):
        """Test BaseVKAPIService initialization"""
        assert base_service.repository == mock_repository
        assert base_service.client == mock_client

    @pytest.mark.asyncio
    async def test_base_service_health_check(
        self, base_service, mock_repository, mock_client
    ):
        """Test base service health check"""
        mock_repository.health_check.return_value = {"status": "healthy"}
        mock_client.health_check.return_value = {"status": "healthy"}

        result = await base_service.health_check()

        assert "overall_status" in result
        assert "client_status" in result
        assert "repository_status" in result

    @pytest.mark.asyncio
    async def test_base_service_resilience_stats(self, base_service):
        """Test base service resilience statistics"""
        result = await base_service.get_resilience_stats()

        # Should return circuit breaker and rate limiter stats
        assert isinstance(result, dict)
        assert "circuit_breakers" in result
        assert "rate_limiters" in result


class TestCircuitBreakerConfig:
    """Test suite for CircuitBreakerConfig"""

    def test_circuit_breaker_config_defaults(self):
        """Test circuit breaker config with defaults"""
        config = CircuitBreakerConfig()

        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.success_threshold == 3
        assert config.timeout == 30.0

    def test_circuit_breaker_config_custom(self):
        """Test circuit breaker config with custom values"""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=120.0,
            success_threshold=5,
            timeout=60.0,
        )

        assert config.failure_threshold == 10
        assert config.recovery_timeout == 120.0
        assert config.success_threshold == 5
        assert config.timeout == 60.0


class TestRateLimiterConfig:
    """Test suite for RateLimiterConfig"""

    def test_rate_limiter_config_defaults(self):
        """Test rate limiter config with defaults"""
        config = RateLimiterConfig()

        assert config.max_calls == 10
        assert config.time_window == 60.0
        assert config.strategy == RateLimitStrategy.FIXED_WINDOW

    def test_rate_limiter_config_custom(self):
        """Test rate limiter config with custom values"""
        config = RateLimiterConfig(
            max_calls=20, time_window=30.0, strategy="sliding_window"
        )

        assert config.max_calls == 20
        assert config.time_window == 30.0
        assert config.strategy == "sliding_window"


class TestCircuitBreakerState:
    """Test suite for CircuitBreakerState enum"""

    def test_circuit_breaker_states(self):
        """Test circuit breaker state values"""
        assert CircuitBreakerState.CLOSED.value == "closed"
        assert CircuitBreakerState.OPEN.value == "open"
        assert CircuitBreakerState.HALF_OPEN.value == "half_open"

    def test_circuit_breaker_state_names(self):
        """Test circuit breaker state names"""
        assert CircuitBreakerState.CLOSED.name == "CLOSED"
        assert CircuitBreakerState.OPEN.name == "OPEN"
        assert CircuitBreakerState.HALF_OPEN.name == "HALF_OPEN"
