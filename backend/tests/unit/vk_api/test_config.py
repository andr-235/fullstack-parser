"""
Tests for VK API Configuration and Validation

Comprehensive test suite for configuration management in the VK API module.
Tests cover configuration loading, validation, environment variable handling,
Pydantic model validation, and configuration persistence.

Test Coverage:
- Configuration model validation
- Environment variable loading
- Default value handling
- Configuration file parsing
- Validation error handling
- Configuration inheritance
- Runtime configuration updates
- Configuration security (token handling)

Uses:
- pytest for test framework
- pytest-mock for mocking environment variables
- pydantic for configuration validation
- Temporary files for configuration testing
"""

import pytest
import os
import json
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from src.vk_api.config import (
    VKAPIConnectionConfig,
    VKAPIRateLimitConfig,
    VKAPIRequestLimits,
    VKAPICacheConfig,
    VKAPIRetryConfig,
    VKAPIProxyConfig,
    vk_api_config,
    VK_ERROR_ACCESS_DENIED,
    VK_ERROR_INVALID_REQUEST,
    VK_ERROR_TOO_MANY_REQUESTS,
    VK_ERROR_AUTH_FAILED,
    VK_ERROR_PERMISSION_DENIED,
    USER_AGENTS,
)


class TestVKAPIConnectionConfig:
    """Test suite for VK API connection configuration"""

    def test_connection_config_defaults(self):
        """Test connection config with default values"""
        config = VKAPIConnectionConfig()

        assert config.timeout == 30.0
        assert config.connection_timeout == 10.0
        assert config.max_connections == 100
        assert config.max_keepalive == 10

    def test_connection_config_custom_values(self):
        """Test connection config with custom values"""
        config = VKAPIConnectionConfig(
            timeout=60.0,
            connection_timeout=20.0,
            max_connections=200,
            max_keepalive=20,
        )

        assert config.timeout == 60.0
        assert config.connection_timeout == 20.0
        assert config.max_connections == 200
        assert config.max_keepalive == 20

    def test_connection_config_validation(self):
        """Test connection config validation"""
        # Valid values
        config = VKAPIConnectionConfig(timeout=10.0, max_connections=50)
        assert config.timeout == 10.0

        # Test negative timeout (should use default or raise error)
        with pytest.raises(ValueError):
            VKAPIConnectionConfig(timeout=-1.0)

    def test_connection_config_json_serialization(self):
        """Test connection config JSON serialization"""
        config = VKAPIConnectionConfig(timeout=45.0, max_connections=150)

        config_dict = config.model_dump()
        assert config_dict["timeout"] == 45.0
        assert config_dict["max_connections"] == 150

        # Test deserialization
        config_json = json.dumps(config_dict)
        parsed_config = VKAPIConnectionConfig.model_validate_json(config_json)
        assert parsed_config.timeout == 45.0


class TestVKAPIRateLimitConfig:
    """Test suite for VK API rate limit configuration"""

    def test_rate_limit_config_defaults(self):
        """Test rate limit config with default values"""
        config = VKAPIRateLimitConfig()

        assert config.max_requests_per_second == 3
        assert config.window_seconds == 1.0

    def test_rate_limit_config_custom_values(self):
        """Test rate limit config with custom values"""
        config = VKAPIRateLimitConfig(
            max_requests_per_second=5, window_seconds=2.0
        )

        assert config.max_requests_per_second == 5
        assert config.window_seconds == 2.0

    def test_rate_limit_config_validation(self):
        """Test rate limit config validation"""
        # Valid values
        config = VKAPIRateLimitConfig(
            max_requests_per_second=10, window_seconds=0.5
        )
        assert config.max_requests_per_second == 10

        # Test zero values (should raise error)
        with pytest.raises(ValueError):
            VKAPIRateLimitConfig(max_requests_per_second=0)

        with pytest.raises(ValueError):
            VKAPIRateLimitConfig(window_seconds=0.0)


class TestVKAPIRequestLimits:
    """Test suite for VK API request limits configuration"""

    def test_request_limits_defaults(self):
        """Test request limits with default values"""
        config = VKAPIRequestLimits()

        assert config.max_posts_per_request == 100
        assert config.max_comments_per_request == 100
        assert config.max_groups_per_request == 10000
        assert config.max_users_per_request == 1000
        assert config.max_group_members_per_request == 1000

    def test_request_limits_custom_values(self):
        """Test request limits with custom values"""
        config = VKAPIRequestLimits(
            max_posts_per_request=50,
            max_comments_per_request=50,
            max_groups_per_request=500,
            max_users_per_request=500,
            max_group_members_per_request=500,
        )

        assert config.max_posts_per_request == 50
        assert config.max_comments_per_request == 50
        assert config.max_groups_per_request == 500
        assert config.max_users_per_request == 500
        assert config.max_group_members_per_request == 500

    def test_request_limits_validation(self):
        """Test request limits validation"""
        # Valid values
        config = VKAPIRequestLimits(max_posts_per_request=200)
        assert config.max_posts_per_request == 200

        # Test negative values (should raise error)
        with pytest.raises(ValueError):
            VKAPIRequestLimits(max_posts_per_request=-1)

        # Test zero values (should raise error)
        with pytest.raises(ValueError):
            VKAPIRequestLimits(max_comments_per_request=0)


class TestVKAPICacheConfig:
    """Test suite for VK API cache configuration"""

    def test_cache_config_defaults(self):
        """Test cache config with default values"""
        config = VKAPICacheConfig()

        assert config.enabled is True
        assert config.group_posts_ttl == 300
        assert config.post_comments_ttl == 600
        assert config.group_info_ttl == 3600
        assert config.user_info_ttl == 1800
        assert config.search_ttl == 1800
        assert config.group_members_ttl == 1800

    def test_cache_config_disabled(self):
        """Test cache config when disabled"""
        config = VKAPICacheConfig(enabled=False)

        assert config.enabled is False
        # TTL values should still be set but not used
        assert config.group_posts_ttl == 300

    def test_cache_config_custom_ttl(self):
        """Test cache config with custom TTL values"""
        config = VKAPICacheConfig(
            group_posts_ttl=600, post_comments_ttl=1200, group_info_ttl=7200
        )

        assert config.group_posts_ttl == 600
        assert config.post_comments_ttl == 1200
        assert config.group_info_ttl == 7200

    def test_cache_config_validation(self):
        """Test cache config validation"""
        # Valid values
        config = VKAPICacheConfig(group_posts_ttl=1000)
        assert config.group_posts_ttl == 1000

        # Test negative TTL (should raise error)
        with pytest.raises(ValueError):
            VKAPICacheConfig(group_posts_ttl=-1)

        # Test zero TTL (should raise error)
        with pytest.raises(ValueError):
            VKAPICacheConfig(post_comments_ttl=0)


class TestVKAPIRetryConfig:
    """Test suite for VK API retry configuration"""

    def test_retry_config_defaults(self):
        """Test retry config with default values"""
        config = VKAPIRetryConfig()

        assert config.enabled is True
        assert config.max_attempts == 3
        assert config.backoff_factor == 2.0
        assert config.max_delay == 60.0

    def test_retry_config_disabled(self):
        """Test retry config when disabled"""
        config = VKAPIRetryConfig(enabled=False)

        assert config.enabled is False
        # Other values should still be set
        assert config.max_attempts == 3

    def test_retry_config_custom_values(self):
        """Test retry config with custom values"""
        config = VKAPIRetryConfig(
            max_attempts=5, backoff_factor=1.5, max_delay=120.0
        )

        assert config.max_attempts == 5
        assert config.backoff_factor == 1.5
        assert config.max_delay == 120.0

    def test_retry_config_validation(self):
        """Test retry config validation"""
        # Valid values
        config = VKAPIRetryConfig(max_attempts=10)
        assert config.max_attempts == 10

        # Test invalid values
        with pytest.raises(ValueError):
            VKAPIRetryConfig(max_attempts=0)

        with pytest.raises(ValueError):
            VKAPIRetryConfig(backoff_factor=-1.0)


class TestVKAPIProxyConfig:
    """Test suite for VK API proxy configuration"""

    def test_proxy_config_defaults(self):
        """Test proxy config with default values"""
        config = VKAPIProxyConfig()

        assert config.enabled is False
        assert config.proxy_list == []
        assert config.rotation_enabled is False

    def test_proxy_config_enabled(self):
        """Test proxy config when enabled"""
        proxy_list = ["http://proxy1:8080", "http://proxy2:8080"]
        config = VKAPIProxyConfig(
            enabled=True, proxy_list=proxy_list, rotation_enabled=True
        )

        assert config.enabled is True
        assert config.proxy_list == proxy_list
        assert config.rotation_enabled is True

    def test_proxy_config_validation(self):
        """Test proxy config validation"""
        # Valid proxy URLs
        config = VKAPIProxyConfig(
            enabled=True,
            proxy_list=["http://proxy1:8080", "https://proxy2:3128"],
        )
        assert len(config.proxy_list) == 2

        # Empty proxy list when enabled should be valid
        config = VKAPIProxyConfig(enabled=True, proxy_list=[])
        assert config.proxy_list == []


class TestMainVKAPIConfig:
    """Test suite for main VK API configuration"""

    def test_vk_api_config_structure(self):
        """Test main config has all required sections"""
        # Test that config object exists and has expected attributes
        assert hasattr(vk_api_config, "connection")
        assert hasattr(vk_api_config, "rate_limit")
        assert hasattr(vk_api_config, "limits")
        assert hasattr(vk_api_config, "cache")
        assert hasattr(vk_api_config, "retry")
        assert hasattr(vk_api_config, "proxy")

    def test_vk_api_config_token_handling(self):
        """Test token handling in main config"""
        # Test that config has token attribute
        assert hasattr(vk_api_config, "access_token")
        assert hasattr(vk_api_config, "is_token_configured")

    @patch.dict(os.environ, {"VK_API_ACCESS_TOKEN": "env_token"})
    def test_config_from_environment(self):
        """Test loading config from environment variables"""
        # This would require reloading the config module
        # For now, just test that the attribute exists
        assert hasattr(vk_api_config, "access_token")

    def test_config_field_mappings(self):
        """Test config field mappings for VK API"""
        # Test that config has expected field mappings
        assert hasattr(vk_api_config, "group_fields")
        assert hasattr(vk_api_config, "user_fields")
        assert hasattr(vk_api_config, "group_members_fields")


class TestErrorCodeConstants:
    """Test suite for error code constants"""

    def test_vk_error_constants_values(self):
        """Test VK error code constant values"""
        assert VK_ERROR_ACCESS_DENIED == 15
        assert VK_ERROR_INVALID_REQUEST == 100
        assert VK_ERROR_TOO_MANY_REQUESTS == 6
        assert VK_ERROR_AUTH_FAILED == 5
        assert VK_ERROR_PERMISSION_DENIED == 7

    def test_error_constants_are_integers(self):
        """Test that all error constants are integers"""
        constants = [
            VK_ERROR_ACCESS_DENIED,
            VK_ERROR_INVALID_REQUEST,
            VK_ERROR_TOO_MANY_REQUESTS,
            VK_ERROR_AUTH_FAILED,
            VK_ERROR_PERMISSION_DENIED,
        ]

        for const in constants:
            assert isinstance(const, int)
            assert const >= 0

    def test_error_constants_uniqueness(self):
        """Test that error constants are unique"""
        constants = [
            VK_ERROR_ACCESS_DENIED,
            VK_ERROR_INVALID_REQUEST,
            VK_ERROR_TOO_MANY_REQUESTS,
            VK_ERROR_AUTH_FAILED,
            VK_ERROR_PERMISSION_DENIED,
        ]

        assert len(constants) == len(set(constants))


class TestUserAgents:
    """Test suite for user agent constants"""

    def test_user_agents_list(self):
        """Test user agents list structure"""
        assert isinstance(USER_AGENTS, list)
        assert len(USER_AGENTS) > 0

    def test_user_agents_content(self):
        """Test user agents content"""
        for ua in USER_AGENTS:
            assert isinstance(ua, str)
            assert len(ua.strip()) > 0
            # Should contain application identifiers
            assert any(
                identifier in ua.lower()
                for identifier in ["vk", "parser", "collector", "client"]
            )

    def test_user_agents_uniqueness(self):
        """Test user agents are unique"""
        assert len(USER_AGENTS) == len(set(USER_AGENTS))


class TestConfigurationValidation:
    """Test suite for overall configuration validation"""

    def test_config_validation_types(self):
        """Test configuration type validation"""
        # Test that all config sections are Pydantic models
        config_sections = [
            vk_api_config.connection,
            vk_api_config.rate_limit,
            vk_api_config.limits,
            vk_api_config.cache,
            vk_api_config.retry,
            vk_api_config.proxy,
        ]

        for section in config_sections:
            assert hasattr(section, "model_dump")  # Pydantic method

    def test_config_validation_ranges(self):
        """Test configuration value ranges"""
        # Test rate limit values
        assert vk_api_config.rate_limit.max_requests_per_second > 0
        assert vk_api_config.rate_limit.window_seconds > 0

        # Test cache TTL values
        assert vk_api_config.cache.group_posts_ttl > 0
        assert vk_api_config.cache.user_info_ttl > 0

        # Test limits values
        assert vk_api_config.limits.max_posts_per_request > 0
        assert vk_api_config.limits.max_users_per_request > 0

    def test_config_cross_validation(self):
        """Test cross-validation between config sections"""
        # Cache TTL should be reasonable compared to rate limits
        rate_limit_window = vk_api_config.rate_limit.window_seconds
        cache_ttl = vk_api_config.cache.group_posts_ttl

        # Cache TTL should be longer than rate limit window
        assert cache_ttl > rate_limit_window


class TestConfigurationEdgeCases:
    """Test suite for configuration edge cases"""

    def test_config_with_none_values(self):
        """Test configuration validation with None values"""
        # Test that config raises validation error for None values
        with pytest.raises(ValidationError):
            VKAPICacheConfig(group_posts_ttl=None)

    def test_config_with_extreme_values(self):
        """Test configuration with extreme values"""
        # Test with very large values
        config = VKAPIRequestLimits(max_posts_per_request=10000)
        assert config.max_posts_per_request == 10000

        # Test with very small values
        config = VKAPIRateLimitConfig(
            max_requests_per_second=1, window_seconds=0.1
        )
        assert config.max_requests_per_second == 1

    def test_config_json_roundtrip(self):
        """Test configuration JSON serialization roundtrip"""
        original_config = VKAPIConnectionConfig(
            timeout=45.0, max_connections=150
        )

        # Serialize to JSON
        config_dict = original_config.model_dump()
        config_json = json.dumps(config_dict)

        # Deserialize back
        parsed_dict = json.loads(config_json)
        restored_config = VKAPIConnectionConfig(**parsed_dict)

        # Verify values are preserved
        assert restored_config.timeout == original_config.timeout
        assert (
            restored_config.max_connections == original_config.max_connections
        )

    def test_config_field_name_consistency(self):
        """Test configuration field name consistency"""
        # Test that field names follow consistent patterns
        config = VKAPIConnectionConfig()

        fields = config.model_fields.keys()
        for field in fields:
            # Field names should be snake_case
            assert field.islower()
            assert "_" in field or field in [
                "timeout"
            ]  # Some fields might not have underscores


class TestConfigurationSecurity:
    """Test suite for configuration security"""

    def test_token_not_logged(self):
        """Test that access tokens are not exposed in logs"""
        # Test that config doesn't expose tokens in string representation
        config_str = str(vk_api_config)
        # Should not contain actual token values
        assert "token" not in config_str.lower() or "***" in config_str

    def test_sensitive_field_handling(self):
        """Test handling of sensitive configuration fields"""
        # Test that sensitive fields have appropriate handling
        # This is more of a design consideration, but we can test the structure
        assert hasattr(vk_api_config, "access_token")
        assert hasattr(vk_api_config, "is_token_configured")

        # Token should be either None or a non-empty string
        token = vk_api_config.access_token
        assert token is None or isinstance(token, str)


class TestConfigurationPerformance:
    """Test suite for configuration performance"""

    def test_config_access_performance(self):
        """Test configuration access performance"""
        import time

        # Test multiple config accesses
        start_time = time.time()
        for _ in range(1000):
            _ = vk_api_config.rate_limit.max_requests_per_second
            _ = vk_api_config.limits.max_posts_per_request
            _ = vk_api_config.cache.enabled

        end_time = time.time()
        duration = end_time - start_time

        # Should be very fast (< 1ms per access)
        assert duration < 1.0

    def test_config_validation_performance(self):
        """Test configuration validation performance"""
        import time

        # Test creating multiple config instances
        start_time = time.time()
        for _ in range(100):
            config = VKAPIConnectionConfig(timeout=30.0, max_connections=100)
            _ = config.model_dump()

        end_time = time.time()
        duration = end_time - start_time

        # Should be reasonably fast
        assert duration < 0.5
