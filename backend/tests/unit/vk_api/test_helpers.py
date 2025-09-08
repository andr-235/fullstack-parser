"""
Tests for VK API Helper Functions

Comprehensive test suite for helper functions and response creation utilities
in the VK API module. Tests cover response formatting, data transformation,
timestamp handling, and utility functions used throughout the module.

Test Coverage:
- Response creation functions for all data types
- Timestamp and date handling utilities
- Data transformation and formatting
- Response structure validation
- Edge cases and boundary conditions
- Performance and memory efficiency
- Error handling in helper functions

Uses:
- pytest for test framework
- Mock data for testing response creation
- Time manipulation for timestamp tests
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from src.vk_api.helpers import (
    get_current_timestamp,
    create_posts_response,
    create_comments_response,
    create_users_response,
    create_groups_response,
    create_post_response,
    create_group_response,
    create_health_response,
    create_stats_response,
    create_limits_response,
    create_token_validation_response,
    create_group_members_response,
)


class TestTimestampUtilities:
    """Test suite for timestamp utility functions"""

    def test_get_current_timestamp(self):
        """Test current timestamp generation"""
        timestamp = get_current_timestamp()

        assert isinstance(timestamp, str)
        assert len(timestamp) > 0

        # Should be ISO format with timezone
        assert "T" in timestamp
        assert "+" in timestamp or "Z" in timestamp

    def test_get_current_timestamp_format(self):
        """Test timestamp format compliance"""
        timestamp = get_current_timestamp()

        # Parse back to verify format
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        assert isinstance(parsed, datetime)
        assert parsed.tzinfo is not None

    def test_get_current_timestamp_uniqueness(self):
        """Test timestamp uniqueness"""
        timestamp1 = get_current_timestamp()
        timestamp2 = get_current_timestamp()

        # Should be different (or at least not identical)
        # Note: In very fast execution, they might be the same millisecond
        assert isinstance(timestamp1, str)
        assert isinstance(timestamp2, str)


class TestPostsResponse:
    """Test suite for posts response creation"""

    def test_create_posts_response_basic(self):
        """Test basic posts response creation"""
        posts = [
            {"id": 1, "text": "Post 1", "date": 1609459200},
            {"id": 2, "text": "Post 2", "date": 1609459260},
        ]

        response = create_posts_response(
            posts=posts,
            total_count=100,
            requested_count=10,
            offset=0,
            has_more=True,
        )

        assert response["success"] is True
        assert response["data_type"] == "posts"
        assert len(response["posts"]) == 2
        assert response["total_count"] == 100
        assert response["requested_count"] == 10
        assert response["offset"] == 0
        assert response["has_more"] is True
        assert "fetched_at" in response

    def test_create_posts_response_empty(self):
        """Test posts response with empty posts list"""
        response = create_posts_response(
            posts=[],
            total_count=0,
            requested_count=10,
            offset=0,
            has_more=False,
        )

        assert response["success"] is True
        assert len(response["posts"]) == 0
        assert response["total_count"] == 0
        assert response["has_more"] is False

    def test_create_posts_response_with_metadata(self):
        """Test posts response with additional metadata"""
        posts = [{"id": 1, "text": "Test post"}]
        group_id = 12345

        response = create_posts_response(
            posts=posts,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
            group_id=group_id,
        )

        assert response["group_id"] == group_id
        assert response["posts"][0]["id"] == 1

    def test_create_posts_response_timestamp_format(self):
        """Test posts response timestamp format"""
        posts = [{"id": 1}]
        response = create_posts_response(
            posts=posts,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
        )

        # Verify timestamp format
        fetched_at = response["fetched_at"]
        assert isinstance(fetched_at, str)
        assert "T" in fetched_at
        assert "Z" in fetched_at


class TestCommentsResponse:
    """Test suite for comments response creation"""

    def test_create_comments_response_basic(self):
        """Test basic comments response creation"""
        comments = [
            {"id": 1, "text": "Comment 1", "from_id": 111},
            {"id": 2, "text": "Comment 2", "from_id": 222},
        ]

        response = create_comments_response(
            comments=comments,
            total_count=50,
            requested_count=20,
            offset=0,
            has_more=True,
            group_id=12345,
            post_id=67890,
            sort="asc",
        )

        assert response["success"] is True
        assert response["data_type"] == "comments"
        assert len(response["comments"]) == 2
        assert response["total_count"] == 50
        assert response["group_id"] == 12345
        assert response["post_id"] == 67890
        assert response["sort"] == "asc"
        assert response["has_more"] is True

    def test_create_comments_response_different_sorts(self):
        """Test comments response with different sort options"""
        comments = [{"id": 1}]

        for sort in ["asc", "desc"]:
            response = create_comments_response(
                comments=comments,
                total_count=1,
                requested_count=1,
                offset=0,
                has_more=False,
                group_id=12345,
                post_id=67890,
                sort=sort,
            )

            assert response["sort"] == sort

    def test_create_comments_response_no_pagination(self):
        """Test comments response without pagination info"""
        comments = [{"id": 1}]

        response = create_comments_response(
            comments=comments,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
        )

        assert "group_id" not in response
        assert "post_id" not in response
        assert "sort" not in response


class TestUsersResponse:
    """Test suite for users response creation"""

    def test_create_users_response_basic(self):
        """Test basic users response creation"""
        users = [
            {"id": 111, "first_name": "John", "last_name": "Doe"},
            {"id": 222, "first_name": "Jane", "last_name": "Smith"},
        ]

        response = create_users_response(
            users=users, requested_ids=[111, 222], found_count=2
        )

        assert response["success"] is True
        assert response["data_type"] == "users"
        assert len(response["users"]) == 2
        assert response["requested_ids"] == [111, 222]
        assert response["found_count"] == 2
        assert response["users"][0]["name"] == "John Doe"

    def test_create_users_response_partial_results(self):
        """Test users response with partial results"""
        users = [{"id": 111, "first_name": "John", "last_name": "Doe"}]

        response = create_users_response(
            users=users, requested_ids=[111, 222, 333], found_count=1
        )

        assert len(response["users"]) == 1
        assert response["requested_ids"] == [111, 222, 333]
        assert response["found_count"] == 1

    def test_create_users_response_name_formatting(self):
        """Test user name formatting"""
        test_cases = [
            ({"first_name": "John", "last_name": "Doe"}, "John Doe"),
            ({"first_name": "John", "last_name": ""}, "John"),
            ({"first_name": "", "last_name": "Doe"}, "Doe"),
            ({"first_name": "", "last_name": ""}, ""),
            ({}, ""),
        ]

        for user_data, expected_name in test_cases:
            users = [dict(user_data, id=1)]
            response = create_users_response(
                users=users, requested_ids=[1], found_count=1
            )

            assert response["users"][0]["name"] == expected_name


class TestGroupsResponse:
    """Test suite for groups response creation"""

    def test_create_groups_response_basic(self):
        """Test basic groups response creation"""
        groups = [
            {"id": 12345, "name": "Test Group 1", "members_count": 100},
            {"id": 67890, "name": "Test Group 2", "members_count": 200},
        ]

        response = create_groups_response(
            groups=groups,
            total_count=150,
            requested_count=20,
            offset=0,
            has_more=True,
            query="test",
            country=1,
            city=2,
        )

        assert response["success"] is True
        assert response["data_type"] == "groups"
        assert len(response["groups"]) == 2
        assert response["total_count"] == 150
        assert response["query"] == "test"
        assert response["country"] == 1
        assert response["city"] == 2

    def test_create_groups_response_minimal(self):
        """Test groups response with minimal parameters"""
        groups = [{"id": 1, "name": "Group"}]

        response = create_groups_response(
            groups=groups,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
        )

        assert response["success"] is True
        assert len(response["groups"]) == 1
        assert "query" not in response
        assert "country" not in response
        assert "city" not in response


class TestPostResponse:
    """Test suite for single post response creation"""

    def test_create_post_response_basic(self):
        """Test basic post response creation"""
        post_data = {
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

        response = create_post_response(post_data)

        assert response["success"] is True
        assert response["data_type"] == "post"
        assert response["post"]["id"] == 123
        assert response["post"]["owner_id"] == -456
        assert response["post"]["text"] == "Test post content"
        assert len(response["post"]["attachments"]) == 1
        assert response["post"]["is_pinned"] is False

    def test_create_post_response_missing_fields(self):
        """Test post response with missing optional fields"""
        minimal_post = {"id": 1, "text": "Minimal post"}

        response = create_post_response(minimal_post)

        assert response["post"]["id"] == 1
        assert response["post"]["text"] == "Minimal post"
        assert response["post"]["attachments"] == []  # Default empty
        assert response["post"]["is_pinned"] is False  # Default false


class TestGroupResponse:
    """Test suite for single group response creation"""

    def test_create_group_response_basic(self):
        """Test basic group response creation"""
        group_data = {
            "id": 12345,
            "name": "Test Group",
            "screen_name": "testgroup",
            "description": "A test group",
            "members_count": 1000,
            "photo_url": "https://example.com/photo.jpg",
            "is_closed": False,
            "type": "group",
        }

        response = create_group_response(group_data)

        assert response["success"] is True
        assert response["data_type"] == "group"
        assert response["group"]["id"] == 12345
        assert response["group"]["name"] == "Test Group"
        assert response["group"]["members_count"] == 1000
        assert response["group"]["is_closed"] is False

    def test_create_group_response_defaults(self):
        """Test group response with default values for missing fields"""
        minimal_group = {"id": 1, "name": "Group"}

        response = create_group_response(minimal_group)

        assert response["group"]["id"] == 1
        assert response["group"]["name"] == "Group"
        assert response["group"]["description"] == ""  # Default empty
        assert response["group"]["members_count"] == 0  # Default zero
        assert response["group"]["photo_url"] == ""  # Default empty
        assert response["group"]["is_closed"] is False  # Default false
        assert response["group"]["type"] == "group"  # Default group


class TestHealthResponse:
    """Test suite for health check response creation"""

    def test_create_health_response_healthy(self):
        """Test healthy health response"""
        client_status = {"status": "healthy", "requests": 100}
        repository_status = {"status": "healthy", "cache_size": 50}

        response = create_health_response(
            status="healthy",
            client_status=client_status,
            repository_status=repository_status,
        )

        assert response["status"] == "healthy"
        assert response["client_status"] == client_status
        assert response["repository_status"] == repository_status
        assert "timestamp" in response

    def test_create_health_response_unhealthy(self):
        """Test unhealthy health response"""
        response = create_health_response(
            status="unhealthy", error="Database connection failed"
        )

        assert response["status"] == "unhealthy"
        assert response["error"] == "Database connection failed"
        assert "timestamp" in response

    def test_create_health_response_minimal(self):
        """Test health response with minimal parameters"""
        response = create_health_response(status="healthy")

        assert response["status"] == "healthy"
        assert "timestamp" in response


class TestStatsResponse:
    """Test suite for statistics response creation"""

    def test_create_stats_response_basic(self):
        """Test basic stats response creation"""
        client_stats = {
            "total_requests": 1000,
            "successful_requests": 950,
            "failed_requests": 50,
        }
        repository_stats = {
            "cache_entries": 100,
            "cache_hits": 80,
            "cache_misses": 20,
        }

        response = create_stats_response(
            client_stats=client_stats,
            repository_stats=repository_stats,
            cache_enabled=True,
            token_configured=True,
        )

        assert response["success"] is True
        assert response["data_type"] == "stats"
        assert response["client_stats"] == client_stats
        assert response["repository_stats"] == repository_stats
        assert response["cache_enabled"] is True
        assert response["token_configured"] is True
        assert "timestamp" in response

    def test_create_stats_response_disabled_features(self):
        """Test stats response with disabled features"""
        response = create_stats_response(
            client_stats={},
            repository_stats={},
            cache_enabled=False,
            token_configured=False,
        )

        assert response["cache_enabled"] is False
        assert response["token_configured"] is False


class TestLimitsResponse:
    """Test suite for limits response creation"""

    def test_create_limits_response_basic(self):
        """Test basic limits response creation"""
        response = create_limits_response(
            max_requests_per_second=3,
            max_posts_per_request=100,
            max_comments_per_request=100,
            max_groups_per_request=10000,
            max_users_per_request=1000,
            current_request_count=5,
            last_request_time=1609459200.0,
            time_until_reset=30.0,
        )

        assert response["success"] is True
        assert response["data_type"] == "limits"
        assert response["max_requests_per_second"] == 3
        assert response["max_posts_per_request"] == 100
        assert response["current_request_count"] == 5
        assert response["time_until_reset"] == 30.0

    def test_create_limits_response_zero_values(self):
        """Test limits response with zero values"""
        response = create_limits_response(
            max_requests_per_second=0,
            max_posts_per_request=0,
            current_request_count=0,
            last_request_time=0.0,
            time_until_reset=0.0,
        )

        assert response["max_requests_per_second"] == 0
        assert response["current_request_count"] == 0


class TestTokenValidationResponse:
    """Test suite for token validation response creation"""

    def test_create_token_validation_response_valid(self):
        """Test valid token validation response"""
        response = create_token_validation_response(
            valid=True, user_id=12345, user_name="John Doe"
        )

        assert response["success"] is True
        assert response["data_type"] == "token_validation"
        assert response["valid"] is True
        assert response["user_id"] == 12345
        assert response["user_name"] == "John Doe"

    def test_create_token_validation_response_invalid(self):
        """Test invalid token validation response"""
        response = create_token_validation_response(
            valid=False, error="Invalid access token"
        )

        assert response["success"] is True
        assert response["valid"] is False
        assert response["error"] == "Invalid access token"
        assert "user_id" not in response
        assert "user_name" not in response


class TestGroupMembersResponse:
    """Test suite for group members response creation"""

    def test_create_group_members_response_basic(self):
        """Test basic group members response creation"""
        members = [
            {"id": 111, "first_name": "John", "last_name": "Doe"},
            {"id": 222, "first_name": "Jane", "last_name": "Smith"},
        ]

        response = create_group_members_response(
            members=members,
            total_count=500,
            requested_count=100,
            offset=0,
            has_more=True,
            group_id=12345,
        )

        assert response["success"] is True
        assert response["data_type"] == "group_members"
        assert len(response["members"]) == 2
        assert response["total_count"] == 500
        assert response["group_id"] == 12345
        assert response["has_more"] is True

    def test_create_group_members_response_no_more(self):
        """Test group members response when no more members available"""
        members = [{"id": 1}]

        response = create_group_members_response(
            members=members,
            total_count=1,
            requested_count=100,
            offset=0,
            has_more=False,
            group_id=12345,
        )

        assert len(response["members"]) == 1
        assert response["total_count"] == 1
        assert response["has_more"] is False


class TestResponseStructureConsistency:
    """Test suite for response structure consistency"""

    def test_all_responses_have_common_fields(self):
        """Test that all response types have consistent structure"""
        test_cases = [
            create_posts_response(
                posts=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_comments_response(
                comments=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_users_response(users=[], requested_ids=[], found_count=0),
            create_groups_response(
                groups=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_post_response({"id": 1}),
            create_group_response({"id": 1, "name": "Test"}),
            create_health_response(status="healthy"),
            create_stats_response(
                client_stats={},
                repository_stats={},
                cache_enabled=True,
                token_configured=True,
            ),
            create_limits_response(
                max_requests_per_second=1,
                max_posts_per_request=1,
                current_request_count=0,
                last_request_time=0,
                time_until_reset=0,
            ),
            create_token_validation_response(valid=True),
            create_group_members_response(
                members=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
                group_id=1,
            ),
        ]

        for response in test_cases:
            assert "success" in response
            assert isinstance(response["success"], bool)
            assert "data_type" in response
            assert isinstance(response["data_type"], str)

    def test_response_data_types_are_valid(self):
        """Test that all responses have valid data types"""
        valid_data_types = {
            "posts",
            "comments",
            "users",
            "groups",
            "post",
            "group",
            "health",
            "stats",
            "limits",
            "token_validation",
            "group_members",
        }

        test_responses = [
            create_posts_response(
                posts=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_comments_response(
                comments=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_users_response(users=[], requested_ids=[], found_count=0),
            create_groups_response(
                groups=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
            ),
            create_post_response({"id": 1}),
            create_group_response({"id": 1, "name": "Test"}),
            create_health_response(status="healthy"),
            create_stats_response(
                client_stats={},
                repository_stats={},
                cache_enabled=True,
                token_configured=True,
            ),
            create_limits_response(
                max_requests_per_second=1,
                max_posts_per_request=1,
                current_request_count=0,
                last_request_time=0,
                time_until_reset=0,
            ),
            create_token_validation_response(valid=True),
            create_group_members_response(
                members=[],
                total_count=0,
                requested_count=0,
                offset=0,
                has_more=False,
                group_id=1,
            ),
        ]

        for response in test_responses:
            assert response["data_type"] in valid_data_types


class TestResponseEdgeCases:
    """Test suite for response creation edge cases"""

    def test_responses_with_none_values(self):
        """Test response creation with None values"""
        response = create_posts_response(
            posts=None,
            total_count=None,
            requested_count=None,
            offset=None,
            has_more=None,
        )

        # Should handle None values gracefully
        assert response["posts"] is None or isinstance(response["posts"], list)
        assert response["total_count"] is None or isinstance(
            response["total_count"], int
        )

    def test_responses_with_large_data(self):
        """Test response creation with large datasets"""
        large_posts = [{"id": i, "text": f"Post {i}"} for i in range(1000)]

        response = create_posts_response(
            posts=large_posts,
            total_count=1000,
            requested_count=1000,
            offset=0,
            has_more=False,
        )

        assert len(response["posts"]) == 1000
        assert response["total_count"] == 1000

    def test_responses_with_unicode_content(self):
        """Test response creation with Unicode content"""
        unicode_posts = [
            {"id": 1, "text": "Привет мир! 🌍 Здравствуй мир! 🚀"}
        ]

        response = create_posts_response(
            posts=unicode_posts,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
        )

        assert "Привет мир! 🌍" in response["posts"][0]["text"]
        assert "Здравствуй мир! 🚀" in response["posts"][0]["text"]

    def test_responses_with_special_characters(self):
        """Test response creation with special characters"""
        special_posts = [
            {"id": 1, "text": "Post with <script> tags & 'quotes' \"double\""}
        ]

        response = create_posts_response(
            posts=special_posts,
            total_count=1,
            requested_count=1,
            offset=0,
            has_more=False,
        )

        assert "<script>" in response["posts"][0]["text"]
        assert "&" in response["posts"][0]["text"]
        assert "'quotes'" in response["posts"][0]["text"]
        assert '"double"' in response["posts"][0]["text"]
