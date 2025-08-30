"""
Shared test fixtures and configuration for VK API tests

This module provides common test fixtures, mock objects, and test data
that can be reused across different test files in the VK API test suite.

Fixtures:
- mock_vk_api_response: Mock VK API response data
- mock_vk_api_client: Mock VK API client
- mock_vk_api_repository: Mock repository with caching
- mock_vk_api_service: Complete mock service setup
- sample_post_data: Sample post data for testing
- sample_user_data: Sample user data for testing
- sample_group_data: Sample group data for testing
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from src.vk_api.client import VKAPIClient
from src.vk_api.models import VKAPIRepository
from src.vk_api.service import VKAPIService


@pytest.fixture
def mock_vk_api_response():
    """Mock VK API response data"""
    return {
        "response": {
            "items": [
                {
                    "id": 1,
                    "owner_id": -12345,
                    "from_id": 67890,
                    "date": 1609459200,  # 2021-01-01
                    "text": "Sample post for testing",
                    "attachments": [],
                    "comments": {"count": 5},
                    "likes": {"count": 10},
                    "reposts": {"count": 2},
                    "views": {"count": 100},
                    "is_pinned": False,
                }
            ],
            "count": 1,
        }
    }


@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "id": 123,
        "owner_id": -456,
        "from_id": 789,
        "date": 1609459200,
        "text": "Test post content",
        "attachments": [{"type": "photo", "photo": {"id": 1}}],
        "comments": {"count": 5},
        "likes": {"count": 10},
        "reposts": {"count": 2},
        "views": {"count": 100},
        "is_pinned": False,
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return [
        {
            "id": 111,
            "first_name": "John",
            "last_name": "Doe",
            "photo_100": "https://example.com/photo.jpg",
        },
        {
            "id": 222,
            "first_name": "Jane",
            "last_name": "Smith",
            "photo_100": "https://example.com/photo2.jpg",
        },
    ]


@pytest.fixture
def sample_group_data():
    """Sample group data for testing"""
    return {
        "id": 12345,
        "name": "Test Group",
        "screen_name": "testgroup",
        "description": "A test group for unit tests",
        "members_count": 1000,
        "photo_200": "https://example.com/group_photo.jpg",
        "is_closed": False,
        "type": "group",
    }


@pytest.fixture
def mock_vk_api_client():
    """Create mock VK API client"""
    client = Mock(spec=VKAPIClient)

    # Mock async methods
    client.make_request = AsyncMock()
    client.ensure_session = AsyncMock()
    client.close_session = AsyncMock()
    client.health_check = AsyncMock(return_value={"status": "healthy"})
    client.get_stats = Mock(
        return_value={
            "current_request_count": 0,
            "last_request_time": datetime.now().timestamp(),
            "time_until_reset": 60.0,
        }
    )

    return client


@pytest.fixture
def mock_vk_api_repository():
    """Create mock VK API repository"""
    repo = Mock(spec=VKAPIRepository)

    # Mock async methods
    repo.get_cached_result = AsyncMock(return_value=None)
    repo.save_cached_result = AsyncMock()
    repo.delete_cached_result = AsyncMock(return_value=True)
    repo.clear_cache = AsyncMock(return_value=10)
    repo.save_request_log = AsyncMock()
    repo.save_error_log = AsyncMock()
    repo.get_stats = AsyncMock(
        return_value={
            "cache": {"total_entries": 5, "active_entries": 5},
            "requests": {"total_requests": 100, "successful_requests": 95},
            "errors": {"total_errors": 2},
        }
    )
    repo.health_check = AsyncMock(
        return_value={
            "status": "healthy",
            "cache_entries": 5,
            "total_requests": 100,
        }
    )

    return repo


@pytest.fixture
def mock_vk_api_service(mock_vk_api_repository, mock_vk_api_client):
    """Create mock VK API service with all dependencies"""
    service = Mock(spec=VKAPIService)

    # Configure common service methods
    service.repository = mock_vk_api_repository
    service.client = mock_vk_api_client
    service.get_group_posts = AsyncMock()
    service.get_post_comments = AsyncMock()
    service.get_group_info = AsyncMock()
    service.search_groups = AsyncMock()
    service.get_user_info = AsyncMock()
    service.get_group_members = AsyncMock()
    service.get_bulk_posts = AsyncMock()
    service.get_post_by_id = AsyncMock()
    service.validate_access_token = AsyncMock()
    service.health_check = AsyncMock()
    service.get_stats = AsyncMock()

    return service


@pytest.fixture
def real_vk_api_service():
    """Create real VK API service instance for integration tests"""
    from src.vk_api.dependencies import create_vk_api_service

    # This would create a real service instance
    # In actual tests, this might need environment setup
    return create_vk_api_service()


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def cleanup_event_loop():
    """Clean up event loop after each test"""
    yield
    # Cleanup code if needed


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance tests"""

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = datetime.now(timezone.utc)

        def stop(self):
            self.end_time = datetime.now(timezone.utc)

        @property
        def duration(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return 0

    return Timer()


# Test data generators
@pytest.fixture
def generate_posts():
    """Generate test post data"""

    def _generate(count: int, group_id: int = 12345) -> List[Dict[str, Any]]:
        return [
            {
                "id": i + 1,
                "owner_id": -abs(group_id),
                "from_id": 1000 + i,
                "date": 1609459200 + i * 3600,  # One hour apart
                "text": f"Test post {i + 1}",
                "attachments": [],
                "comments": {"count": i},
                "likes": {"count": i * 2},
                "reposts": {"count": i // 2},
                "views": {"count": i * 10},
                "is_pinned": False,
            }
            for i in range(count)
        ]

    return _generate


@pytest.fixture
def generate_comments():
    """Generate test comment data"""

    def _generate(post_id: int, count: int) -> List[Dict[str, Any]]:
        return [
            {
                "id": i + 1,
                "from_id": 2000 + i,
                "date": 1609459200 + i * 300,  # 5 minutes apart
                "text": f"Comment {i + 1} on post {post_id}",
                "likes": {"count": i % 5},
            }
            for i in range(count)
        ]

    return _generate


@pytest.fixture
def generate_users():
    """Generate test user data"""

    def _generate(count: int) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1000 + i,
                "first_name": f"User{i + 1}",
                "last_name": f"Test{i + 1}",
                "photo_100": f"https://example.com/photo{i + 1}.jpg",
            }
            for i in range(count)
        ]

    return _generate


# Error simulation fixtures
@pytest.fixture
def simulate_vk_api_error():
    """Simulate VK API errors"""

    def _simulate(error_code: int, error_msg: str):
        return {"error": {"error_code": error_code, "error_msg": error_msg}}

    return _simulate


@pytest.fixture
def simulate_network_error():
    """Simulate network errors"""
    from aiohttp import ClientError

    def _simulate():
        return ClientError("Network connection failed")

    return _simulate


# Test configuration fixtures
@pytest.fixture
def test_config():
    """Test configuration data"""
    return {
        "access_token": "test_token_12345",
        "rate_limit": {"max_requests_per_second": 3, "window_seconds": 1.0},
        "limits": {
            "max_posts_per_request": 100,
            "max_comments_per_request": 100,
            "max_users_per_request": 1000,
        },
        "cache": {
            "enabled": True,
            "group_posts_ttl": 300,
            "user_info_ttl": 1800,
        },
    }


# Mock response factory
@pytest.fixture
def mock_response_factory():
    """Factory for creating mock VK API responses"""

    def _create_response(
        data_type: str, items: List[Dict], total_count: int = None
    ):
        if total_count is None:
            total_count = len(items)

        return {"response": {"items": items, "count": total_count}}

    return _create_response


# Async test utilities
@pytest.fixture
def async_delay():
    """Create async delay for testing"""

    async def _delay(seconds: float):
        await asyncio.sleep(seconds)

    return _delay


# Test data validation
@pytest.fixture
def validate_response_structure():
    """Validate response structure"""

    def _validate(response: Dict[str, Any], expected_fields: List[str]):
        """Validate that response contains expected fields"""
        for field in expected_fields:
            assert field in response, f"Missing field: {field}"

        assert "success" in response
        assert isinstance(response["success"], bool)

        if response["success"]:
            assert "data_type" in response
            assert isinstance(response["data_type"], str)

    return _validate
