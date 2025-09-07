"""
Configuration and fixtures for Parser module tests

Provides common test fixtures, mocks, and setup for all parser tests.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from uuid import uuid4

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
from src.exceptions import APIError


@pytest.fixture
def mock_vk_api_service():
    """Mock VK API service for testing"""
    service = AsyncMock()
    service.get_group_info = AsyncMock()
    service.get_group_posts = AsyncMock()
    service.get_post_comments = AsyncMock()
    return service


@pytest.fixture
def mock_parser_service(mock_vk_api_service):
    """Mock parser service with VK API service"""
    service = ParserService(vk_api_service=mock_vk_api_service)
    return service


@pytest.fixture
def sample_group_ids():
    """Sample group IDs for testing"""
    return [123456789, 987654321, 111222333]


@pytest.fixture
def sample_parse_request_data():
    """Sample parse request data"""
    return {
        "group_ids": [123456789, 987654321],
        "max_posts": 50,
        "max_comments_per_post": 100,
        "force_reparse": False,
        "priority": "normal",
    }


@pytest.fixture
def sample_parse_request(sample_parse_request_data):
    """Sample parse request object"""
    return ParseRequest(**sample_parse_request_data)


@pytest.fixture
def sample_parse_response():
    """Sample parse response"""
    return ParseResponse(
        task_id=str(uuid4()),
        status="started",
        group_ids=[123456789, 987654321],
        estimated_time=60,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_parse_status():
    """Sample parse status"""
    return ParseStatus(
        task_id=str(uuid4()),
        status="running",
        progress=45.5,
        current_group=123456789,
        groups_completed=1,
        groups_total=2,
        posts_found=25,
        comments_found=150,
        errors=["Sample error"],
        started_at=datetime.utcnow(),
        duration=30,
    )


@pytest.fixture
def sample_parser_state():
    """Sample parser state"""
    return ParserState(
        is_running=True,
        active_tasks=3,
        queue_size=5,
        total_tasks_processed=42,
        total_posts_found=1250,
        total_comments_found=8750,
        last_activity=datetime.utcnow(),
        uptime_seconds=3600,
    )


@pytest.fixture
def sample_parse_result():
    """Sample parse result"""
    return ParseResult(
        group_id=123456789,
        posts_found=25,
        comments_found=150,
        posts_saved=25,
        comments_saved=150,
        errors=["Minor parsing error"],
        duration_seconds=15.5,
    )


@pytest.fixture
def sample_parse_task(sample_parse_result):
    """Sample parse task"""
    return ParseTask(
        id=str(uuid4()),
        group_ids=[123456789, 987654321],
        config={
            "max_posts": 100,
            "max_comments_per_post": 100,
            "force_reparse": False,
            "priority": "normal",
        },
        status="completed",
        created_at=datetime.utcnow(),
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        progress=100.0,
        result=sample_parse_result,
    )


@pytest.fixture
def sample_parse_stats():
    """Sample parse statistics"""
    return ParseStats(
        total_tasks=10,
        completed_tasks=7,
        failed_tasks=2,
        running_tasks=1,
        total_posts_found=350,
        total_comments_found=2450,
        total_processing_time=450,
        average_task_duration=45.0,
        max_groups_per_request=50,
        max_posts_per_request=100,
        max_comments_per_request=200,
        max_users_per_request=1000,
    )


@pytest.fixture
def sample_vk_group_info():
    """Sample VK group information"""
    return {
        "id": 123456789,
        "name": "Test Group",
        "screen_name": "test_group",
        "description": "A test VK group for parsing",
        "members_count": 15000,
        "photo_url": "https://example.com/photo.jpg",
        "is_closed": False,
    }


@pytest.fixture
def sample_vk_post():
    """Sample VK post"""
    return {
        "id": 1,
        "text": "Test post content",
        "date": datetime.utcnow(),
        "likes_count": 42,
        "comments_count": 15,
        "author_id": 987654321,
    }


@pytest.fixture
def sample_vk_comment():
    """Sample VK comment"""
    return {
        "id": 1,
        "post_id": 1,
        "text": "Test comment",
        "date": datetime.utcnow(),
        "likes_count": 5,
        "author_id": 111222333,
        "author_name": "Test User",
    }


@pytest.fixture
def mock_task_id():
    """Sample task ID for testing"""
    return str(uuid4())


@pytest.fixture
def mock_parsing_errors():
    """Sample parsing errors"""
    return ["Network timeout", "Invalid group data", "API rate limit exceeded"]


@pytest.fixture
def mock_validation_errors():
    """Sample validation errors"""
    return [
        "group_ids cannot be empty",
        "max_posts must be between 1 and 1000",
        "priority must be low, normal, or high",
    ]


# Async context manager mocks
@pytest.fixture
def mock_async_context_manager():
    """Mock async context manager for database operations"""

    class AsyncContextManager:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    return AsyncContextManager()


@pytest.fixture
def mock_database_session(mock_async_context_manager):
    """Mock database session"""
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# Exception fixtures
@pytest.fixture
def task_not_found_exception(mock_task_id):
    """Task not found exception"""
    return TaskNotFoundException(mock_task_id)


@pytest.fixture
def invalid_task_data_exception():
    """Invalid task data exception"""
    return InvalidTaskDataException("group_ids", "invalid_value")


@pytest.fixture
def parsing_exception():
    """Parsing exception"""
    return ParsingException("Test parsing error", group_id=123456789)
