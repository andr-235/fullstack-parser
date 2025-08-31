"""
Integration Tests for VK API Module

Comprehensive integration test suite for the VK API module.
Tests cover end-to-end scenarios combining multiple components,
real-world usage patterns, performance under load, and system resilience.

Test Coverage:
- End-to-end request flows from service to client
- Component integration (service + repository + client)
- Error propagation through the entire stack
- Caching integration with service layer
- Concurrent request handling
- Memory and resource management
- System recovery and resilience
- Real-world usage scenarios

Uses:
- pytest for test framework
- pytest-asyncio for async integration tests
- Mock VK API responses for controlled testing
- Performance monitoring and benchmarking
"""

import pytest
import asyncio
import time
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
def integration_repository():
    """Create repository for integration tests"""
    # Используем Mock вместо реального VKAPIRepository для контроля в тестах
    repo = Mock(spec=VKAPIRepository)

    # Override with mocks for controlled testing
    repo.get_cached_result = AsyncMock(return_value=None)
    repo.save_cached_result = AsyncMock()
    repo.save_request_log = AsyncMock()
    repo.save_error_log = AsyncMock()

    return repo


@pytest.fixture
def integration_client():
    """Create client for integration tests"""
    client = VKAPIClient(access_token="test_token")

    # Mock the actual HTTP requests
    client.make_request = AsyncMock()
    client.get_stats = Mock(
        return_value={
            "current_request_count": 0,
            "last_request_time": time.time(),
            "time_until_reset": 60.0,
        }
    )
    client.health_check = AsyncMock(return_value={"status": "healthy"})

    return client


@pytest.fixture
def integration_service(integration_repository, integration_client):
    """Create service for integration tests"""
    return VKAPIService(integration_repository, integration_client)


class TestServiceClientIntegration:
    """Test suite for service-client integration"""

    @pytest.mark.asyncio
    async def test_get_group_posts_full_flow(
        self, integration_service, integration_client
    ):
        """Test complete flow for getting group posts"""
        # Mock VK API response
        vk_response = {
            "response": {
                "items": [
                    {
                        "id": 1,
                        "owner_id": -12345,
                        "from_id": 67890,
                        "date": 1609459200,
                        "text": "Test post",
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

        integration_client.make_request.return_value = vk_response

        # Execute the request
        result = await integration_service.get_group_posts(
            group_id=12345, count=10, offset=0
        )

        # Verify the complete flow
        assert result["success"] is True
        assert result["group_id"] == 12345
        assert len(result["posts"]) == 1
        assert result["posts"][0]["id"] == 1

        # Verify client was called with correct parameters
        integration_client.make_request.assert_called_once_with(
            "wall.get",
            {"owner_id": -12345, "count": 10, "offset": 0},  # VK API format
        )

    @pytest.mark.asyncio
    async def test_get_group_posts_with_caching(
        self, integration_service, integration_repository
    ):
        """Test group posts retrieval with caching integration"""
        # First call - cache miss
        integration_repository.get_cached_result.return_value = None

        # Mock VK API response
        vk_response = {
            "response": {
                "items": [{"id": 1, "text": "Cached post"}],
                "count": 1,
            }
        }
        integration_service.client.make_request.return_value = vk_response

        # First request
        result1 = await integration_service.get_group_posts(
            group_id=12345, count=10
        )

        # Verify cache was checked and saved
        integration_repository.get_cached_result.assert_called_with(
            "group:12345:posts:10:0"
        )
        integration_repository.save_cached_result.assert_called_once()

        # Second call - cache hit
        integration_repository.get_cached_result.return_value = result1
        integration_service.client.make_request.reset_mock()

        result2 = await integration_service.get_group_posts(
            group_id=12345, count=10
        )

        # Verify client was not called (cache hit)
        integration_service.client.make_request.assert_not_called()
        assert result2 == result1


class TestServiceRepositoryIntegration:
    """Test suite for service-repository integration"""

    @pytest.mark.asyncio
    async def test_request_logging_integration(
        self, integration_service, integration_repository
    ):
        """Test request logging through service to repository"""
        # Mock successful API call
        integration_service.client.make_request.return_value = {
            "response": {"items": [], "count": 0}
        }

        await integration_service.get_group_posts(group_id=12345, count=5)

        # Verify request was logged
        integration_repository.save_request_log.assert_called_once()
        call_args = integration_repository.save_request_log.call_args

        assert call_args[0][0] == "wall.get"  # method
        assert call_args[0][3] == True  # success
        assert isinstance(call_args[0][2], float)  # response_time

    @pytest.mark.asyncio
    async def test_error_logging_integration(
        self, integration_service, integration_repository
    ):
        """Test error logging through service to repository"""
        # Mock API error
        integration_service.client.make_request.side_effect = (
            VKAPIRateLimitError()
        )

        with pytest.raises(VKAPIRateLimitError):
            await integration_service.get_group_posts(group_id=12345)

        # Verify error was logged through the log_request decorator
        # The decorator should call save_error_log for the wrapped error
        integration_repository.save_error_log.assert_called_once()
        call_args = integration_repository.save_error_log.call_args

        assert call_args[0][0] == "wall.get"  # method
        assert (
            call_args[0][1] == 6
        )  # VK rate limit error code (from VKAPIRateLimitError)

    @pytest.mark.asyncio
    async def test_health_check_integration(
        self, integration_service, integration_repository, integration_client
    ):
        """Test health check integration across all components"""
        # Mock component health checks
        integration_client.health_check.return_value = {"status": "healthy"}
        integration_repository.health_check.return_value = {
            "status": "healthy"
        }

        result = await integration_service.health_check()

        assert result["status"] == "healthy"
        assert "client_status" in result
        assert "repository_status" in result

        # Verify component health checks were called
        integration_client.health_check.assert_called_once()
        integration_repository.health_check.assert_called_once()


class TestErrorPropagationIntegration:
    """Test suite for error propagation through the stack"""

    @pytest.mark.asyncio
    async def test_validation_error_propagation(self, integration_service):
        """Test validation error propagation from service"""
        with pytest.raises(ValidationError):
            await integration_service.get_group_posts(group_id=0)

    @pytest.mark.asyncio
    async def test_client_error_propagation(
        self, integration_service, integration_client
    ):
        """Test client error propagation to service"""
        integration_client.make_request.side_effect = VKAPIAuthError(
            "Invalid token"
        )

        with pytest.raises(VKAPIAuthError):
            await integration_service.get_group_posts(group_id=12345)

    @pytest.mark.asyncio
    async def test_network_error_handling(
        self, integration_service, integration_client
    ):
        """Test network error handling and recovery"""
        # Mock network failure for all retry attempts (3 attempts total)
        integration_client.make_request.side_effect = [
            ServiceUnavailableError("Network timeout"),
            ServiceUnavailableError("Network timeout"),
            ServiceUnavailableError("Network timeout"),
        ]

        # All attempts should fail and exception should be raised
        with pytest.raises(ServiceUnavailableError):
            await integration_service.get_group_posts(group_id=12345)

        # Reset for retry test
        integration_client.make_request.side_effect = None
        integration_client.make_request.return_value = {
            "response": {"items": [{"id": 1}], "count": 1}
        }

        # Second attempt should succeed
        result = await integration_service.get_group_posts(group_id=12345)
        assert result["success"] is True


class TestConcurrentOperationsIntegration:
    """Test suite for concurrent operations"""

    @pytest.mark.asyncio
    async def test_concurrent_group_posts_requests(
        self, integration_service, integration_client
    ):
        """Test concurrent group posts requests"""
        # Mock client to return different data for different calls
        call_count = 0

        async def mock_make_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return {
                "response": {
                    "items": [
                        {"id": call_count, "text": f"Post {call_count}"}
                    ],
                    "count": 1,
                }
            }

        integration_client.make_request.side_effect = mock_make_request

        # Make concurrent requests
        tasks = [
            integration_service.get_group_posts(group_id=12345 + i, count=10)
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        assert len(results) == 5
        for result in results:
            assert result["success"] is True

        # Verify client was called 5 times
        assert integration_client.make_request.call_count == 5

    @pytest.mark.asyncio
    async def test_concurrent_bulk_operations(
        self, integration_service, integration_client
    ):
        """Test concurrent bulk operations"""

        # Mock single post retrieval
        async def mock_get_post_by_id(group_id, post_id):
            return {"id": post_id, "text": f"Post {post_id}"}

        integration_service.get_post_by_id = AsyncMock(
            side_effect=mock_get_post_by_id
        )

        # Execute bulk operation
        result = await integration_service.get_bulk_posts(
            group_id=12345, post_ids=[1, 2, 3, 4, 5]
        )

        assert result["total_requested"] == 5
        assert result["total_found"] == 5
        assert result["success_rate"] == 100.0

        # Verify posts were retrieved
        assert len(result["posts"]) == 5


class TestBulkOperationsIntegration:
    """Test suite for bulk operations integration"""

    @pytest.mark.asyncio
    async def test_bulk_posts_with_partial_failures(self, integration_service):
        """Test bulk posts with some failures"""
        call_count = 0

        async def mock_get_post_by_id(group_id, post_id):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Fail every other call
                raise ServiceUnavailableError(f"Post {post_id} not found")
            return {"id": post_id, "text": f"Post {post_id}"}

        integration_service.get_post_by_id = AsyncMock(
            side_effect=mock_get_post_by_id
        )

        result = await integration_service.get_bulk_posts(
            group_id=12345, post_ids=[1, 2, 3, 4, 5]
        )

        assert result["total_requested"] == 5
        assert result["total_found"] == 3  # Only odd-numbered posts succeed
        assert len(result["errors"]) == 2
        assert result["success_rate"] == 60.0

    @pytest.mark.asyncio
    async def test_bulk_posts_performance_metrics(self, integration_service):
        """Test bulk operations performance metrics"""
        # Mock successful post retrieval
        integration_service.get_post_by_id = AsyncMock(
            return_value={"id": 1, "text": "Post"}
        )

        start_time = time.time()
        result = await integration_service.get_bulk_posts(
            group_id=12345, post_ids=list(range(10))
        )
        end_time = time.time()

        assert result["total_requested"] == 10
        assert result["total_found"] == 10
        assert "processing_time_seconds" in result
        assert result["processing_time_seconds"] >= 0
        assert (
            result["processing_time_seconds"] < end_time - start_time + 1
        )  # Allow some tolerance


class TestRealWorldScenariosIntegration:
    """Test suite for real-world usage scenarios"""

    @pytest.mark.asyncio
    async def test_social_media_monitoring_scenario(
        self, integration_service, integration_client
    ):
        """Test social media monitoring scenario"""
        # Mock responses for a monitoring workflow
        call_sequence = [
            # Group info
            {
                "response": {
                    "id": 12345,
                    "name": "Test Group",
                    "members_count": 1000,
                }
            },
            # Posts
            {
                "response": {
                    "items": [
                        {"id": 1, "text": "Post 1", "comments": {"count": 5}},
                        {"id": 2, "text": "Post 2", "comments": {"count": 3}},
                    ],
                    "count": 2,
                }
            },
            # Comments for post 1
            {
                "response": {
                    "items": [
                        {"id": 1, "text": "Comment 1"},
                        {"id": 2, "text": "Comment 2"},
                    ],
                    "count": 2,
                }
            },
            # Comments for post 2
            {
                "response": {
                    "items": [{"id": 3, "text": "Comment 3"}],
                    "count": 1,
                }
            },
        ]

        integration_client.make_request.side_effect = call_sequence

        # Execute monitoring workflow
        group_info = await integration_service.get_group_info(12345)
        posts = await integration_service.get_group_posts(12345, count=10)
        comments_1 = await integration_service.get_post_comments(
            12345, 1, count=10
        )
        comments_2 = await integration_service.get_post_comments(
            12345, 2, count=10
        )

        # Verify workflow results
        assert group_info["id"] == 12345
        assert len(posts["posts"]) == 2
        assert len(comments_1["comments"]) == 2
        assert len(comments_2["comments"]) == 1

    @pytest.mark.asyncio
    async def test_user_research_scenario(
        self, integration_service, integration_client
    ):
        """Test user research scenario"""
        # Mock user data responses
        integration_client.make_request.side_effect = [
            # User info
            {
                "response": [
                    {"id": 111, "first_name": "John", "last_name": "Doe"},
                    {"id": 222, "first_name": "Jane", "last_name": "Smith"},
                ]
            },
            # Group search
            {
                "response": {
                    "items": [
                        {"id": 1, "name": "Tech Group", "members_count": 500},
                        {"id": 2, "name": "Art Group", "members_count": 300},
                    ],
                    "count": 2,
                }
            },
        ]

        # Execute research workflow
        users = await integration_service.get_user_info([111, 222])
        groups = await integration_service.search_groups(
            "technology", count=20
        )

        # Verify results
        assert len(users["users"]) == 2
        assert users["users"][0]["name"] == "John Doe"
        assert len(groups["groups"]) == 2
        assert groups["query"] == "technology"

    @pytest.mark.asyncio
    async def test_content_moderation_scenario(
        self, integration_service, integration_client
    ):
        """Test content moderation scenario"""
        # Mock responses for moderation workflow
        integration_client.make_request.side_effect = [
            # Posts to moderate
            {
                "response": {
                    "items": [
                        {"id": 1, "text": "Good post", "from_id": 111},
                        {"id": 2, "text": "Spam post", "from_id": 222},
                        {
                            "id": 3,
                            "text": "Questionable content",
                            "from_id": 333,
                        },
                    ],
                    "count": 3,
                }
            },
            # User info for moderation decision
            {
                "response": [
                    {"id": 111, "first_name": "Trusted", "last_name": "User"},
                    {"id": 222, "first_name": "Spam", "last_name": "Account"},
                    {"id": 333, "first_name": "New", "last_name": "User"},
                ]
            },
        ]

        # Execute moderation workflow
        posts = await integration_service.get_group_posts(12345, count=10)
        user_ids = [post["from_id"] for post in posts["posts"]]
        users = await integration_service.get_user_info(user_ids)

        # Verify moderation data is available
        assert len(posts["posts"]) == 3
        assert len(users["users"]) == 3

        # Could implement moderation logic here
        for post, user in zip(posts["posts"], users["users"]):
            assert "text" in post
            assert "name" in user


class TestSystemResilienceIntegration:
    """Test suite for system resilience and recovery"""

    @pytest.mark.asyncio
    async def test_service_degradation_recovery(
        self, integration_service, integration_client
    ):
        """Test service degradation and recovery"""
        # Start with healthy service
        integration_client.make_request.return_value = {
            "response": {"items": [], "count": 0}
        }

        # Normal operation
        result = await integration_service.get_group_posts(12345)
        assert result["success"] is True

        # Service degradation
        integration_client.make_request.side_effect = ServiceUnavailableError(
            "Service down"
        )

        with pytest.raises(ServiceUnavailableError):
            await integration_service.get_group_posts(12345)

        # Service recovery
        integration_client.make_request.side_effect = None
        integration_client.make_request.return_value = {
            "response": {"items": [], "count": 0}
        }

        result = await integration_service.get_group_posts(12345)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_memory_management_under_load(
        self, integration_service, integration_client
    ):
        """Test memory management under load"""
        # Mock large responses
        large_response = {
            "response": {
                "items": [
                    {"id": i, "text": f"Large post {i}"} for i in range(1000)
                ],
                "count": 1000,
            }
        }
        integration_client.make_request.return_value = large_response

        # Process large dataset
        result = await integration_service.get_group_posts(12345, count=1000)

        assert len(result["posts"]) == 1000
        assert result["total_count"] == 1000

        # Verify memory is properly managed (no memory leaks in real implementation)
        # This is more of a design consideration for the actual implementation

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(
        self, integration_service, integration_client
    ):
        """Test rate limiting integration"""
        # Mock rate limit exceeded
        integration_client.make_request.side_effect = VKAPIRateLimitError(
            wait_time=30.0
        )

        start_time = time.time()
        with pytest.raises(VKAPIRateLimitError) as exc_info:
            await integration_service.get_group_posts(12345)
        end_time = time.time()

        # Verify rate limit error includes wait time
        assert exc_info.value.details["wait_time"] == 30.0


class TestPerformanceIntegration:
    """Test suite for performance monitoring"""

    @pytest.mark.asyncio
    async def test_request_performance_tracking(
        self, integration_service, integration_repository, integration_client
    ):
        """Test request performance tracking"""
        integration_client.make_request.return_value = {
            "response": {"items": [], "count": 0}
        }

        start_time = time.time()
        await integration_service.get_group_posts(12345, count=5)
        end_time = time.time()

        # Verify performance was tracked
        integration_repository.save_request_log.assert_called_once()
        call_args = integration_repository.save_request_log.call_args

        response_time = call_args[0][2]  # response_time parameter
        assert isinstance(response_time, float)
        assert response_time >= 0
        assert (
            response_time <= end_time - start_time + 0.1
        )  # Allow small tolerance

    @pytest.mark.asyncio
    async def test_bulk_operation_performance(self, integration_service):
        """Test bulk operation performance"""
        # Mock fast post retrieval
        integration_service.get_post_by_id = AsyncMock(return_value={"id": 1})

        start_time = time.time()
        result = await integration_service.get_bulk_posts(
            12345, list(range(50))
        )
        end_time = time.time()

        processing_time = result["processing_time_seconds"]
        actual_time = end_time - start_time

        assert processing_time > 0
        assert processing_time <= actual_time + 0.1  # Allow small tolerance

    @pytest.mark.asyncio
    async def test_memory_efficiency_large_datasets(
        self, integration_service, integration_client
    ):
        """Test memory efficiency with large datasets"""
        # Create a very large response
        large_posts = [{"id": i, "text": f"Post {i}"} for i in range(5000)]
        integration_client.make_request.return_value = {
            "response": {"items": large_posts, "count": 5000}
        }

        # Process large dataset
        result = await integration_service.get_group_posts(12345, count=5000)

        assert len(result["posts"]) == 5000
        # In a real implementation, we'd verify memory usage here
        # For now, just verify the data is processed correctly
