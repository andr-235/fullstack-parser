"""
Comprehensive tests for Settings module utilities, schemas, exceptions, constants, and dependencies

This file contains tests for:
- Utility functions (utils.py)
- Pydantic schemas (schemas.py)
- Custom exceptions (exceptions.py)
- Constants (constants.py)
- Dependencies (dependencies.py)
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from src.settings.utils import (
    validate_settings_section_name,
    validate_settings_key,
    sanitize_settings_value,
    calculate_settings_hash,
    sort_dict_recursive,
    diff_settings,
    flatten_settings,
    unflatten_settings,
    filter_settings_by_permissions,
    create_settings_backup,
    validate_settings_backup,
    get_settings_summary,
    merge_settings_with_defaults,
)

from src.settings.exceptions import (
    SettingsError,
    SettingsSectionNotFoundError,
    SettingsKeyNotFoundError,
    SettingsValidationError,
    SettingsUpdateError,
    SettingsAccessDeniedError,
    SettingsReadonlyError,
    SettingsCriticalSectionError,
    SettingsImportError,
    SettingsExportError,
    SettingsCacheError,
    SettingsSizeLimitError,
    SettingsSectionLimitError,
    SettingsValueLimitError,
    SettingsAuditError,
    SettingsMetricsError,
    SettingsBackupError,
    SettingsRestoreError,
)

from src.settings.constants import *
from src.settings.schemas import *
from src.settings.dependencies import get_settings_service


class TestUtils:
    """Test suite for utility functions"""

    def test_validate_settings_section_name_valid(self):
        """Test validating valid section names"""
        # Valid names
        valid_names = [
            "vk_api",
            "my_section",
            "section123",
            "section_name",
            "section-name",
        ]

        for name in valid_names:
            valid, error = validate_settings_section_name(name)
            assert valid is True
            assert error == ""

    def test_validate_settings_section_name_invalid(self):
        """Test validating invalid section names"""
        # Invalid names
        invalid_cases = [
            ("", "Название секции не может быть пустым"),
            ("   ", "Название секции не может быть пустым"),
            (
                "very_long_section_name_that_exceeds_fifty_characters_limit",
                "Название секции слишком длинное",
            ),
            ("123section", "Название секции не может начинаться с цифры"),
            (
                "section@name",
                "Название секции может содержать только буквы, цифры, _ и -",
            ),
            (
                "section name",
                "Название секции может содержать только буквы, цифры, _ и -",
            ),
        ]

        for name, expected_error in invalid_cases:
            valid, error = validate_settings_section_name(name)
            assert valid is False
            assert expected_error in error

    def test_validate_settings_key_valid(self):
        """Test validating valid setting keys"""
        # Valid keys
        valid_keys = [
            "api_version",
            "my_key",
            "key123",
            "key_name",
            "key-name",
        ]

        for key in valid_keys:
            valid, error = validate_settings_key(key)
            assert valid is True
            assert error == ""

    def test_validate_settings_key_invalid(self):
        """Test validating invalid setting keys"""
        # Invalid keys
        invalid_cases = [
            ("", "Ключ настройки не может быть пустым"),
            ("   ", "Ключ настройки не может быть пустым"),
            (
                "a" * 101,  # Create a key longer than 100 characters
                "Ключ настройки слишком длинный (макс 100 символов)",
            ),
            ("key@name", "Ключ может содержать только буквы, цифры, _ и -"),
            ("key name", "Ключ может содержать только буквы, цифры, _ и -"),
        ]

        for key, expected_error in invalid_cases:
            valid, error = validate_settings_key(key)
            assert valid is False
            assert expected_error in error

    def test_sanitize_settings_value_string(self):
        """Test sanitizing string values"""
        # Normal string
        assert sanitize_settings_value("test") == "test"

        # String with whitespace
        assert sanitize_settings_value("  test  ") == "test"

        # Very long string (should be truncated)
        long_string = "x" * 10001
        sanitized = sanitize_settings_value(long_string)
        assert len(sanitized) == 10003  # 10000 + len("...")
        assert sanitized.endswith("...")

    def test_sanitize_settings_value_dict(self):
        """Test sanitizing dictionary values"""
        test_dict = {
            "key1": "value1",
            "key2": {"nested": "value"},
            "invalid_key": "value",  # This should be filtered out due to key length check
        }

        result = sanitize_settings_value(test_dict)
        assert "key1" in result
        assert "key2" in result
        assert isinstance(result["key2"], dict)

    def test_sanitize_settings_value_list(self):
        """Test sanitizing list values"""
        # Normal list
        test_list = ["item1", "item2", "item3"]
        result = sanitize_settings_value(test_list)
        assert result == test_list

        # Very long list (should be truncated)
        long_list = list(range(1001))
        result = sanitize_settings_value(long_list)
        assert len(result) == 1000

    def test_calculate_settings_hash_consistent(self):
        """Test that hash calculation is consistent"""
        settings1 = {"a": 1, "b": {"c": 2}}
        settings2 = {"a": 1, "b": {"c": 2}}

        hash1 = calculate_settings_hash(settings1)
        hash2 = calculate_settings_hash(settings2)

        assert hash1 == hash2

    def test_calculate_settings_hash_different(self):
        """Test that different settings produce different hashes"""
        settings1 = {"a": 1, "b": 2}
        settings2 = {"a": 1, "b": 3}

        hash1 = calculate_settings_hash(settings1)
        hash2 = calculate_settings_hash(settings2)

        assert hash1 != hash2

    def test_sort_dict_recursive(self):
        """Test recursive dictionary sorting"""
        unsorted = {"b": {"z": 1, "a": 2}, "a": {"m": 3, "n": 4}, "c": 5}

        result = sort_dict_recursive(unsorted)

        # Check that keys are sorted
        keys = list(result.keys())
        assert keys == ["a", "b", "c"]

        # Check that nested dict is also sorted
        nested_keys = list(result["b"].keys())
        assert nested_keys == ["a", "z"]

    def test_diff_settings(self):
        """Test calculating differences between settings"""
        old_settings = {
            "section1": {"key1": "value1", "key2": "value2"},
            "section2": {"key3": "value3"},
        }

        new_settings = {
            "section1": {
                "key1": "value1",
                "key2": "new_value2",
                "key4": "value4",
            },
            "section3": {"key5": "value5"},
        }

        result = diff_settings(old_settings, new_settings)

        assert "section1" in result["modified"]
        assert "section2" in result["removed"]
        assert "section3" in result["added"]
        assert result["modified"]["section1"]["new"]["key2"] == "new_value2"

    def test_flatten_settings(self):
        """Test flattening nested settings"""
        nested = {
            "section1": {"key1": "value1", "key2": {"nested": "value"}},
            "section2": ["item1", "item2"],
        }

        result = flatten_settings(nested)

        assert result["section1.key1"] == "value1"
        assert result["section1.key2.nested"] == "value"
        assert result["section2"] == '["item1", "item2"]'

    def test_unflatten_settings(self):
        """Test unflattening settings"""
        flat = {
            "section1.key1": "value1",
            "section1.key2.nested": "value",
            "section2": '["item1", "item2"]',
        }

        result = unflatten_settings(flat)

        assert result["section1"]["key1"] == "value1"
        assert result["section1"]["key2"]["nested"] == "value"
        assert result["section2"] == ["item1", "item2"]

    def test_filter_settings_by_permissions_admin(self):
        """Test filtering with admin permissions"""
        settings = {"public": {"key": "value"}, "critical": {"secret": "data"}}

        permissions = ["settings:admin"]
        result = filter_settings_by_permissions(
            settings, permissions, ["critical"]
        )

        assert "public" in result
        assert "critical" in result

    def test_filter_settings_by_permissions_limited(self):
        """Test filtering with limited permissions"""
        settings = {"public": {"key": "value"}, "critical": {"secret": "data"}}

        permissions = ["settings:read:public"]
        result = filter_settings_by_permissions(
            settings, permissions, ["critical"]
        )

        assert "public" in result
        assert "critical" not in result

    def test_create_settings_backup(self):
        """Test creating settings backup"""
        settings = {"section": {"key": "value"}}
        result = create_settings_backup(settings)

        assert "settings" in result
        assert "backup_created_at" in result
        assert "version" in result
        assert "hash" in result
        assert "sections_count" in result
        assert result["sections_count"] == 1

    def test_validate_settings_backup_valid(self):
        """Test validating valid backup"""
        backup = {
            "settings": {"section": {"key": "value"}},
            "backup_created_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "hash": calculate_settings_hash({"section": {"key": "value"}}),
            "sections_count": 1,
        }

        valid, error = validate_settings_backup(backup)
        assert valid is True
        assert error == ""

    def test_validate_settings_backup_invalid(self):
        """Test validating invalid backup"""
        # Missing required field
        invalid_backup = {"settings": {"section": {"key": "value"}}}

        valid, error = validate_settings_backup(invalid_backup)
        assert valid is False
        assert "Missing required field" in error

    def test_get_settings_summary(self):
        """Test getting settings summary"""
        settings = {
            "section1": {"key1": "string", "key2": 42},
            "section2": {"key3": True},
        }

        result = get_settings_summary(settings)

        assert result["total_sections"] == 2
        assert result["total_keys"] == 3
        assert result["total_size_bytes"] > 0
        assert "str" in result["value_types"]
        assert "int" in result["value_types"]
        assert "bool" in result["value_types"]
        assert "section1" in result["sections_list"]
        assert "section2" in result["sections_list"]

    def test_merge_settings_with_defaults(self):
        """Test merging settings with defaults"""
        current = {"section1": {"key1": "modified"}}
        defaults = {
            "section1": {"key1": "default", "key2": "default2"},
            "section2": {"key3": "default3"},
        }

        result = merge_settings_with_defaults(current, defaults)

        assert (
            result["section1"]["key1"] == "modified"
        )  # Current value preserved
        assert result["section1"]["key2"] == "default2"  # Default value added
        assert result["section2"]["key3"] == "default3"  # New section added


class TestExceptions:
    """Test suite for custom exceptions"""

    def test_settings_error(self):
        """Test SettingsError exception"""
        error = SettingsError("Test error", "TEST_ERROR", {"detail": "info"})

        assert error.status_code == 500
        assert error.detail == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details["detail"] == "info"

    def test_settings_section_not_found_error(self):
        """Test SettingsSectionNotFoundError exception"""
        error = SettingsSectionNotFoundError("missing_section")

        assert error.status_code == 404
        assert "missing_section" in error.detail
        assert error.error_code == "SETTINGS_SECTION_NOT_FOUND"
        assert error.details["section_name"] == "missing_section"

    def test_settings_key_not_found_error(self):
        """Test SettingsKeyNotFoundError exception"""
        error = SettingsKeyNotFoundError("section", "key")

        assert error.status_code == 404
        assert "section.key" in error.detail
        assert error.error_code == "SETTINGS_KEY_NOT_FOUND"
        assert error.details["section_name"] == "section"
        assert error.details["key"] == "key"

    def test_settings_validation_error(self):
        """Test SettingsValidationError exception"""
        validation_errors = {"field": "error message"}
        error = SettingsValidationError("Validation failed", validation_errors)

        assert error.status_code == 400
        assert error.detail == "Validation failed"
        assert error.error_code == "SETTINGS_VALIDATION_ERROR"
        assert error.details["validation_errors"] == validation_errors

    def test_settings_readonly_error_with_key(self):
        """Test SettingsReadonlyError with key"""
        error = SettingsReadonlyError("section", "key")

        assert error.status_code == 403
        assert "section.key" in error.detail
        assert error.error_code == "SETTINGS_READONLY_ERROR"
        assert error.details["section_name"] == "section"
        assert error.details["key"] == "key"

    def test_settings_readonly_error_without_key(self):
        """Test SettingsReadonlyError without key"""
        error = SettingsReadonlyError("section")

        assert error.status_code == 403
        assert "section" in error.detail
        assert error.error_code == "SETTINGS_READONLY_ERROR"
        assert error.details["section_name"] == "section"
        assert "key" not in error.details

    def test_settings_critical_section_error(self):
        """Test SettingsCriticalSectionError exception"""
        error = SettingsCriticalSectionError("critical_section")

        assert error.status_code == 403
        assert "critical_section" in error.detail
        assert error.error_code == "SETTINGS_CRITICAL_SECTION_ERROR"
        assert error.details["section_name"] == "critical_section"

    def test_settings_size_limit_error(self):
        """Test SettingsSizeLimitError exception"""
        error = SettingsSizeLimitError(2000, 1000)

        assert error.status_code == 413
        assert "2000 > 1000" in error.detail
        assert error.error_code == "SETTINGS_SIZE_LIMIT_ERROR"
        assert error.details["current_size"] == 2000
        assert error.details["max_size"] == 1000

    def test_settings_section_limit_error(self):
        """Test SettingsSectionLimitError exception"""
        error = SettingsSectionLimitError(60, 50)

        assert error.status_code == 413
        assert "60 > 50" in error.detail
        assert error.error_code == "SETTINGS_SECTION_LIMIT_ERROR"
        assert error.details["current_count"] == 60
        assert error.details["max_count"] == 50

    def test_settings_value_limit_error(self):
        """Test SettingsValueLimitError exception"""
        error = SettingsValueLimitError("section", 120, 100)

        assert error.status_code == 413
        assert "section" in error.detail
        assert "120 > 100" in error.detail
        assert error.error_code == "SETTINGS_VALUE_LIMIT_ERROR"
        assert error.details["section_name"] == "section"
        assert error.details["current_count"] == 120
        assert error.details["max_count"] == 100


class TestConstants:
    """Test suite for constants"""

    def test_settings_section_constants(self):
        """Test settings section constants"""
        assert SETTINGS_SECTION_VK_API == "vk_api"
        assert SETTINGS_SECTION_MONITORING == "monitoring"
        assert SETTINGS_SECTION_DATABASE == "database"
        assert SETTINGS_SECTION_LOGGING == "logging"
        assert SETTINGS_SECTION_UI == "ui"
        assert SETTINGS_SECTION_CACHE == "cache"
        assert SETTINGS_SECTION_SECURITY == "security"

    def test_vk_api_constants(self):
        """Test VK API related constants"""
        assert VK_API_ACCESS_TOKEN == "access_token"
        assert VK_API_API_VERSION == "api_version"
        assert VK_API_REQUESTS_PER_SECOND == "requests_per_second"

    def test_monitoring_constants(self):
        """Test monitoring related constants"""
        assert MONITORING_SCHEDULER_INTERVAL == "scheduler_interval_seconds"
        assert MONITORING_MAX_CONCURRENT_GROUPS == "max_concurrent_groups"
        assert MONITORING_ENABLED == "enabled"

    def test_database_constants(self):
        """Test database related constants"""
        assert DATABASE_POOL_SIZE == "pool_size"
        assert DATABASE_MAX_OVERFLOW == "max_overflow"
        assert DATABASE_POOL_RECYCLE == "pool_recycle"
        assert DATABASE_ECHO == "echo"

    def test_ui_constants(self):
        """Test UI related constants"""
        assert UI_THEME == "theme"
        assert UI_AUTO_REFRESH == "auto_refresh"
        assert UI_REFRESH_INTERVAL == "refresh_interval"
        assert UI_ITEMS_PER_PAGE == "items_per_page"
        assert UI_SHOW_NOTIFICATIONS == "show_notifications"

    def test_default_values(self):
        """Test default value constants"""
        assert DEFAULT_VK_API_VERSION == "5.199"
        assert DEFAULT_REQUESTS_PER_SECOND == 3
        assert DEFAULT_SCHEDULER_INTERVAL == 300
        assert DEFAULT_MAX_CONCURRENT_GROUPS == 5
        assert DEFAULT_DATABASE_POOL_SIZE == 10
        assert DEFAULT_LOG_LEVEL == "INFO"
        assert DEFAULT_UI_THEME == "system"
        assert DEFAULT_CACHE_TTL == 300

    def test_ui_themes(self):
        """Test UI theme constants"""
        assert UI_THEME_SYSTEM == "system"
        assert UI_THEME_LIGHT == "light"
        assert UI_THEME_DARK == "dark"

    def test_log_formats(self):
        """Test log format constants"""
        assert LOG_FORMAT_JSON == "json"
        assert LOG_FORMAT_TEXT == "text"
        assert LOG_FORMAT_DETAILED == "detailed"

    def test_log_levels(self):
        """Test log level constants"""
        assert LOG_LEVEL_DEBUG == "DEBUG"
        assert LOG_LEVEL_INFO == "INFO"
        assert LOG_LEVEL_WARNING == "WARNING"
        assert LOG_LEVEL_ERROR == "ERROR"
        assert LOG_LEVEL_CRITICAL == "CRITICAL"

    def test_cache_backends(self):
        """Test cache backend constants"""
        assert CACHE_BACKEND_MEMORY == "memory"
        assert CACHE_BACKEND_REDIS == "redis"
        assert CACHE_BACKEND_FILE == "file"

    def test_security_algorithms(self):
        """Test security algorithm constants"""
        assert SECURITY_ALGORITHM_HS256 == "HS256"
        assert SECURITY_ALGORITHM_HS512 == "HS512"

    def test_error_messages(self):
        """Test error message constants"""
        assert ERROR_INVALID_SETTINGS_SECTION == "Неверная секция настроек"
        assert ERROR_SETTING_NOT_FOUND == "Настройка не найдена"
        assert (
            ERROR_SETTINGS_VALIDATION_FAILED
            == "Валидация настроек не пройдена"
        )
        assert ERROR_SETTINGS_UPDATE_FAILED == "Не удалось обновить настройки"

    def test_success_messages(self):
        """Test success message constants"""
        assert SUCCESS_SETTINGS_UPDATED == "Настройки успешно обновлены"
        assert (
            SUCCESS_SETTINGS_RESET
            == "Настройки сброшены к значениям по умолчанию"
        )

    def test_limit_constants(self):
        """Test limit constants"""
        assert MIN_PASSWORD_LENGTH == 8
        assert MAX_PASSWORD_LENGTH == 128
        assert MIN_POOL_SIZE == 1
        assert MAX_POOL_SIZE == 100
        assert MIN_REQUESTS_PER_SECOND == 1
        assert MAX_REQUESTS_PER_SECOND == 10

    def test_permissions(self):
        """Test permission constants"""
        assert PERMISSION_SETTINGS_READ == "settings:read"
        assert PERMISSION_SETTINGS_WRITE == "settings:write"
        assert PERMISSION_SETTINGS_ADMIN == "settings:admin"

    def test_regex_patterns(self):
        """Test regex pattern constants"""
        import re

        # Test email regex
        assert re.match(REGEX_EMAIL, "test@example.com")
        assert not re.match(REGEX_EMAIL, "invalid-email")

        # Test URL regex
        assert re.match(REGEX_URL, "https://example.com")
        assert not re.match(REGEX_URL, "not-a-url")

    def test_all_exported_constants(self):
        """Test that all constants are properly exported"""
        # This test ensures __all__ contains all the constants we expect
        expected_constants = [
            # Sections
            "SETTINGS_SECTION_VK_API",
            "SETTINGS_SECTION_MONITORING",
            "SETTINGS_SECTION_DATABASE",
            "SETTINGS_SECTION_LOGGING",
            "SETTINGS_SECTION_UI",
            "SETTINGS_SECTION_CACHE",
            "SETTINGS_SECTION_SECURITY",
            # VK API keys
            "VK_API_ACCESS_TOKEN",
            "VK_API_API_VERSION",
            "VK_API_REQUESTS_PER_SECOND",
            # Monitoring keys
            "MONITORING_SCHEDULER_INTERVAL",
            "MONITORING_MAX_CONCURRENT_GROUPS",
            # Default values
            "DEFAULT_VK_API_VERSION",
            "DEFAULT_REQUESTS_PER_SECOND",
            # UI themes
            "UI_THEME_SYSTEM",
            "UI_THEME_LIGHT",
            "UI_THEME_DARK",
            # Error messages
            "ERROR_INVALID_SETTINGS_SECTION",
            "ERROR_SETTINGS_UPDATE_FAILED",
            # Permissions
            "PERMISSION_SETTINGS_READ",
            "PERMISSION_SETTINGS_WRITE",
            "PERMISSION_SETTINGS_ADMIN",
        ]

        for const in expected_constants:
            assert hasattr(
                __import__("src.settings.constants", fromlist=[const]), const
            )


class TestSchemas:
    """Test suite for Pydantic schemas"""

    def test_settings_section_schema(self):
        """Test SettingsSection schema"""
        data = {
            "name": "test_section",
            "values": {"key1": "value1", "key2": 42},
            "description": "Test section",
        }

        section = SettingsSection(**data)

        assert section.name == "test_section"
        assert section.values["key1"] == "value1"
        assert section.values["key2"] == 42
        assert section.description == "Test section"

    def test_settings_update_request_schema(self):
        """Test SettingsUpdateRequest schema"""
        data = {
            "sections": {
                "vk_api": {"api_version": "5.200"},
                "database": {"pool_size": 20},
            }
        }

        request = SettingsUpdateRequest(**data)

        assert "vk_api" in request.sections
        assert "database" in request.sections
        assert request.sections["vk_api"]["api_version"] == "5.200"
        assert request.sections["database"]["pool_size"] == 20

    def test_settings_validation_result_schema(self):
        """Test SettingsValidationResult schema"""
        data = {
            "valid": True,
            "issues": {},
            "total_sections": 3,
            "sections_with_issues": 0,
        }

        result = SettingsValidationResult(**data)

        assert result.valid is True
        assert len(result.issues) == 0
        assert result.total_sections == 3
        assert result.sections_with_issues == 0

    def test_settings_export_response_schema(self):
        """Test SettingsExportResponse schema"""
        data = {
            "settings": {"section": {"key": "value"}},
            "exported_at": "2024-01-01T00:00:00Z",
            "version": "1.0",
            "format": "json",
            "sections_count": 1,
        }

        response = SettingsExportResponse(**data)

        assert response.settings["section"]["key"] == "value"
        assert response.version == "1.0"
        assert response.format == "json"
        assert response.sections_count == 1

    def test_settings_import_request_schema(self):
        """Test SettingsImportRequest schema"""
        data = {
            "settings": {"section": {"key": "value"}},
            "merge": True,
            "backup_before_import": False,
        }

        request = SettingsImportRequest(**data)

        assert request.settings["section"]["key"] == "value"
        assert request.merge is True
        assert request.backup_before_import is False

    def test_settings_health_response_schema(self):
        """Test SettingsHealthResponse schema"""
        data = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "cache": {"cache_valid": True, "cache_age_seconds": 60.0},
            "settings_loaded": True,
            "sections_count": 4,
        }

        response = SettingsHealthResponse(**data)

        assert response.status == "healthy"
        assert response.settings_loaded is True
        assert response.sections_count == 4
        assert response.cache["cache_valid"] is True

    def test_settings_cache_stats_schema(self):
        """Test SettingsCacheStats schema"""
        data = {
            "cache_valid": True,
            "cache_age_seconds": 120.5,
            "cache_size": 2048,
            "sections_cached": 3,
        }

        stats = SettingsCacheStats(**data)

        assert stats.cache_valid is True
        assert stats.cache_age_seconds == 120.5
        assert stats.cache_size == 2048
        assert stats.sections_cached == 3

    def test_settings_summary_schema(self):
        """Test SettingsSummary schema"""
        data = {
            "total_sections": 5,
            "total_keys": 15,
            "total_size_bytes": 1024,
            "value_types": {"str": 10, "int": 5},
            "sections_list": ["section1", "section2", "section3"],
            "last_updated": "2024-01-01T00:00:00Z",
        }

        summary = SettingsSummary(**data)

        assert summary.total_sections == 5
        assert summary.total_keys == 15
        assert summary.total_size_bytes == 1024
        assert len(summary.value_types) == 2
        assert len(summary.sections_list) == 3

    def test_settings_backup_schema(self):
        """Test SettingsBackup schema"""
        data = {
            "settings": {"section": {"key": "value"}},
            "backup_created_at": "2024-01-01T00:00:00Z",
            "version": "1.0",
            "hash": "abc123",
            "sections_count": 1,
        }

        backup = SettingsBackup(**data)

        assert backup.settings["section"]["key"] == "value"
        assert backup.version == "1.0"
        assert backup.hash == "abc123"
        assert backup.sections_count == 1

    def test_settings_diff_schema(self):
        """Test SettingsDiff schema"""
        data = {
            "added": {"new_section": {"key": "value"}},
            "removed": {"old_section": {"key": "value"}},
            "modified": {
                "modified_section": {
                    "old": {"key": "old"},
                    "new": {"key": "new"},
                }
            },
        }

        diff = SettingsDiff(**data)

        assert "new_section" in diff.added
        assert "old_section" in diff.removed
        assert "modified_section" in diff.modified

    def test_settings_value_response_schema(self):
        """Test SettingsValueResponse schema"""
        data = {
            "section_name": "test_section",
            "key": "test_key",
            "value": "test_value",
            "value_type": "str",
        }

        response = SettingsValueResponse(**data)

        assert response.section_name == "test_section"
        assert response.key == "test_key"
        assert response.value == "test_value"
        assert response.value_type == "str"

    def test_settings_operation_result_schema(self):
        """Test SettingsOperationResult schema"""
        data = {
            "success": True,
            "operation": "update",
            "message": "Operation completed",
            "timestamp": "2024-01-01T00:00:00Z",
            "affected_sections": ["section1", "section2"],
        }

        result = SettingsOperationResult(**data)

        assert result.success is True
        assert result.operation == "update"
        assert result.message == "Operation completed"
        assert len(result.affected_sections) == 2

    def test_settings_bulk_update_request_schema(self):
        """Test SettingsBulkUpdateRequest schema"""
        data = {
            "updates": {
                "section1": {"key1": "value1"},
                "section2": {"key2": "value2"},
            },
            "validate_before_update": True,
            "create_backup": False,
        }

        request = SettingsBulkUpdateRequest(**data)

        assert len(request.updates) == 2
        assert request.validate_before_update is True
        assert request.create_backup is False

    def test_settings_search_request_schema(self):
        """Test SettingsSearchRequest schema"""
        data = {
            "query": "test query",
            "section_filter": "vk_api",
            "case_sensitive": True,
        }

        request = SettingsSearchRequest(**data)

        assert request.query == "test query"
        assert request.section_filter == "vk_api"
        assert request.case_sensitive is True

    def test_settings_search_result_schema(self):
        """Test SettingsSearchResult schema"""
        data = {
            "section_name": "test_section",
            "key": "test_key",
            "value": "test_value",
            "match_type": "exact",
        }

        result = SettingsSearchResult(**data)

        assert result.section_name == "test_section"
        assert result.key == "test_key"
        assert result.value == "test_value"
        assert result.match_type == "exact"

    def test_settings_permission_check_schema(self):
        """Test SettingsPermissionCheck schema"""
        data = {
            "user_id": "user123",
            "permissions": ["settings:read", "settings:write"],
            "section_name": "vk_api",
            "can_read": True,
            "can_write": True,
            "is_admin": False,
        }

        check = SettingsPermissionCheck(**data)

        assert check.user_id == "user123"
        assert len(check.permissions) == 2
        assert check.section_name == "vk_api"
        assert check.can_read is True
        assert check.can_write is True
        assert check.is_admin is False

    def test_schema_validation_errors(self):
        """Test schema validation errors"""
        # Test missing required field
        with pytest.raises(ValueError):
            SettingsSection()  # Missing required fields

        # Test invalid field type
        with pytest.raises(ValueError):
            SettingsValidationResult(valid="not_a_boolean")

    def test_schema_field_validation(self):
        """Test schema field validation"""
        # Test optional fields
        section = SettingsSection(name="test", values={})
        assert section.description is None

        # Test default values
        import_request = SettingsImportRequest(settings={})
        assert import_request.merge is True
        assert import_request.backup_before_import is True


class TestDependencies:
    """Test suite for dependencies"""

    @pytest.mark.asyncio
    async def test_get_settings_service(self):
        """Test get_settings_service dependency"""
        service = await get_settings_service()

        # Should return a SettingsService instance
        assert service is not None
        assert hasattr(service, "get_current_settings")
        assert hasattr(service, "update_settings")
        assert hasattr(service, "reset_to_defaults")

    def test_dependency_function_signature(self):
        """Test dependency function signature"""
        import inspect

        sig = inspect.signature(get_settings_service)
        assert len(sig.parameters) == 0  # No parameters required

        # Should be async function
        assert inspect.iscoroutinefunction(get_settings_service)
