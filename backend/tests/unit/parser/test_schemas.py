"""
Unit tests for Parser Pydantic schemas

Tests cover all schema validation including:
- ParseRequest validation
- ParseResponse structure
- ParseStatus fields
- ParserState validation
- ParseResult structure
- ParseTask model
- ParseStats validation
- Error response schemas
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.parser.schemas import (
    ParseRequest,
    ParseResponse,
    ParseStatus,
    ParserState,
    StopParseRequest,
    StopParseResponse,
    VKGroupInfo,
    VKPostInfo,
    VKCommentInfo,
    ParseResult,
    ParseTask,
    ParseStats,
    VKAPIError,
)


class TestParseRequest:
    """Test suite for ParseRequest schema"""

    def test_valid_parse_request(self, sample_parse_request_data):
        """Test valid parse request creation"""
        request = ParseRequest(**sample_parse_request_data)

        assert request.group_ids == [123456789, 987654321]
        assert request.max_posts == 50
        assert request.max_comments_per_post == 100
        assert request.force_reparse is False
        assert request.priority == "normal"

    def test_parse_request_defaults(self):
        """Test parse request with minimal data (defaults)"""
        data = {"group_ids": [123456789]}
        request = ParseRequest(**data)

        assert request.group_ids == [123456789]
        assert request.max_posts == 100
        assert request.max_comments_per_post == 100
        assert request.force_reparse is False
        assert request.priority == "normal"

    def test_parse_request_empty_group_ids(self):
        """Test parse request with empty group_ids"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[])

        assert "List should have at least 1 item" in str(exc_info.value)

    def test_parse_request_invalid_group_ids_type(self):
        """Test parse request with invalid group_ids type"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids="invalid")

        assert "Input should be a valid list" in str(exc_info.value)

    def test_parse_request_negative_group_id(self):
        """Test parse request with negative group_id"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[-123])

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_parse_request_invalid_max_posts(self):
        """Test parse request with invalid max_posts"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[123456789], max_posts=0)

        assert "Input should be greater than or equal to 1" in str(
            exc_info.value
        )

    def test_parse_request_max_posts_too_large(self):
        """Test parse request with max_posts too large"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[123456789], max_posts=1500)

        assert "Input should be less than or equal to 1000" in str(
            exc_info.value
        )

    def test_parse_request_invalid_max_comments(self):
        """Test parse request with invalid max_comments_per_post"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[123456789], max_comments_per_post=2000)

        assert "Input should be less than or equal to 1000" in str(
            exc_info.value
        )

    def test_parse_request_invalid_priority(self):
        """Test parse request with invalid priority"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[123456789], priority="urgent")

        assert "Input should be 'low', 'normal' or 'high'" in str(
            exc_info.value
        )

    def test_parse_request_invalid_force_reparse_type(self):
        """Test parse request with invalid force_reparse type"""
        with pytest.raises(ValidationError) as exc_info:
            ParseRequest(group_ids=[123456789], force_reparse="true")

        assert "Input should be a valid boolean" in str(exc_info.value)


class TestParseResponse:
    """Test suite for ParseResponse schema"""

    def test_valid_parse_response(self, sample_parse_response):
        """Test valid parse response creation"""
        assert sample_parse_response.task_id is not None
        assert sample_parse_response.status == "started"
        assert len(sample_parse_response.group_ids) == 2
        assert sample_parse_response.estimated_time == 60
        assert isinstance(sample_parse_response.created_at, datetime)

    def test_parse_response_required_fields(self):
        """Test parse response required fields"""
        with pytest.raises(ValidationError) as exc_info:
            ParseResponse(
                status="started",
                group_ids=[123456789],
                estimated_time=30,
                created_at=datetime.utcnow(),
            )

        assert "Field required" in str(exc_info.value)


class TestParseStatus:
    """Test suite for ParseStatus schema"""

    def test_valid_parse_status(self, sample_parse_status):
        """Test valid parse status creation"""
        assert sample_parse_status.task_id is not None
        assert sample_parse_status.status == "running"
        assert sample_parse_status.progress == 45.5
        assert sample_parse_status.current_group == 123456789
        assert sample_parse_status.groups_completed == 1
        assert sample_parse_status.groups_total == 2
        assert sample_parse_status.posts_found == 25
        assert sample_parse_status.comments_found == 150
        assert len(sample_parse_status.errors) == 1

    def test_parse_status_defaults(self):
        """Test parse status with minimal required fields"""
        status = ParseStatus(
            task_id="test-task-id",
            status="pending",
            groups_completed=0,
            groups_total=1,
            posts_found=0,
            comments_found=0,
        )

        assert status.task_id == "test-task-id"
        assert status.status == "pending"
        assert status.progress == 0.0
        assert status.errors == []

    def test_parse_status_invalid_progress(self):
        """Test parse status with invalid progress value"""
        with pytest.raises(ValidationError) as exc_info:
            ParseStatus(
                task_id="test-task-id",
                status="running",
                progress=150.0,  # Invalid: > 100
                groups_completed=1,
                groups_total=2,
                posts_found=10,
                comments_found=50,
            )

        assert "Input should be less than or equal to 100" in str(
            exc_info.value
        )


class TestParserState:
    """Test suite for ParserState schema"""

    def test_valid_parser_state(self, sample_parser_state):
        """Test valid parser state creation"""
        assert sample_parser_state.is_running is True
        assert sample_parser_state.active_tasks == 3
        assert sample_parser_state.queue_size == 5
        assert sample_parser_state.total_tasks_processed == 42
        assert sample_parser_state.total_posts_found == 1250
        assert sample_parser_state.total_comments_found == 8750
        assert sample_parser_state.uptime_seconds == 3600

    def test_parser_state_required_fields(self):
        """Test parser state required fields"""
        with pytest.raises(ValidationError) as exc_info:
            ParserState(
                is_running=False,
                active_tasks=0,
                queue_size=0,
                total_tasks_processed=10,
                total_posts_found=100,
                total_comments_found=500,
                # Missing uptime_seconds
            )

        assert "Field required" in str(exc_info.value)


class TestStopParseRequest:
    """Test suite for StopParseRequest schema"""

    def test_valid_stop_parse_request_with_task_id(self):
        """Test valid stop parse request with task_id"""
        request = StopParseRequest(task_id="test-task-id")

        assert request.task_id == "test-task-id"

    def test_valid_stop_parse_request_without_task_id(self):
        """Test valid stop parse request without task_id"""
        request = StopParseRequest()

        assert request.task_id is None


class TestStopParseResponse:
    """Test suite for StopParseResponse schema"""

    def test_valid_stop_parse_response(self):
        """Test valid stop parse response"""
        response = StopParseResponse(
            stopped_tasks=["task-1", "task-2"],
            message="Tasks stopped successfully",
        )

        assert len(response.stopped_tasks) == 2
        assert response.message == "Tasks stopped successfully"


class TestVKGroupInfo:
    """Test suite for VKGroupInfo schema"""

    def test_valid_vk_group_info(self, sample_vk_group_info):
        """Test valid VK group info creation"""
        group = VKGroupInfo(**sample_vk_group_info)

        assert group.id == 123456789
        assert group.name == "Test Group"
        assert group.screen_name == "test_group"
        assert group.members_count == 15000
        assert group.is_closed is False

    def test_vk_group_info_optional_fields(self):
        """Test VK group info with optional fields"""
        data = {
            "id": 123456789,
            "name": "Test Group",
            "screen_name": "test_group",
            "members_count": 1000,
            "is_closed": False,
        }

        group = VKGroupInfo(**data)

        assert group.description is None
        assert group.photo_url is None


class TestVKPostInfo:
    """Test suite for VKPostInfo schema"""

    def test_valid_vk_post_info(self, sample_vk_post):
        """Test valid VK post info creation"""
        post = VKPostInfo(**sample_vk_post)

        assert post.id == 1
        assert post.text == "Test post content"
        assert isinstance(post.date, datetime)
        assert post.likes_count == 42
        assert post.comments_count == 15
        assert post.author_id == 987654321


class TestVKCommentInfo:
    """Test suite for VKCommentInfo schema"""

    def test_valid_vk_comment_info(self, sample_vk_comment):
        """Test valid VK comment info creation"""
        comment = VKCommentInfo(**sample_vk_comment)

        assert comment.id == 1
        assert comment.post_id == 1
        assert comment.text == "Test comment"
        assert isinstance(comment.date, datetime)
        assert comment.likes_count == 5
        assert comment.author_id == 111222333
        assert comment.author_name == "Test User"

    def test_vk_comment_info_without_author_name(self):
        """Test VK comment info without author_name"""
        data = {
            "id": 1,
            "post_id": 1,
            "text": "Test comment",
            "date": datetime.utcnow(),
            "likes_count": 5,
            "author_id": 111222333,
        }

        comment = VKCommentInfo(**data)

        assert comment.author_name is None


class TestParseResult:
    """Test suite for ParseResult schema"""

    def test_valid_parse_result(self, sample_parse_result):
        """Test valid parse result creation"""
        assert sample_parse_result.group_id == 123456789
        assert sample_parse_result.posts_found == 25
        assert sample_parse_result.comments_found == 150
        assert sample_parse_result.posts_saved == 25
        assert sample_parse_result.comments_saved == 150
        assert len(sample_parse_result.errors) == 1
        assert sample_parse_result.duration_seconds == 15.5

    def test_parse_result_required_fields(self):
        """Test parse result required fields"""
        with pytest.raises(ValidationError) as exc_info:
            ParseResult(
                group_id=123456789,
                posts_found=10,
                comments_found=50,
                posts_saved=10,
                comments_saved=50,
                errors=[],
                # Missing duration_seconds
            )

        assert "Field required" in str(exc_info.value)


class TestParseTask:
    """Test suite for ParseTask schema"""

    def test_valid_parse_task(self, sample_parse_task):
        """Test valid parse task creation"""
        assert sample_parse_task.id is not None
        assert len(sample_parse_task.group_ids) == 2
        assert isinstance(sample_parse_task.config, dict)
        assert sample_parse_task.status == "completed"
        assert isinstance(sample_parse_task.created_at, datetime)
        assert sample_parse_task.progress == 100.0

    def test_parse_task_optional_fields(self):
        """Test parse task with optional fields"""
        task = ParseTask(
            id="test-task-id",
            group_ids=[123456789],
            config={"max_posts": 100},
            status="pending",
            created_at=datetime.utcnow(),
            progress=0.0,
        )

        assert task.started_at is None
        assert task.completed_at is None
        assert task.result is None


class TestParseStats:
    """Test suite for ParseStats schema"""

    def test_valid_parse_stats(self, sample_parse_stats):
        """Test valid parse stats creation"""
        assert sample_parse_stats.total_tasks == 10
        assert sample_parse_stats.completed_tasks == 7
        assert sample_parse_stats.failed_tasks == 2
        assert sample_parse_stats.running_tasks == 1
        assert sample_parse_stats.total_posts_found == 350
        assert sample_parse_stats.total_comments_found == 2450
        assert sample_parse_stats.total_processing_time == 450
        assert sample_parse_stats.average_task_duration == 45.0

    def test_parse_stats_required_fields(self):
        """Test parse stats required fields"""
        with pytest.raises(ValidationError) as exc_info:
            ParseStats(
                total_tasks=5,
                completed_tasks=3,
                failed_tasks=1,
                running_tasks=1,
                total_posts_found=100,
                total_comments_found=500,
                total_processing_time=200,
                # Missing average_task_duration
            )

        assert "Field required" in str(exc_info.value)


class TestVKAPIError:
    """Test suite for VKAPIError schema"""

    def test_valid_vk_api_error(self):
        """Test valid VK API error creation"""
        error = VKAPIError(
            error_code=5,
            error_msg="User authorization failed",
            request_params={"method": "wall.get", "oauth": "1"},
        )

        assert error.error_code == 5
        assert error.error_msg == "User authorization failed"
        assert error.request_params == {"method": "wall.get", "oauth": "1"}

    def test_vk_api_error_without_request_params(self):
        """Test VK API error without request_params"""
        error = VKAPIError(error_code=1, error_msg="Unknown error occurred")

        assert error.error_code == 1
        assert error.error_msg == "Unknown error occurred"
        assert error.request_params is None
