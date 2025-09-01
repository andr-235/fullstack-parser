"""
Unit tests for Parser utility functions

Tests cover all utility functions including:
- Request validation
- Task progress calculation
- Time estimation
- Text sanitization
- VK data validation
- Task summary generation
"""

import pytest
from datetime import datetime

from src.parser.utils import (
    validate_parsing_request,
    calculate_task_progress,
    estimate_parsing_time,
    sanitize_vk_text,
    extract_vk_entities,
    validate_vk_group_id,
    validate_vk_post_id,
    generate_task_summary,
    create_parsing_report,
)


class TestValidateParsingRequest:
    """Test suite for validate_parsing_request function"""

    def test_valid_request(self):
        """Test validation of valid request"""
        data = {
            "group_ids": [123456789, 987654321],
            "max_posts": 50,
            "max_comments_per_post": 100,
            "force_reparse": False,
            "priority": "normal",
        }
        errors = validate_parsing_request(data)

        assert errors == []

    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        data = {"max_posts": 100}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "group_ids не заполнено" in errors[0]

    def test_empty_group_ids(self):
        """Test validation with empty group_ids"""
        data = {"group_ids": []}

        errors = validate_parsing_request(data)

        assert len(errors) == 2
        assert "group_ids не может быть пустым" in errors[0]
        assert "group_ids должен быть списком" in errors[1]

    def test_invalid_group_ids_type(self):
        """Test validation with invalid group_ids type"""
        data = {"group_ids": "invalid"}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "group_ids должен быть списком" in errors[0]

    def test_negative_group_id(self):
        """Test validation with negative group_id"""
        data = {"group_ids": [123, -456]}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert (
            "group_ids[1] должен быть положительным целым числом" in errors[0]
        )

    def test_invalid_max_posts(self):
        """Test validation with invalid max_posts"""
        data = {"group_ids": [123], "max_posts": 0}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "max_posts должен быть от 1 до 1000" in errors[0]

    def test_max_posts_too_large(self):
        """Test validation with max_posts too large"""
        data = {"group_ids": [123], "max_posts": 1500}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "max_posts должен быть от 1 до 1000" in errors[0]

    def test_invalid_max_comments(self):
        """Test validation with invalid max_comments_per_post"""
        data = {"group_ids": [123], "max_comments_per_post": 2000}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "max_comments_per_post должен быть от 1 до 1000" in errors[0]

    def test_invalid_priority(self):
        """Test validation with invalid priority"""
        data = {"group_ids": [123], "priority": "urgent"}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "priority должен быть: low, normal, high" in errors[0]

    def test_invalid_force_reparse_type(self):
        """Test validation with invalid force_reparse type"""
        data = {"group_ids": [123], "force_reparse": "true"}

        errors = validate_parsing_request(data)

        assert len(errors) == 1
        assert "force_reparse должен быть boolean" in errors[0]

    def test_multiple_validation_errors(self):
        """Test validation with multiple errors"""
        data = {
            "group_ids": [],
            "max_posts": 0,
            "max_comments_per_post": 2000,
            "priority": "invalid",
            "force_reparse": "not_boolean",
        }

        errors = validate_parsing_request(data)

        assert len(errors) == 6


class TestCalculateTaskProgress:
    """Test suite for calculate_task_progress function"""

    def test_zero_groups_completed(self):
        """Test progress calculation with no groups completed"""
        progress = calculate_task_progress(groups_completed=0, groups_total=5)

        assert progress == 0.0

    def test_half_groups_completed(self):
        """Test progress calculation with half groups completed"""
        progress = calculate_task_progress(groups_completed=2, groups_total=4)

        assert progress == 50.0

    def test_all_groups_completed(self):
        """Test progress calculation with all groups completed"""
        progress = calculate_task_progress(groups_completed=3, groups_total=3)

        assert progress == 100.0

    def test_progress_with_posts_and_comments(self):
        """Test progress calculation with posts and comments data"""
        progress = calculate_task_progress(
            groups_completed=1,
            groups_total=2,
            posts_found=50,
            comments_found=200,
        )

        # Should still base calculation on groups, not posts/comments
        assert progress == 50.0

    def test_single_group(self):
        """Test progress calculation with single group"""
        progress = calculate_task_progress(groups_completed=0, groups_total=1)

        assert progress == 0.0

        progress = calculate_task_progress(groups_completed=1, groups_total=1)

        assert progress == 100.0


class TestEstimateParsingTime:
    """Test suite for estimate_parsing_time function"""

    def test_estimate_for_single_group(self):
        """Test time estimation for single group"""
        result = estimate_parsing_time([123])

        assert result == 30  # 30 seconds per group

    def test_estimate_for_multiple_groups(self):
        """Test time estimation for multiple groups"""
        result = estimate_parsing_time([123, 456, 789])

        assert (
            result == 76
        )  # 153 API calls * 0.5 seconds per call, max with 30

    def test_estimate_for_empty_groups(self):
        """Test time estimation for empty group list"""
        result = estimate_parsing_time([])

        assert result == 0


class TestSanitizeVKText:
    """Test suite for sanitize_vk_text function"""

    def test_sanitize_normal_text(self):
        """Test sanitizing normal text"""
        text = "Normal text with spaces"
        result = sanitize_vk_text(text)

        assert result == text

    def test_sanitize_text_with_newlines(self):
        """Test sanitizing text with newlines"""
        text = "Line 1\nLine 2\n\nLine 3"
        result = sanitize_vk_text(text)

        assert result == "Line 1 Line 2  Line 3"

    def test_sanitize_text_with_html(self):
        """Test sanitizing text with HTML tags"""
        text = "Text with <b>bold</b> and <i>italic</i> tags"
        result = sanitize_vk_text(text)

        assert "<b>" not in result
        assert "<i>" not in result
        assert result == "Text with bold and italic tags"

    def test_sanitize_text_with_emojis(self):
        """Test sanitizing text with emojis"""
        text = "Text with 😀 emoji"
        result = sanitize_vk_text(text)

        assert result == text  # Emojis should be preserved

    def test_sanitize_empty_text(self):
        """Test sanitizing empty text"""
        result = sanitize_vk_text("")

        assert result == ""

    def test_sanitize_none_text(self):
        """Test sanitizing None text"""
        result = sanitize_vk_text(None)

        assert result == ""


class TestExtractVKEntities:
    """Test suite for extract_vk_entities function"""

    def test_extract_mentions(self):
        """Test extracting mentions from text"""
        text = "Hello @username and @another_user!"
        result = extract_vk_entities(text)

        assert "mentions" in result
        assert "@username" in result["mentions"]
        assert "@another_user" in result["mentions"]

    def test_extract_hashtags(self):
        """Test extracting hashtags from text"""
        text = "Check out #hashtag1 and #hashtag2"
        result = extract_vk_entities(text)

        assert "hashtags" in result
        assert "#hashtag1" in result["hashtags"]
        assert "#hashtag2" in result["hashtags"]

    def test_extract_links(self):
        """Test extracting links from text"""
        text = "Visit https://example.com and http://test.org"
        result = extract_vk_entities(text)

        assert "links" in result
        assert "https://example.com" in result["links"]
        assert "http://test.org" in result["links"]

    def test_extract_empty_text(self):
        """Test extracting entities from empty text"""
        result = extract_vk_entities("")

        assert result["mentions"] == []
        assert result["hashtags"] == []
        assert result["links"] == []


class TestValidateVKGroupId:
    """Test suite for validate_vk_group_id function"""

    def test_valid_group_id(self):
        """Test validation of valid VK group ID"""
        result = validate_vk_group_id(123456789)

        assert result is True

    def test_invalid_group_id_negative(self):
        """Test validation of negative group ID"""
        result = validate_vk_group_id(-123)

        assert result is False

    def test_invalid_group_id_zero(self):
        """Test validation of zero group ID"""
        result = validate_vk_group_id(0)

        assert result is False

    def test_invalid_group_id_too_large(self):
        """Test validation of too large group ID"""
        result = validate_vk_group_id(10**10)  # Very large number

        assert result is False


class TestValidateVKPostId:
    """Test suite for validate_vk_post_id function"""

    def test_valid_post_id(self):
        """Test validation of valid VK post ID"""
        result = validate_vk_post_id("wall123_456")

        assert result is True

    def test_valid_post_id_numeric(self):
        """Test validation of numeric post ID"""
        result = validate_vk_post_id("123456")

        assert result is True

    def test_invalid_post_id_empty(self):
        """Test validation of empty post ID"""
        result = validate_vk_post_id("")

        assert result is False

    def test_invalid_post_id_special_chars(self):
        """Test validation of post ID with special characters"""
        result = validate_vk_post_id("wall@123")

        assert result is False


class TestGenerateTaskSummary:
    """Test suite for generate_task_summary function"""

    def test_generate_summary_with_tasks(self):
        """Test generating summary with tasks"""
        tasks = [
            {
                "id": "task1",
                "status": "completed",
                "posts_found": 10,
                "comments_found": 50,
                "created_at": datetime.utcnow(),
                "errors": [],
            },
            {
                "id": "task2",
                "status": "running",
                "posts_found": 5,
                "comments_found": 25,
                "created_at": datetime.utcnow(),
                "errors": ["Network error"],
            },
        ]

        result = generate_task_summary(tasks)

        assert result["total_tasks"] == 2
        assert result["completed_tasks"] == 1
        assert result["running_tasks"] == 1
        assert result["total_posts"] == 15
        assert result["total_comments"] == 75
        assert result["total_errors"] == 1

    def test_generate_summary_empty_tasks(self):
        """Test generating summary with empty tasks list"""
        result = generate_task_summary([])

        assert result["total_tasks"] == 0
        assert result["completed_tasks"] == 0
        assert result["running_tasks"] == 0
        assert result["total_posts"] == 0
        assert result["total_comments"] == 0
        assert result["total_errors"] == 0


class TestCreateParsingReport:
    """Test suite for create_parsing_report function"""

    def test_create_report(self):
        """Test creating parsing report"""
        parsing_data = {
            "group_id": 123456789,
            "posts_found": 25,
            "comments_found": 150,
            "posts_saved": 25,
            "comments_saved": 150,
            "errors": ["Minor parsing error"],
            "duration_seconds": 45.5,
        }

        result = create_parsing_report(parsing_data)

        assert result["group_id"] == 123456789
        assert result["posts_found"] == 25
        assert result["comments_found"] == 150
        assert result["success_rate"] == 100.0
        assert result["average_comments_per_post"] == 6.0
        assert result["duration_seconds"] == 45.5
        assert len(result["errors"]) == 1

    def test_create_report_with_errors(self):
        """Test creating parsing report with errors"""
        parsing_data = {
            "group_id": 123456789,
            "posts_found": 20,
            "comments_found": 100,
            "posts_saved": 15,
            "comments_saved": 80,
            "errors": ["Network timeout", "Invalid data"],
            "duration_seconds": 30.0,
        }

        result = create_parsing_report(parsing_data)

        assert result["success_rate"] == 75.0  # 15/20 * 100
        assert result["average_comments_per_post"] == 5.0
        assert len(result["errors"]) == 2

    def test_create_report_zero_posts(self):
        """Test creating parsing report with zero posts"""
        parsing_data = {
            "group_id": 123456789,
            "posts_found": 0,
            "comments_found": 0,
            "posts_saved": 0,
            "comments_saved": 0,
            "errors": [],
            "duration_seconds": 10.0,
        }

        result = create_parsing_report(parsing_data)

        assert result["success_rate"] == 0.0
        assert result["average_comments_per_post"] == 0.0
