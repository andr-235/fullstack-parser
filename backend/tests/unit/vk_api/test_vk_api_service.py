"""
Tests for VKAPIService

Comprehensive test suite for the main VK API service component.
Tests cover all major functionality including posts, comments, groups,
users, bulk operations, and error handling.

Test Coverage:
- Group posts retrieval with pagination
- Post comments with sorting and limits
- Group information and search
- User information retrieval
- Group members with large datasets
- Bulk operations with concurrency
- Token validation
- Health checks and statistics
- Error scenarios and edge cases

Uses:
- pytest for test framework
- pytest-asyncio for async test support
- pytest-mock for mocking dependencies
- Mock VK API responses for reliability
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List, Optional

from src.vk_api.service import VKAPIService
from src.vk_api.models import VKAPIRepository
from src.vk_api.client import VKAPIClient
from src.exceptions import (
    ValidationError,
    ServiceUnavailableError,
)
from src.vk_api.exceptions import (
    VKAPIRateLimitError,
    VKAPIAuthError,
)
from src.vk_api.config import vk_api_config


@pytest.fixture
def mock_repository():
    """Create mock repository for testing"""
    repo = Mock(spec=VKAPIRepository)

    # Mock cache methods
    repo.get_cached_result = AsyncMock(return_value=None)
    repo.save_cached_result = AsyncMock()
    repo.delete_cached_result = AsyncMock(return_value=True)
    repo.get_stats = AsyncMock(
        return_value={
            "cache": {"total_entries": 10},
            "requests": {"total_requests": 100},
            "errors": {"total_errors": 2},
        }
    )
    repo.health_check = AsyncMock(
        return_value={
            "status": "healthy",
            "cache_entries": 10,
            "total_requests": 100,
        }
    )

    return repo


@pytest.fixture
def mock_client():
    """Create mock VK API client"""
    client = Mock(spec=VKAPIClient)

    # Mock request method
    client.make_request = AsyncMock()
    client.get_stats = Mock(
        return_value={
            "current_request_count": 5,
            "last_request_time": datetime.now().timestamp(),
            "time_until_reset": 30.0,
        }
    )
    client.health_check = AsyncMock(
        return_value={
            "status": "healthy",
            "total_requests": 100,
            "successful_requests": 95,
        }
    )

    return client


@pytest.fixture
def vk_service(mock_repository, mock_client):
    """Create VKAPIService instance with mocked dependencies"""
    return VKAPIService(mock_repository, mock_client)


@pytest.fixture
def sample_vk_response():
    """Sample VK API response data"""
    return {
        "response": {
            "items": [
                {
                    "id": 1,
                    "owner_id": -12345,
                    "from_id": 67890,
                    "date": 1609459200,  # 2021-01-01
                    "text": "Sample post text",
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


class TestVKAPIServicePosts:
    """Test suite for post-related functionality"""

    @pytest.mark.asyncio
    async def test_get_group_posts_success(
        self, vk_service, mock_client, sample_vk_response
    ):
        """Test successful retrieval of group posts"""
        mock_client.make_request.return_value = sample_vk_response

        result = await vk_service.get_group_posts(
            group_id=12345, count=10, offset=0
        )

        assert result["success"] is True
        assert result["group_id"] == 12345
        assert len(result["posts"]) == 1
        assert result["posts"][0]["id"] == 1
        assert result["total_count"] == 1
        assert result["requested_count"] == 10
        assert result["offset"] == 0
        assert result["has_more"] is False

    @pytest.mark.asyncio
    async def test_get_group_posts_with_pagination(
        self, vk_service, mock_client
    ):
        """Test group posts retrieval with pagination"""
        response_data = {
            "response": {
                "items": [
                    {"id": i, "text": f"Post {i}"} for i in range(1, 101)
                ],
                "count": 200,
            }
        }
        mock_client.make_request.return_value = response_data

        result = await vk_service.get_group_posts(
            group_id=12345, count=100, offset=0
        )

        assert len(result["posts"]) == 100
        assert result["total_count"] == 200
        assert result["has_more"] is True

    @pytest.mark.asyncio
    async def test_get_group_posts_validation_error(self, vk_service):
        """Test validation error for invalid group_id"""
        with pytest.raises(ValidationError):
            await vk_service.get_group_posts(group_id=-1)

    @pytest.mark.asyncio
    async def test_get_group_posts_api_error(self, vk_service, mock_client):
        """Test handling of VK API errors"""
        mock_client.make_request.side_effect = ServiceUnavailableError(
            "VK API unavailable"
        )

        with pytest.raises(ServiceUnavailableError):
            await vk_service.get_group_posts(group_id=12345)

    @pytest.mark.asyncio
    async def test_get_post_comments_success(self, vk_service, mock_client):
        """Test successful retrieval of post comments"""
        comments_response = {
            "response": {
                "items": [
                    {
                        "id": 1,
                        "from_id": 111,
                        "date": 1609459200,
                        "text": "Great post!",
                        "likes": {"count": 2},
                    },
                    {
                        "id": 2,
                        "from_id": 222,
                        "date": 1609459260,
                        "text": "Thanks for sharing",
                        "likes": {"count": 1},
                    },
                ],
                "count": 2,
            }
        }
        mock_client.make_request.return_value = comments_response

        result = await vk_service.get_post_comments(
            group_id=12345, post_id=67890, count=10, sort="asc"
        )

        assert result["success"] is True
        assert len(result["comments"]) == 2
        assert result["total_count"] == 2
        assert result["group_id"] == 12345
        assert result["post_id"] == 67890
        assert result["sort"] == "asc"

    @pytest.mark.asyncio
    async def test_get_post_comments_sort_validation(self, vk_service):
        """Test sort parameter validation"""
        with pytest.raises(ValidationError):
            await vk_service.get_post_comments(
                group_id=12345, post_id=67890, sort="invalid"
            )


class TestVKAPIServiceGroups:
    """Test suite for group-related functionality"""

    @pytest.mark.asyncio
    async def test_get_group_info_success(self, vk_service, mock_client):
        """Test successful group information retrieval"""
        group_response = {
            "response": [
                {
                    "id": 12345,
                    "name": "Test Group",
                    "screen_name": "test_group",
                    "description": "A test group",
                    "members_count": 1000,
                    "photo_200": "https://example.com/photo.jpg",
                    "is_closed": False,
                    "type": "group",
                }
            ]
        }
        mock_client.make_request.return_value = group_response

        result = await vk_service.get_group_info(group_id=12345)

        assert result["success"] is True
        assert "group" in result
        assert result["group"]["id"] == 12345
        assert result["group"]["name"] == "Test Group"
        assert result["group"]["members_count"] == 1000
        assert result["group"]["is_closed"] is False

    @pytest.mark.asyncio
    async def test_search_groups_success(self, vk_service, mock_client):
        """Test successful group search"""
        search_response = {
            "response": {
                "items": [
                    {"id": 1, "name": "Group 1", "members_count": 100},
                    {"id": 2, "name": "Group 2", "members_count": 200},
                ],
                "count": 2,
            }
        }
        mock_client.make_request.return_value = search_response

        result = await vk_service.search_groups(query="test", count=20)

        assert result["success"] is True
        assert len(result["groups"]) == 2
        assert result["total_count"] == 2
        assert result["query"] == "test"

    @pytest.mark.asyncio
    async def test_search_groups_empty_query(self, vk_service):
        """Test validation for empty search query"""
        with pytest.raises(ValidationError):
            await vk_service.search_groups(query="")


class TestVKAPIServiceUsers:
    """Test suite for user-related functionality"""

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, vk_service, mock_client):
        """Test successful user information retrieval"""
        users_response = {
            "response": [
                {
                    "id": 12345,
                    "first_name": "John",
                    "last_name": "Doe",
                    "photo_100": "https://example.com/photo.jpg",
                }
            ]
        }
        mock_client.make_request.return_value = users_response

        result = await vk_service.get_user_info(user_ids=12345)

        assert result["success"] is True
        assert len(result["users"]) == 1
        assert result["users"][0]["id"] == 12345
        assert result["users"][0]["first_name"] == "John"
        assert result["users"][0]["last_name"] == "Doe"

    @pytest.mark.asyncio
    async def test_get_user_info_multiple_users(self, vk_service, mock_client):
        """Test retrieval of multiple users"""
        users_response = {
            "response": [
                {"id": 1, "first_name": "User", "last_name": "One"},
                {"id": 2, "first_name": "User", "last_name": "Two"},
            ]
        }
        mock_client.make_request.return_value = users_response

        result = await vk_service.get_user_info(user_ids=[1, 2])

        assert len(result["users"]) == 2
        assert result["found_count"] == 2

    @pytest.mark.asyncio
    async def test_get_user_info_empty_list(self, vk_service):
        """Test validation for empty user list"""
        with pytest.raises(ValidationError):
            await vk_service.get_user_info(user_ids=[])


class TestVKAPIServiceMembers:
    """Test suite for group members functionality"""

    @pytest.mark.asyncio
    async def test_get_group_members_success(self, vk_service, mock_client):
        """Test successful group members retrieval"""
        members_response = {
            "response": {
                "items": [
                    {"id": 1, "first_name": "Member", "last_name": "One"},
                    {"id": 2, "first_name": "Member", "last_name": "Two"},
                ],
                "count": 500,
            }
        }
        mock_client.make_request.return_value = members_response

        result = await vk_service.get_group_members(group_id=12345, count=1000)

        assert result["success"] is True
        assert len(result["members"]) == 2
        assert result["total_count"] == 500
        assert result["group_id"] == 12345
        assert result["has_more"] is True


class TestVKAPIServiceBulkOperations:
    """Test suite for bulk operations"""

    @pytest.mark.asyncio
    async def test_get_bulk_posts_success(self, vk_service, mock_client):
        """Test successful bulk posts retrieval"""
        # Mock get_post_by_id method
        post_data = {"id": 1, "owner_id": -12345, "text": "Post content"}
        vk_service.get_post_by_id = AsyncMock(return_value=post_data)

        result = await vk_service.get_bulk_posts(
            group_id=12345, post_ids=[1, 2, 3]
        )

        assert result["total_requested"] == 3
        assert result["total_found"] == 3
        assert result["group_id"] == 12345
        assert result["success_rate"] == 100.0

    @pytest.mark.asyncio
    async def test_get_bulk_posts_with_errors(self, vk_service, mock_client):
        """Test bulk posts with some failures"""

        # Mock get_post_by_id to fail for one post
        async def mock_get_post(group_id, post_id):
            if post_id == 2:
                raise ServiceUnavailableError("Post not found")
            return {"id": post_id, "text": f"Post {post_id}"}

        vk_service.get_post_by_id = AsyncMock(side_effect=mock_get_post)

        result = await vk_service.get_bulk_posts(
            group_id=12345, post_ids=[1, 2, 3]
        )

        assert result["total_requested"] == 3
        assert result["total_found"] == 2
        # Errors are now properly collected
        assert len(result["errors"]) == 1
        assert "Пост 2:" in result["errors"][0]
        assert result["success_rate"] == pytest.approx(66.7, abs=0.1)

    @pytest.mark.asyncio
    async def test_get_bulk_posts_too_many_posts(self, vk_service):
        """Test validation for too many posts in bulk operation"""
        with pytest.raises(ValidationError):
            await vk_service.get_bulk_posts(
                group_id=12345, post_ids=list(range(51))
            )


class TestVKAPIServiceTokenValidation:
    """Test suite for token validation"""

    @pytest.mark.asyncio
    async def test_validate_access_token_success(
        self, vk_service, mock_client
    ):
        """Test successful token validation"""
        token_response = {
            "response": [
                {"id": 12345, "first_name": "John", "last_name": "Doe"}
            ]
        }
        mock_client.make_request.return_value = token_response

        result = await vk_service.validate_access_token()

        assert result["valid"] is True
        assert result["user_id"] == 12345
        assert result["user_name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_validate_access_token_invalid(
        self, vk_service, mock_client
    ):
        """Test invalid token validation"""
        mock_client.make_request.side_effect = VKAPIAuthError("Invalid token")

        result = await vk_service.validate_access_token()

        assert result["valid"] is False
        assert "Invalid token" in result["error"]


class TestVKAPIServiceHealthAndStats:
    """Test suite for health checks and statistics"""

    @pytest.mark.asyncio
    async def test_health_check_success(
        self, vk_service, mock_repository, mock_client
    ):
        """Test successful health check"""
        mock_client.health_check.return_value = {"status": "healthy"}
        mock_repository.health_check.return_value = {"status": "healthy"}

        result = await vk_service.health_check()

        assert result["status"] == "healthy"
        assert "client_status" in result
        assert "repository_status" in result
        assert result["client_status"]["status"] == "healthy"
        assert result["repository_status"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_client(
        self, vk_service, mock_repository, mock_client
    ):
        """Test health check with unhealthy client"""
        mock_client.health_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
        }
        mock_repository.health_check.return_value = {"status": "healthy"}

        result = await vk_service.health_check()

        assert result["status"] == "unhealthy"
        assert "error" in result["client_status"]
        assert result["client_status"]["error"] == "Connection failed"

    @pytest.mark.asyncio
    async def test_get_stats(self, vk_service, mock_repository, mock_client):
        """Test statistics retrieval"""
        result = await vk_service.get_stats()

        assert "client_stats" in result
        assert "repository_stats" in result
        assert "cache_enabled" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_get_api_limits(self, vk_service):
        """Test API limits retrieval"""
        result = await vk_service.get_api_limits()

        assert "max_requests_per_second" in result
        assert "max_posts_per_request" in result
        assert "current_request_count" in result


class TestVKAPIServiceErrorHandling:
    """Test suite for error handling scenarios"""

    @pytest.mark.asyncio
    async def test_service_unavailable_error(self, vk_service, mock_client):
        """Test handling of service unavailable errors"""
        mock_client.make_request.side_effect = ServiceUnavailableError(
            "VK API down"
        )

        with pytest.raises(ServiceUnavailableError):
            await vk_service.get_group_posts(group_id=12345)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, vk_service, mock_client):
        """Test handling of rate limit errors"""
        mock_client.make_request.side_effect = VKAPIRateLimitError(
            wait_time=30.0
        )

        with pytest.raises(ServiceUnavailableError):
            await vk_service.get_group_posts(group_id=12345)

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, vk_service, mock_client):
        """Test handling of invalid API response"""
        mock_client.make_request.return_value = {"invalid": "response"}

        with pytest.raises(ServiceUnavailableError):
            await vk_service.get_group_posts(group_id=12345)


# Performance and resilience tests
class TestVKAPIServicePerformance:
    """Test suite for performance and resilience"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, vk_service, mock_client):
        """Test handling of concurrent requests"""
        mock_client.make_request.return_value = {
            "response": {"items": [{"id": 1, "text": "Post"}], "count": 1}
        }

        # Create multiple concurrent requests
        tasks = [
            vk_service.get_group_posts(group_id=12345, count=10)
            for _ in range(10)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        for result in results:
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, vk_service, mock_client):
        """Test handling of large datasets"""
        large_response = {
            "response": {
                "items": [{"id": i, "text": f"Post {i}"} for i in range(1000)],
                "count": 1000,
            }
        }
        mock_client.make_request.return_value = large_response

        result = await vk_service.get_group_posts(group_id=12345, count=1000)

        assert len(result["posts"]) == 1000
        assert result["total_count"] == 1000
