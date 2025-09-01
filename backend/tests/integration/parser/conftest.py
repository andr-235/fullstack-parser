"""
Configuration and fixtures for Parser module integration tests

Provides integration-level fixtures, test data, and setup for testing
complete workflows and component interactions.
"""

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from src.main import app
from src.parser.service import ParserService
from src.parser.schemas import (
    ParseRequest,
    ParseResponse,
    ParseStatus,
    ParserState,
    ParseResult,
    ParseTask,
    ParseStats,
)
from src.parser.exceptions import (
    TaskNotFoundException,
    InvalidTaskDataException,
    ParsingException,
)


@pytest.fixture
def mock_vk_api_client():
    """Mock VK API client for integration tests"""
    client = AsyncMock()
    client.get_group_info = AsyncMock()
    client.get_group_posts = AsyncMock()
    client.get_post_comments = AsyncMock()
    client.get_user_info = AsyncMock()
    return client


@pytest.fixture
def mock_vk_api_service(mock_vk_api_client):
    """Mock VK API service with client for integration tests"""
    service = AsyncMock()
    service.get_group_info = AsyncMock()
    service.get_group_posts = AsyncMock()
    service.get_post_comments = AsyncMock()
    service.get_user_info = AsyncMock()
    return service


@pytest.fixture
def integration_parser_service(mock_vk_api_service):
    """ParserService instance for integration tests"""
    service = ParserService(vk_api_service=mock_vk_api_service)
    return service


@pytest.fixture
def mock_parser_service(integration_parser_service):
    """Mock parser service for integration tests"""
    return integration_parser_service


@pytest.fixture
def sample_vk_api_responses():
    """Sample VK API responses for integration tests"""
    return {
        "group_info": {
            "group": {
                "id": 123456789,
                "name": "Test Community",
                "screen_name": "test_community",
                "description": "A test VK community for integration testing",
                "members_count": 50000,
                "photo_url": "https://example.com/photo.jpg",
                "is_closed": False,
            }
        },
        "group_posts": {
            "posts": [
                {
                    "id": 1001,
                    "text": "Test post 1",
                    "date": int(
                        (datetime.utcnow() - timedelta(hours=1)).timestamp()
                    ),
                    "likes": {"count": 42},
                    "comments": {"count": 15},
                    "from_id": 987654321,
                },
                {
                    "id": 1002,
                    "text": "Test post 2",
                    "date": int(
                        (datetime.utcnow() - timedelta(hours=2)).timestamp()
                    ),
                    "likes": {"count": 25},
                    "comments": {"count": 8},
                    "from_id": 987654322,
                },
            ]
        },
        "post_comments": {
            "comments": [
                {
                    "id": 2001,
                    "post_id": 1001,
                    "text": "Great post!",
                    "date": int(
                        (datetime.utcnow() - timedelta(minutes=30)).timestamp()
                    ),
                    "likes": {"count": 5},
                    "from_id": 111111111,
                    "author_name": "User One",
                },
                {
                    "id": 2002,
                    "post_id": 1001,
                    "text": "Thanks for sharing",
                    "date": int(
                        (datetime.utcnow() - timedelta(minutes=15)).timestamp()
                    ),
                    "likes": {"count": 3},
                    "from_id": 222222222,
                    "author_name": "User Two",
                },
            ]
        },
        "user_info": {
            "user": {
                "id": 111111111,
                "first_name": "John",
                "last_name": "Doe",
                "photo_url": "https://example.com/avatar.jpg",
            }
        },
    }


@pytest.fixture
def integration_test_data(sample_vk_api_responses):
    """Complete test data set for integration tests"""
    return {
        "group_ids": [123456789, 987654321],
        "max_posts": 10,
        "max_comments_per_post": 50,
        "force_reparse": False,
        "priority": "normal",
        "vk_responses": sample_vk_api_responses,
        "expected_results": {
            "task_id": None,  # Will be set during test
            "posts_found": 2,
            "comments_found": 4,
            "posts_saved": 2,
            "comments_saved": 4,
            "groups_processed": 1,
        },
    }


@pytest.fixture
def mock_task_storage():
    """Mock task storage for integration tests"""

    class MockTaskStorage:
        def __init__(self):
            self.storage = {}

        async def get_task(self, task_id: str) -> Dict[str, Any]:
            return self.storage.get(task_id)

        async def save_task(
            self, task_id: str, task_data: Dict[str, Any]
        ) -> None:
            self.storage[task_id] = task_data

        async def update_task(
            self, task_id: str, updates: Dict[str, Any]
        ) -> None:
            if task_id in self.storage:
                self.storage[task_id].update(updates)

        async def delete_task(self, task_id: str) -> None:
            self.storage.pop(task_id, None)

        async def list_tasks(
            self, limit: int = 50, offset: int = 0, **filters
        ) -> List[Dict[str, Any]]:
            tasks = list(self.storage.values())
            for key, value in filters.items():
                tasks = [t for t in tasks if t.get(key) == value]
            return tasks[offset : offset + limit]

    return MockTaskStorage()


@pytest.fixture
def integration_config():
    """Integration test configuration"""
    return {
        "timeout": 30,
        "max_retries": 3,
        "batch_size": 10,
        "rate_limit_delay": 1.0,
        "enable_caching": False,
        "log_level": "DEBUG",
    }


@pytest.fixture
def setup_integration_environment(
    integration_parser_service,
    mock_vk_api_service,
    sample_vk_api_responses,
    mock_task_storage,
):
    """Setup complete integration environment"""
    # Configure VK API service mocks
    mock_vk_api_service.get_group_info.return_value = sample_vk_api_responses[
        "group_info"
    ]
    mock_vk_api_service.get_group_posts.return_value = sample_vk_api_responses[
        "group_posts"
    ]
    mock_vk_api_service.get_post_comments.return_value = (
        sample_vk_api_responses["post_comments"]
    )
    mock_vk_api_service.get_user_info.return_value = sample_vk_api_responses[
        "user_info"
    ]

    # Task storage is handled by service mocking

    return {
        "service": integration_parser_service,
        "vk_api": mock_vk_api_service,
        "storage": mock_task_storage,
        "test_data": sample_vk_api_responses,
    }


# Test data factories
def create_integration_parse_request(**overrides):
    """Factory for creating integration test parse requests"""
    defaults = {
        "group_ids": [123456789],
        "max_posts": 10,
        "max_comments_per_post": 50,
        "force_reparse": False,
        "priority": "normal",
    }
    defaults.update(overrides)
    return ParseRequest(**defaults)


def create_integration_parse_task(**overrides):
    """Factory for creating integration test parse tasks"""
    defaults = {
        "id": str(uuid4()),
        "group_ids": [123456789],
        "config": {
            "max_posts": 10,
            "max_comments_per_post": 50,
            "force_reparse": False,
            "priority": "normal",
        },
        "status": "pending",
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "progress": 0.0,
        "result": None,
    }
    defaults.update(overrides)
    return defaults


def create_integration_parse_result(**overrides):
    """Factory for creating integration test parse results"""
    defaults = {
        "group_id": 123456789,
        "posts_found": 5,
        "comments_found": 25,
        "posts_saved": 5,
        "comments_saved": 25,
        "errors": [],
        "duration_seconds": 15.5,
    }
    defaults.update(overrides)
    return ParseResult(**defaults)


# Performance test fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance integration tests"""
    return {
        "warmup_iterations": 5,
        "test_iterations": 20,
        "max_execution_time": 60,  # seconds
        "memory_threshold": 100 * 1024 * 1024,  # 100MB
        "cpu_threshold": 80.0,  # 80%
    }


@pytest.fixture
def load_test_config():
    """Configuration for load integration tests"""
    return {
        "concurrent_users": 10,
        "requests_per_user": 50,
        "ramp_up_time": 30,  # seconds
        "test_duration": 300,  # seconds
        "think_time": (1, 3),  # min/max seconds between requests
    }


# Error simulation fixtures
@pytest.fixture
def error_simulation_config():
    """Configuration for error simulation in integration tests"""
    return {
        "network_errors": ["timeout", "connection_refused", "dns_failure"],
        "api_errors": ["rate_limit", "auth_failure", "invalid_request"],
        "data_errors": [
            "corrupted_response",
            "empty_response",
            "invalid_format",
        ],
        "error_probability": 0.1,  # 10% chance of error
        "recovery_attempts": 3,
    }


@pytest.fixture
def mock_external_dependencies():
    """Mock external dependencies for integration tests"""
    return {
        "database": AsyncMock(),
        "cache": AsyncMock(),
        "message_queue": AsyncMock(),
        "monitoring": AsyncMock(),
        "logging": AsyncMock(),
    }


@pytest.fixture
def api_client():
    """FastAPI test client for integration tests"""
    return TestClient(app)


# Test utilities
def assert_integration_response_format(response, expected_keys):
    """Assert that integration response has correct format"""
    assert isinstance(response, dict), "Response should be a dictionary"
    for key in expected_keys:
        assert key in response, f"Response should contain key: {key}"


def assert_task_lifecycle(task_data, expected_statuses):
    """Assert that task goes through expected lifecycle statuses"""
    actual_statuses = [
        status
        for status in expected_statuses
        if status in task_data.get("status_history", [])
    ]
    assert len(actual_statuses) == len(
        expected_statuses
    ), f"Task should go through statuses: {expected_statuses}"


def assert_performance_metrics(metrics, thresholds):
    """Assert that performance metrics are within acceptable thresholds"""
    if "execution_time" in thresholds:
        assert (
            metrics.get("execution_time", 0) <= thresholds["execution_time"]
        ), "Execution time exceeded threshold"

    if "memory_usage" in thresholds:
        assert (
            metrics.get("memory_usage", 0) <= thresholds["memory_usage"]
        ), "Memory usage exceeded threshold"

    if "cpu_usage" in thresholds:
        assert (
            metrics.get("cpu_usage", 0) <= thresholds["cpu_usage"]
        ), "CPU usage exceeded threshold"
