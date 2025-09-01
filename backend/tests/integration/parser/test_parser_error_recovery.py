"""
Error recovery integration tests for Parser

Tests error handling and recovery scenarios including:
- Network failures and recovery
- API rate limits and backoff
- Partial failures and data consistency
- Service degradation and failover
- Resource exhaustion recovery
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import time

from src.parser.service import ParserService
from src.parser.exceptions import (
    VKAPILimitExceededException,
    VKAPITimeoutException,
    ParsingException,
    TaskNotFoundException,
)


class TestParserErrorRecoveryIntegration:
    """Error recovery integration tests for Parser"""

    @pytest.fixture
    def error_prone_service(self, mock_vk_api_service):
        """ParserService configured to handle various error scenarios"""
        service = ParserService(vk_api_service=mock_vk_api_service)
        return service

    @pytest.mark.asyncio
    async def test_network_failure_recovery(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test recovery from network failures during parsing"""
        call_count = 0

        async def failing_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Fail first 2 attempts
                raise VKAPITimeoutException(timeout=30)
            # Succeed on 3rd attempt
            return {
                "group": {
                    "id": 123456789,
                    "name": "Test Group",
                    "is_closed": False,
                }
            }

        mock_vk_api_service.get_group_info.side_effect = failing_api_call

        # Attempt parsing - should eventually succeed
        result = await error_prone_service.parse_group(
            group_id=123456789, max_posts=5, max_comments_per_post=10
        )

        # Verify recovery worked
        assert result["group_id"] == 123456789
        assert call_count == 3  # Should have retried 2 times

    @pytest.mark.asyncio
    async def test_rate_limit_handling_and_backoff(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test handling of VK API rate limits with exponential backoff"""
        call_count = 0
        start_time = time.time()

        async def rate_limited_api_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                raise VKAPILimitExceededException(retry_after=1)
            elif call_count == 2:
                raise VKAPILimitExceededException(retry_after=2)
            else:
                # Succeed after backoff
                return {
                    "posts": [
                        {
                            "id": 1001,
                            "text": "Test post",
                            "likes": {"count": 5},
                        }
                    ]
                }

        mock_vk_api_service.get_group_posts.side_effect = rate_limited_api_call

        # Start parsing
        result = await error_prone_service.parse_group(
            group_id=123456789, max_posts=5, max_comments_per_post=10
        )

        end_time = time.time()
        total_time = end_time - start_time

        # Should have taken at least the backoff time
        assert total_time >= 3  # 1 + 2 seconds backoff
        assert call_count == 3  # Initial + 2 retries
        assert result["posts_found"] == 1

    @pytest.mark.asyncio
    async def test_partial_failure_data_consistency(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test data consistency when some operations fail partially"""
        # Configure mixed success/failure scenario
        post_call_count = 0

        async def partial_failure_posts(*args, **kwargs):
            nonlocal post_call_count
            post_call_count += 1
            group_id = kwargs.get("group_id", args[0] if args else None)

            if group_id == 123456789:
                # First group succeeds
                return {"posts": [{"id": 1001, "text": "Post 1"}]}
            elif group_id == 987654321:
                # Second group fails
                raise VKAPITimeoutException(timeout=30)
            else:
                # Default success case
                return {"posts": [{"id": 1003, "text": "Post 3"}]}

        mock_vk_api_service.get_group_posts.side_effect = partial_failure_posts
        mock_vk_api_service.get_post_comments.return_value = {"comments": []}
        mock_vk_api_service.get_group_info.return_value = {
            "group": {"id": 987654321, "name": "Test Group"}
        }

        # Start parsing with multiple groups
        result1 = await error_prone_service.parse_group(
            group_id=123456789, max_posts=5, max_comments_per_post=10
        )

        # Second group should fail with VKAPITimeoutException
        with pytest.raises(VKAPITimeoutException):
            await error_prone_service.parse_group(
                group_id=987654321, max_posts=5, max_comments_per_post=10
            )

        # Verify partial success is handled correctly
        assert result1["posts_found"] == 1  # First group succeeded
        assert (
            post_call_count == 2
        )  # 2 API calls made (one failed, one succeeded)

        # Check that errors are recorded
        assert (
            len(result1["errors"]) == 0
        )  # No errors in successful operations

    @pytest.mark.asyncio
    async def test_service_degradation_recovery(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test recovery from service degradation scenarios"""

        # Simulate service degradation (slow responses)
        async def degraded_api_call(*args, **kwargs):
            await asyncio.sleep(2)  # 2 second delay (degraded)
            return {
                "group": {
                    "id": 123456789,
                    "name": "Slow Group",
                    "is_closed": False,
                }
            }

        mock_vk_api_service.get_group_info.side_effect = degraded_api_call

        # Mock get_group_posts to return sample posts
        async def mock_get_posts(*args, **kwargs):
            await asyncio.sleep(2)  # 2 second delay (degraded)
            return {
                "posts": [
                    {
                        "id": 1001,
                        "text": "Test post",
                        "date": 1234567890,
                        "likes": {"count": 10},
                        "comments": {"count": 5},
                        "from_id": 987654321,
                    }
                ]
            }

        mock_vk_api_service.get_group_posts.side_effect = mock_get_posts

        # Mock get_post_comments to return sample comments
        async def mock_get_comments(*args, **kwargs):
            await asyncio.sleep(2)  # 2 second delay (degraded)
            return {
                "comments": [
                    {
                        "id": 2001,
                        "post_id": 1001,
                        "text": "Test comment",
                        "date": 1234567890,
                        "likes": {"count": 2},
                        "from_id": 111111111,
                        "author_name": "Test User",
                    }
                ]
            }

        mock_vk_api_service.get_post_comments.side_effect = mock_get_comments

        start_time = time.time()

        # Perform multiple operations during degradation
        tasks = []
        for i in range(3):
            task = error_prone_service.parse_group(
                group_id=123456789 + i, max_posts=5, max_comments_per_post=10
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All operations should complete despite degradation
        assert len(results) == 3
        assert all(
            result["group_id"] == 123456789 + i
            for i, result in enumerate(results)
        )
        assert total_time >= 6  # At least 2 seconds per operation

    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self, error_prone_service):
        """Test recovery from resource exhaustion scenarios"""
        # Simulate memory pressure scenario
        large_data = "x" * (10 * 1024 * 1024)  # 10MB string

        # Perform operations that might cause memory pressure
        results = []
        for i in range(10):
            try:
                result = await error_prone_service.start_parsing(
                    group_ids=[123456789 + i],
                    max_posts=20,
                    max_comments_per_post=50,
                )
                results.append(result)
            except Exception as e:
                # Should handle memory pressure gracefully
                assert (
                    "memory" in str(e).lower() or "resource" in str(e).lower()
                )

        # Service should continue to function after potential memory pressure
        final_result = await error_prone_service.get_parser_state()
        assert "active_tasks" in final_result

    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test circuit breaker pattern for external service failures"""
        failure_count = 0
        success_count = 0

        async def circuit_breaker_api_call(*args, **kwargs):
            nonlocal failure_count, success_count

            if failure_count < 5:  # Fail first 5 attempts
                failure_count += 1
                raise VKAPITimeoutException(timeout=30)
            else:
                success_count += 1
                return {"group": {"id": 123456789, "name": "Test Group"}}

        mock_vk_api_service.get_group_info.side_effect = (
            circuit_breaker_api_call
        )

        # Mock get_group_posts for successful attempts
        async def mock_get_posts(*args, **kwargs):
            return {
                "posts": [
                    {
                        "id": 1001,
                        "text": "Test post",
                        "date": 1234567890,
                        "likes": {"count": 10},
                        "comments": {"count": 5},
                        "from_id": 987654321,
                    }
                ]
            }

        # Mock get_post_comments for successful attempts
        async def mock_get_comments(*args, **kwargs):
            return {
                "comments": [
                    {
                        "id": 2001,
                        "post_id": 1001,
                        "text": "Test comment",
                        "date": 1234567890,
                        "likes": {"count": 2},
                        "from_id": 111111111,
                        "author_name": "Test User",
                    }
                ]
            }

        mock_vk_api_service.get_group_posts.side_effect = mock_get_posts
        mock_vk_api_service.get_post_comments.side_effect = mock_get_comments

        # First 5 attempts should fail
        for i in range(5):
            with pytest.raises(VKAPITimeoutException):
                await error_prone_service.parse_group(
                    group_id=123456789, max_posts=5, max_comments_per_post=10
                )

        # 6th attempt should succeed (circuit breaker recovers)
        result = await error_prone_service.parse_group(
            group_id=123456789, max_posts=5, max_comments_per_post=10
        )

        assert result["group_id"] == 123456789
        assert failure_count == 5
        assert success_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_error_isolation(
        self, error_prone_service, mock_vk_api_service
    ):
        """Test that errors in one operation don't affect concurrent operations"""
        error_call_count = 0
        success_call_count = 0

        async def mixed_error_api_call(*args, **kwargs):
            nonlocal error_call_count, success_call_count

            if "error_group" in str(args) or "error_group" in str(kwargs):
                error_call_count += 1
                raise VKAPITimeoutException(timeout=30)
            else:
                success_call_count += 1
                return {"group": {"id": 123456789, "name": "Success Group"}}

        mock_vk_api_service.get_group_info.side_effect = mixed_error_api_call

        # Start concurrent operations - some will succeed, some will fail
        async def run_with_error():
            try:
                return await error_prone_service.parse_group(
                    group_id=999999999,  # This will "error"
                    max_posts=5,
                    max_comments_per_post=10,
                )
            except VKAPITimeoutException:
                return {"error": "timeout"}

        async def run_with_success():
            return await error_prone_service.parse_group(
                group_id=123456789,  # This will succeed
                max_posts=5,
                max_comments_per_post=10,
            )

        # Run both operations concurrently
        error_result, success_result = await asyncio.gather(
            run_with_error(), run_with_success()
        )

        # Verify isolation - one succeeds, one fails, but they don't interfere
        assert "error" in error_result
        assert success_result["group_id"] == 123456789
        assert error_call_count == 1
        assert success_call_count == 1

    @pytest.mark.asyncio
    async def test_graceful_shutdown_under_load(self, error_prone_service):
        """Test graceful shutdown when operations are in progress"""
        # Start multiple long-running operations
        tasks = []
        for i in range(5):
            task = error_prone_service.start_parsing(
                group_ids=[123456789 + i],
                max_posts=10,
                max_comments_per_post=20,
            )
            tasks.append(task)

        # Start operations
        started_tasks = await asyncio.gather(*tasks)

        # Simulate shutdown signal
        shutdown_tasks = []
        for task_result in started_tasks:
            shutdown_task = error_prone_service.stop_parsing(
                task_id=task_result["task_id"]
            )
            shutdown_tasks.append(shutdown_task)

        # Wait for graceful shutdown
        shutdown_results = await asyncio.gather(*shutdown_tasks)

        # Verify all tasks were stopped gracefully
        assert len(shutdown_results) == 5
        for result in shutdown_results:
            assert "stopped_tasks" in result
            assert len(result["stopped_tasks"]) == 1

        # Verify final state
        final_state = await error_prone_service.get_parser_state()
        assert final_state["active_tasks"] == 0
