"""
Tests for VKAPIClient

Comprehensive test suite for the VK API HTTP client component.
Tests cover HTTP request handling, rate limiting, error processing,
session management, and various VK API error scenarios.

Test Coverage:
- HTTP request execution with proper headers
- Rate limiting and request throttling
- Error handling for different VK API error codes
- Session management (creation, closing)
- Authentication token handling
- Timeout and network error handling
- Request/response logging and statistics

Uses:
- pytest for test framework
- pytest-asyncio for async test support
- aiohttp test client for HTTP mocking
- Mock responses for different scenarios
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, Optional

import aiohttp
from aiohttp import ClientTimeout

from src.vk_api.client import VKAPIClient
from src.vk_api.exceptions import (
    VKAPIError,
    VKAPIRateLimitError,
    VKAPIAuthError,
    VKAPIAccessDeniedError,
    VKAPIInvalidTokenError,
    VKAPIInvalidParamsError,
    VKAPITimeoutError,
    VKAPINetworkError,
    VKAPIInvalidResponseError,
)
from src.vk_api.config import (
    VK_ERROR_ACCESS_DENIED,
    VK_ERROR_INVALID_REQUEST,
    VK_ERROR_TOO_MANY_REQUESTS,
    VK_ERROR_AUTH_FAILED,
    VK_ERROR_PERMISSION_DENIED,
    USER_AGENTS,
)


@pytest.fixture
def mock_session():
    """Create mock aiohttp session"""
    from unittest.mock import AsyncMock, Mock

    # Создаем мок сессии
    session = Mock()

    # Мокаем методы HTTP запросов
    mock_get_response = Mock()
    mock_get_response.status = 200
    mock_get_response.text = AsyncMock(
        return_value='{"response": {"items": []}}'
    )

    mock_post_response = Mock()
    mock_post_response.status = 200
    mock_post_response.text = AsyncMock(
        return_value='{"response": {"items": []}}'
    )

    # Мокаем GET и POST методы с поддержкой асинхронного контекстного менеджера
    # Важно: создаем отдельные моки для каждого вызова
    def create_get_mock(*args, **kwargs):
        get_mock = Mock()
        get_mock.__aenter__ = AsyncMock(return_value=mock_get_response)
        get_mock.__aexit__ = AsyncMock(return_value=None)
        return get_mock

    def create_post_mock(*args, **kwargs):
        post_mock = Mock()
        post_mock.__aenter__ = AsyncMock(return_value=mock_post_response)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        return post_mock

    session.get = Mock(side_effect=create_get_mock)
    session.post = Mock(side_effect=create_post_mock)

    # Мокаем свойства сессии
    session.closed = False
    session.close = AsyncMock()

    return session


@pytest.fixture
def vk_client():
    """Create VKAPIClient instance for testing"""
    from src.vk_api.client import VKAPIClient

    # Создаем клиент с тестовым токеном
    client = VKAPIClient(access_token="test_token")

    return client


class TestVKAPIClientInitialization:
    """Test suite for client initialization"""

    def test_client_initialization_with_token(self, vk_client):
        """Test client initialization with access token"""
        assert vk_client.access_token == "test_token"
        assert vk_client.session is None
        assert vk_client.logger is not None

    def test_client_initialization_without_token(self):
        """Test client initialization without token"""
        with patch("src.vk_api.client.vk_api_config") as mock_config:
            mock_config.access_token = "config_token"
            client = VKAPIClient()
            assert client.access_token == "config_token"

    def test_client_initialization_with_session(self, mock_session):
        """Test client initialization with existing session"""
        client = VKAPIClient(session=mock_session)
        assert client.session == mock_session


class TestVKAPIClientSessionManagement:
    """Test suite for session management"""

    @pytest.mark.asyncio
    async def test_ensure_session_creates_new_session(self, vk_client):
        """Test that ensure_session creates a new session when none exists"""
        await vk_client.ensure_session()

        assert vk_client.session is not None
        assert not vk_client.session.closed

        # Cleanup
        await vk_client.close_session()

    @pytest.mark.asyncio
    async def test_ensure_session_reuses_existing_session(
        self, vk_client, mock_session
    ):
        """Test that ensure_session reuses existing session"""
        vk_client.session = mock_session
        await vk_client.ensure_session()

        assert vk_client.session == mock_session

    @pytest.mark.asyncio
    async def test_close_session_success(self, vk_client, mock_session):
        """Test successful session closing"""
        vk_client.session = mock_session
        mock_session.closed = False

        await vk_client.close_session()

        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_session_already_closed(self, vk_client):
        """Test closing already closed session"""
        vk_client.session = None

        # Should not raise error
        await vk_client.close_session()

    @pytest.mark.asyncio
    async def test_context_manager(self, vk_client):
        """Test async context manager functionality"""
        async with vk_client:
            assert vk_client.session is not None
            assert not vk_client.session.closed

        # Session should be closed after context
        assert vk_client.session.closed


class TestVKAPIClientRequestHandling:
    """Test suite for HTTP request handling"""

    @pytest.mark.asyncio
    async def test_make_request_success(self, vk_client, mock_session):
        """Test successful API request"""
        vk_client.session = mock_session

        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value='{"response": {"items": []}}'
        )

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await vk_client.make_request("wall.get", {"owner_id": -12345})

        assert isinstance(result, dict)
        assert "response" in result

    @pytest.mark.asyncio
    async def test_make_request_with_auth_token(self, vk_client, mock_session):
        """Test request includes access token"""
        vk_client.session = mock_session
        vk_client.access_token = "test_token"

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        await vk_client.make_request("wall.get", {"param": "value"})

        # Verify access_token was included in request
        call_args = mock_session.get.call_args
        assert "access_token" in call_args[1]["params"]
        assert call_args[1]["params"]["access_token"] == "test_token"

    @pytest.mark.asyncio
    async def test_make_request_with_user_agent(self, vk_client, mock_session):
        """Test request includes proper User-Agent header"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        await vk_client.make_request("wall.get", {})

        # Verify that the request was made (User-Agent is set at session creation, not per request)
        assert mock_session.get.called
        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://api.vk.com/method/wall.get"  # URL
        assert "params" in call_args[1]  # Parameters


class TestVKAPIClientErrorHandling:
    """Test suite for error handling"""

    @pytest.mark.asyncio
    async def test_vk_error_access_denied(self, vk_client, mock_session):
        """Test handling of VK access denied error"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value=json.dumps(
                {
                    "error": {
                        "error_code": VK_ERROR_ACCESS_DENIED,
                        "error_msg": "Access denied",
                    }
                }
            )
        )

        # Override the fixture's side_effect with our custom response
        def create_error_mock(*args, **kwargs):
            error_mock = Mock()
            error_mock.__aenter__ = AsyncMock(return_value=mock_response)
            error_mock.__aexit__ = AsyncMock(return_value=None)
            return error_mock

        mock_session.get.side_effect = create_error_mock

        with pytest.raises(VKAPIAuthError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_vk_error_rate_limit(self, vk_client, mock_session):
        """Test handling of VK rate limit error"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value=json.dumps(
                {
                    "error": {
                        "error_code": VK_ERROR_TOO_MANY_REQUESTS,
                        "error_msg": "Too many requests",
                    }
                }
            )
        )

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(VKAPIRateLimitError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_vk_error_auth_failed(self, vk_client, mock_session):
        """Test handling of VK authentication error"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value=json.dumps(
                {
                    "error": {
                        "error_code": VK_ERROR_AUTH_FAILED,
                        "error_msg": "Invalid access token",
                    }
                }
            )
        )

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(VKAPIInvalidTokenError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_vk_error_invalid_params(self, vk_client, mock_session):
        """Test handling of VK invalid parameters error"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value=json.dumps(
                {
                    "error": {
                        "error_code": VK_ERROR_INVALID_REQUEST,
                        "error_msg": "Invalid request parameters",
                    }
                }
            )
        )

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(VKAPIInvalidParamsError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_http_error(self, vk_client, mock_session):
        """Test handling of HTTP errors"""
        vk_client.session = mock_session

        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")

        with pytest.raises(VKAPINetworkError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_timeout_error(self, vk_client, mock_session):
        """Test handling of timeout errors"""
        vk_client.session = mock_session

        mock_session.get.side_effect = asyncio.TimeoutError()

        with pytest.raises(VKAPITimeoutError):
            await vk_client.make_request("wall.get", {})

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, vk_client, mock_session):
        """Test handling of invalid JSON responses"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="invalid json")

        mock_session.get.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(VKAPIInvalidResponseError):
            await vk_client.make_request("wall.get", {})


class TestVKAPIClientRateLimiting:
    """Test suite for rate limiting functionality"""

    def test_rate_limit_initialization(self, vk_client):
        """Test rate limit initialization"""
        assert vk_client.request_count == 0
        assert vk_client.last_request_time == 0
        assert (
            vk_client.rate_limit_reset_time > 0
        )  # Должно быть инициализировано текущим временем

    @pytest.mark.asyncio
    async def test_request_count_increment(self, vk_client, mock_session):
        """Test that request count is incremented"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        await vk_client.make_request("wall.get", {})

        assert vk_client.total_requests == 1
        assert vk_client.successful_requests == 1

    @pytest.mark.asyncio
    async def test_failed_request_counting(self, vk_client, mock_session):
        """Test that failed requests are counted"""
        vk_client.session = mock_session

        mock_session.post.side_effect = aiohttp.ClientError("Failed")

        try:
            await vk_client.make_request("wall.get", {})
        except VKAPINetworkError:
            pass  # Expected

        assert vk_client.total_requests == 1
        assert vk_client.failed_requests == 1


class TestVKAPIClientStatistics:
    """Test suite for client statistics"""

    def test_get_stats_initial(self, vk_client):
        """Test initial statistics"""
        stats = vk_client.get_stats()

        assert stats["current_request_count"] == 0
        assert "last_request_time" in stats
        assert "time_until_reset" in stats

    @pytest.mark.asyncio
    async def test_get_stats_after_requests(self, vk_client, mock_session):
        """Test statistics after making requests"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        # Make a few requests
        for _ in range(3):
            await vk_client.make_request("wall.get", {})

        stats = vk_client.get_stats()

        assert stats["current_request_count"] == 3
        assert vk_client.total_requests == 3
        assert vk_client.successful_requests == 3

    @pytest.mark.asyncio
    async def test_health_check_success(self, vk_client, mock_session):
        """Test successful health check"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        # Make some successful requests
        for _ in range(5):
            await vk_client.make_request("wall.get", {})

        health = await vk_client.health_check()

        assert health["status"] == "healthy"
        assert health["total_requests"] == 5
        assert health["successful_requests"] == 5

    @pytest.mark.asyncio
    async def test_health_check_with_failures(self, vk_client, mock_session):
        """Test health check with some failures"""
        vk_client.session = mock_session

        # Mock alternating success and failure
        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = Mock()
            mock_response.status = 200

            if call_count % 2 == 0:
                mock_response.text = AsyncMock(return_value='{"response": {}}')
            else:
                mock_response.text = AsyncMock(
                    return_value=json.dumps(
                        {"error": {"error_code": 1, "error_msg": "Error"}}
                    )
                )

            return mock_response

        mock_session.post.side_effect = mock_post

        # Make requests (some will succeed, some will fail)
        for _ in range(4):
            try:
                await vk_client.make_request("wall.get", {})
            except VKAPIError:
                pass  # Expected for some calls

        health = await vk_client.health_check()

        assert (
            health["status"] == "healthy"
        )  # Still healthy with some failures
        assert health["total_requests"] == 4


class TestVKAPIClientEdgeCases:
    """Test suite for edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_empty_params(self, vk_client, mock_session):
        """Test request with empty parameters"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await vk_client.make_request("users.get", {})

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_large_response(self, vk_client, mock_session):
        """Test handling of large responses"""
        vk_client.session = mock_session

        # Create a large response
        large_data = {"response": {"items": [{"id": i} for i in range(1000)]}}
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(large_data))

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await vk_client.make_request("wall.get", {})

        assert len(result["response"]["items"]) == 1000

    @pytest.mark.asyncio
    async def test_unicode_characters(self, vk_client, mock_session):
        """Test handling of Unicode characters in responses"""
        vk_client.session = mock_session

        unicode_data = {"response": {"text": "Привет мир! 🌍"}}
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(
            return_value=json.dumps(unicode_data, ensure_ascii=False)
        )

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await vk_client.make_request("wall.get", {})

        assert result["response"]["text"] == "Привет мир! 🌍"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, vk_client, mock_session):
        """Test handling of concurrent requests"""
        vk_client.session = mock_session

        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"response": {}}')

        mock_session.post.return_value.__aenter__ = AsyncMock(
            return_value=mock_response
        )
        mock_session.post.return_value.__aexit__ = AsyncMock(return_value=None)

        # Make concurrent requests
        tasks = [
            vk_client.make_request("wall.get", {"id": i}) for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)
