"""
Tests for VK API Exceptions and Error Handling

Comprehensive test suite for custom exceptions in the VK API module.
Tests cover exception creation, inheritance, error codes, serialization,
and error handling patterns throughout the application.

Test Coverage:
- VKAPIError and its subclasses
- Error code mappings and handling
- Exception serialization for API responses
- Error message formatting
- Exception chaining and context preservation
- HTTP status code mappings
- Error logging and monitoring
- Exception handling in different contexts

Uses:
- pytest for test framework
- Custom exception classes from vk_api.exceptions
- Error code constants and mappings
"""

import pytest
import json
from typing import Dict, Any, Optional

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
)


class TestVKAPIError:
    """Test suite for base VKAPIError class"""

    def test_vk_api_error_basic(self):
        """Test basic VKAPIError creation"""
        error = VKAPIError("Test error message")

        assert error.detail == "VK API Error: Test error message"
        assert error.status_code == 502
        assert error.error_code == "VK_API_ERROR"
        assert error.details["message"] == "Test error message"

    def test_vk_api_error_with_code(self):
        """Test VKAPIError with error code"""
        error = VKAPIError("Test error", error_code=123)

        assert error.details["vk_error_code"] == 123

    def test_vk_api_error_with_method(self):
        """Test VKAPIError with method context"""
        error = VKAPIError("Test error", method="wall.get")

        assert error.details["method"] == "wall.get"

    def test_vk_api_error_with_details(self):
        """Test VKAPIError with additional details"""
        details = {"extra": "info", "context": "test"}
        error = VKAPIError("Test error", details=details)

        assert error.details["details"] == details

    def test_vk_api_error_full_context(self):
        """Test VKAPIError with all parameters"""
        details = {"param": "value"}
        error = VKAPIError(
            message="Full test error",
            error_code=456,
            method="groups.getById",
            details=details,
        )

        assert error.message == "VK API Error: Full test error"
        assert error.details["vk_error_code"] == 456
        assert error.details["method"] == "groups.getById"
        assert error.details["details"] == details

    def test_vk_api_error_serialization(self):
        """Test VKAPIError serialization"""
        error = VKAPIError("Test error", error_code=123, method="test.method")

        # Test that it can be properly serialized
        error_dict = {
            "status_code": error.status_code,
            "error_code": error.error_code,
            "message": error.message,
            "details": error.details,
        }

        # Should be JSON serializable
        json_str = json.dumps(error_dict)
        parsed = json.loads(json_str)

        assert parsed["status_code"] == 502
        assert parsed["error_code"] == "VK_API_ERROR"
        assert "Test error" in parsed["message"]
        assert parsed["details"]["vk_error_code"] == 123


class TestVKAPIRateLimitError:
    """Test suite for VKAPIRateLimitError"""

    def test_rate_limit_error_basic(self):
        """Test basic rate limit error"""
        error = VKAPIRateLimitError()

        assert error.status_code == 429
        assert error.error_code == "VK_API_RATE_LIMIT"
        assert error.error_type == "rate_limit"
        assert "rate limit" in error.message.lower()

    def test_rate_limit_error_with_wait_time(self):
        """Test rate limit error with wait time"""
        error = VKAPIRateLimitError(wait_time=30.5)

        assert "30.5 seconds" in error.message
        assert error.details["wait_time"] == 30.5

    def test_rate_limit_error_with_method(self):
        """Test rate limit error with method context"""
        error = VKAPIRateLimitError(method="wall.get", wait_time=60.0)

        assert error.details["method"] == "wall.get"
        assert error.details["wait_time"] == 60.0


class TestVKAPIAuthError:
    """Test suite for VKAPIAuthError"""

    def test_auth_error_basic(self):
        """Test basic authentication error"""
        error = VKAPIAuthError("Invalid token")

        assert error.status_code == 401
        assert error.error_code == "VK_API_AUTH"
        assert error.details["error_type"] == "auth"
        assert "authentication" in error.message.lower()

    def test_auth_error_with_method(self):
        """Test auth error with method context"""
        error = VKAPIAuthError("Token expired", method="users.get")

        assert error.details["method"] == "users.get"


class TestVKAPIAccessDeniedError:
    """Test suite for VKAPIAccessDeniedError"""

    def test_access_denied_error_basic(self):
        """Test basic access denied error"""
        error = VKAPIAccessDeniedError("Access denied to group")

        assert error.status_code == 403
        assert error.error_code == "VK_API_ACCESS_DENIED"
        assert error.details["error_type"] == "access_denied"
        assert "access denied" in error.message.lower()

    def test_access_denied_error_with_method(self):
        """Test access denied error with method context"""
        error = VKAPIAccessDeniedError("Private group", method="wall.get")

        assert error.details["method"] == "wall.get"


class TestVKAPIInvalidTokenError:
    """Test suite for VKAPIInvalidTokenError"""

    def test_invalid_token_error_basic(self):
        """Test basic invalid token error"""
        error = VKAPIInvalidTokenError("Token is invalid")

        assert error.status_code == 401
        assert error.error_code == "VK_API_INVALID_TOKEN"
        assert error.details["error_type"] == "invalid_token"
        assert "invalid token" in error.message.lower()


class TestVKAPIInvalidParamsError:
    """Test suite for VKAPIInvalidParamsError"""

    def test_invalid_params_error_basic(self):
        """Test basic invalid parameters error"""
        error = VKAPIInvalidParamsError("Invalid group_id")

        assert error.status_code == 400
        assert error.error_code == "VK_API_INVALID_PARAMS"
        assert error.details["error_type"] == "invalid_params"
        assert "invalid parameters" in error.message.lower()

    def test_invalid_params_error_with_field(self):
        """Test invalid params error with field information"""
        error = VKAPIInvalidParamsError("Invalid count value", field="count")

        assert error.details["field"] == "count"


class TestVKAPITimeoutError:
    """Test suite for VKAPITimeoutError"""

    def test_timeout_error_basic(self):
        """Test basic timeout error"""
        error = VKAPITimeoutError("Request timed out")

        assert error.status_code == 504
        assert error.error_code == "VK_API_TIMEOUT"
        assert error.details["error_type"] == "timeout"
        assert "timeout" in error.message.lower()

    def test_timeout_error_with_timeout_value(self):
        """Test timeout error with timeout value"""
        error = VKAPITimeoutError("Request timed out", timeout=30.0)

        assert error.details["timeout"] == 30.0


class TestVKAPINetworkError:
    """Test suite for VKAPINetworkError"""

    def test_network_error_basic(self):
        """Test basic network error"""
        error = VKAPINetworkError("Connection failed")

        assert error.status_code == 502
        assert error.error_code == "VK_API_NETWORK"
        assert error.details["error_type"] == "network"
        assert "network" in error.message.lower()


class TestVKAPIInvalidResponseError:
    """Test suite for VKAPIInvalidResponseError"""

    def test_invalid_response_error_basic(self):
        """Test basic invalid response error"""
        error = VKAPIInvalidResponseError("Invalid JSON response")

        assert error.status_code == 502
        assert error.error_code == "VK_API_INVALID_RESPONSE"
        assert error.details["error_type"] == "invalid_response"
        assert "invalid response" in error.message.lower()


class TestExceptionInheritance:
    """Test suite for exception inheritance hierarchy"""

    def test_all_exceptions_inherit_from_vkapi_error(self):
        """Test that all VK API exceptions inherit from VKAPIError"""
        exceptions = [
            VKAPIRateLimitError(),
            VKAPIAuthError("test"),
            VKAPIAccessDeniedError("test"),
            VKAPIInvalidTokenError("test"),
            VKAPIInvalidParamsError("test"),
            VKAPITimeoutError("test"),
            VKAPINetworkError("test"),
            VKAPIInvalidResponseError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, VKAPIError)

    def test_exception_chaining(self):
        """Test exception chaining and context preservation"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise VKAPIError("Wrapped error") from e
        except VKAPIError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"


class TestErrorCodeMappings:
    """Test suite for error code mappings and constants"""

    def test_vk_error_constants(self):
        """Test VK error code constants"""
        assert VK_ERROR_ACCESS_DENIED == 15
        assert VK_ERROR_INVALID_REQUEST == 100
        assert VK_ERROR_TOO_MANY_REQUESTS == 6
        assert VK_ERROR_AUTH_FAILED == 5
        assert VK_ERROR_PERMISSION_DENIED == 7

    def test_error_code_to_exception_mapping(self):
        """Test mapping of VK error codes to appropriate exceptions"""
        error_mappings = {
            VK_ERROR_TOO_MANY_REQUESTS: VKAPIRateLimitError,
            VK_ERROR_AUTH_FAILED: VKAPIAuthError,
            VK_ERROR_ACCESS_DENIED: VKAPIAccessDeniedError,
            VK_ERROR_PERMISSION_DENIED: VKAPIAccessDeniedError,
            VK_ERROR_INVALID_REQUEST: VKAPIInvalidParamsError,
        }

        for error_code, exception_class in error_mappings.items():
            error = exception_class(f"Error {error_code}")
            assert error.details["error_type"] in [
                "rate_limit",
                "auth",
                "access_denied",
                "invalid_params",
            ]


class TestExceptionContextAndLogging:
    """Test suite for exception context and logging"""

    def test_exception_with_request_context(self):
        """Test exception with full request context"""
        error = VKAPIError(
            message="Request failed",
            error_code=123,
            method="wall.get",
            details={
                "request_params": {"owner_id": -12345, "count": 10},
                "response_time": 2.5,
                "user_id": 67890,
                "ip_address": "192.168.1.100",
            },
        )

        assert error.details["method"] == "wall.get"
        assert error.details["vk_error_code"] == 123
        assert error.details["details"]["request_params"]["owner_id"] == -12345
        assert error.details["details"]["response_time"] == 2.5

    def test_exception_for_audit_logging(self):
        """Test exception formatting for audit logging"""
        error = VKAPIRateLimitError(wait_time=30.0, method="groups.search")

        # Should contain all necessary information for logging
        log_context = {
            "error_type": error.details["error_type"],
            "error_code": error.error_code,
            "method": error.details.get("method"),
            "wait_time": error.details.get("wait_time"),
            "timestamp": "2024-01-01T12:00:00Z",  # Would be added by logger
            "severity": "warning",
        }

        assert log_context["error_type"] == "rate_limit"
        assert log_context["error_code"] == "VK_API_RATE_LIMIT"
        assert log_context["method"] == "groups.search"
        assert log_context["wait_time"] == 30.0


class TestExceptionHTTPStatusCodes:
    """Test suite for HTTP status code mappings"""

    def test_http_status_codes(self):
        """Test correct HTTP status codes for different error types"""
        status_mappings = {
            VKAPIRateLimitError(): 429,  # Too Many Requests
            VKAPIAuthError("test"): 401,  # Unauthorized
            VKAPIAccessDeniedError("test"): 403,  # Forbidden
            VKAPIInvalidTokenError("test"): 401,  # Unauthorized
            VKAPIInvalidParamsError("test"): 400,  # Bad Request
            VKAPITimeoutError("test"): 504,  # Gateway Timeout
            VKAPINetworkError("test"): 502,  # Bad Gateway
            VKAPIInvalidResponseError("test"): 502,  # Bad Gateway
            VKAPIError("test"): 502,  # Bad Gateway (default)
        }

        for exception, expected_status in status_mappings.items():
            assert exception.status_code == expected_status

    def test_error_code_consistency(self):
        """Test error code consistency across exception types"""
        exceptions = [
            (VKAPIRateLimitError(), "VK_API_RATE_LIMIT"),
            (VKAPIAuthError("test"), "VK_API_AUTH"),
            (VKAPIAccessDeniedError("test"), "VK_API_ACCESS_DENIED"),
            (VKAPIInvalidTokenError("test"), "VK_API_INVALID_TOKEN"),
            (VKAPIInvalidParamsError("test"), "VK_API_INVALID_PARAMS"),
            (VKAPITimeoutError("test"), "VK_API_TIMEOUT"),
            (VKAPINetworkError("test"), "VK_API_NETWORK"),
            (VKAPIInvalidResponseError("test"), "VK_API_INVALID_RESPONSE"),
        ]

        for exception, expected_code in exceptions:
            assert exception.error_code == expected_code


class TestExceptionDetailsStructure:
    """Test suite for exception details structure"""

    def test_exception_details_completeness(self):
        """Test that exception details contain all necessary information"""
        error = VKAPIError(
            message="Test error",
            error_code=123,
            method="test.method",
            details={"custom": "data"},
        )

        required_fields = ["message", "vk_error_code", "method", "details"]

        for field in required_fields:
            assert field in error.details

    def test_exception_details_types(self):
        """Test that exception details have correct types"""
        error = VKAPIError("Test", error_code=123, method="test")

        assert isinstance(error.details["message"], str)
        assert isinstance(error.details["vk_error_code"], int)
        assert isinstance(error.details["method"], str)
        assert isinstance(error.details["details"], dict)

    def test_exception_details_immutability(self):
        """Test that exception details are properly isolated"""
        original_details = {"key": "value"}
        error = VKAPIError("Test", details=original_details)

        # Modify original dict
        original_details["key"] = "modified"

        # Error details should remain unchanged
        assert error.details["details"]["key"] == "value"


class TestExceptionEdgeCases:
    """Test suite for exception edge cases and boundary conditions"""

    def test_exception_with_none_values(self):
        """Test exception creation with None values"""
        error = VKAPIError(
            message="Test", error_code=None, method=None, details=None
        )

        assert "vk_error_code" not in error.details
        assert "method" not in error.details
        assert "details" not in error.details

    def test_exception_with_empty_strings(self):
        """Test exception creation with empty strings"""
        error = VKAPIError(
            message="",
            method="",
        )

        assert error.message == "VK API Error: "
        assert error.details["method"] == ""

    def test_exception_with_large_details(self):
        """Test exception with large details dictionary"""
        large_details = {f"key{i}": f"value{i}" for i in range(100)}
        error = VKAPIError("Test", details=large_details)

        assert len(error.details["details"]) == 100
        assert error.details["details"]["key50"] == "value50"

    def test_exception_message_formatting(self):
        """Test exception message formatting with special characters"""
        special_messages = [
            "Error with quotes: 'test'",
            'Error with double quotes: "test"',
            "Error with newlines:\nline2",
            "Error with unicode: тест 🚀",
            "Error with HTML: <script>alert('xss')</script>",
        ]

        for message in special_messages:
            error = VKAPIError(message)
            assert message in error.message

    def test_exception_inheritance_depth(self):
        """Test deep exception inheritance"""
        # Create a chain of exceptions
        try:
            raise ValueError("Root cause")
        except ValueError as e1:
            try:
                raise RuntimeError("Intermediate") from e1
            except RuntimeError as e2:
                raise VKAPIError("Top level") from e2
        except VKAPIError as e:
            # Should preserve the entire chain
            assert e.__cause__ is not None
            assert e.__cause__.__cause__ is not None
            assert isinstance(e.__cause__.__cause__, ValueError)
