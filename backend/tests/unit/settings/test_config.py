"""
Unit tests for SettingsConfig

Tests cover all configuration methods and class attributes including:
- Default settings retrieval
- Configuration methods for different aspects
- Critical and readonly section management
- Cache configuration
- Validation configuration
- Security configuration
- Performance configuration
"""

import pytest

from src.settings.config import SettingsConfig, settings_config


class TestSettingsConfig:
    """Test suite for SettingsConfig"""

    def test_class_attributes(self):
        """Test SettingsConfig class attributes"""
        # Basic settings
        assert hasattr(SettingsConfig, "ENABLED")
        assert hasattr(SettingsConfig, "CACHE_ENABLED")
        assert hasattr(SettingsConfig, "CACHE_TTL")
        assert hasattr(SettingsConfig, "VALIDATION_ENABLED")

        # Export/Import settings
        assert hasattr(SettingsConfig, "EXPORT_FORMAT")
        assert hasattr(SettingsConfig, "EXPORT_COMPRESSION")
        assert hasattr(SettingsConfig, "IMPORT_MERGE_DEFAULT")

        # Validation settings
        assert hasattr(SettingsConfig, "VALIDATION_STRICT_MODE")
        assert hasattr(SettingsConfig, "VALIDATION_ALLOW_UNKNOWN_SECTIONS")
        assert hasattr(SettingsConfig, "VALIDATION_ALLOW_UNKNOWN_KEYS")

        # Audit settings
        assert hasattr(SettingsConfig, "AUDIT_ENABLED")
        assert hasattr(SettingsConfig, "AUDIT_LOG_CHANGES")
        assert hasattr(SettingsConfig, "AUDIT_LOG_ACCESS")

        # Cache settings
        assert hasattr(SettingsConfig, "CACHE_PREFIX")
        assert hasattr(SettingsConfig, "CACHE_SECTIONS_SEPARATELY")
        assert hasattr(SettingsConfig, "CACHE_VALUES_SEPARATELY")

        # Performance settings
        assert hasattr(SettingsConfig, "MAX_SETTINGS_SIZE")
        assert hasattr(SettingsConfig, "MAX_SECTIONS_COUNT")
        assert hasattr(SettingsConfig, "MAX_VALUES_PER_SECTION")

        # Security settings
        assert hasattr(SettingsConfig, "REQUIRE_AUTH_FOR_WRITE")
        assert hasattr(SettingsConfig, "REQUIRE_ADMIN_FOR_CRITICAL")
        assert hasattr(SettingsConfig, "ALLOW_RESET_TO_DEFAULTS")

        # Critical and readonly sections
        assert hasattr(SettingsConfig, "CRITICAL_SECTIONS")
        assert hasattr(SettingsConfig, "READONLY_SECTIONS")

        # Default sections
        assert hasattr(SettingsConfig, "DEFAULT_SECTIONS")
        assert isinstance(SettingsConfig.DEFAULT_SECTIONS, dict)

    def test_default_sections_structure(self):
        """Test default sections structure"""
        default_sections = SettingsConfig.DEFAULT_SECTIONS

        # Check required sections exist
        required_sections = [
            "vk_api",
            "monitoring",
            "database",
            "logging",
            "ui",
            "cache",
            "security",
        ]
        for section in required_sections:
            assert (
                section in default_sections
            ), f"Missing required section: {section}"
            assert isinstance(
                default_sections[section], dict
            ), f"Section {section} should be a dict"

    def test_vk_api_default_section(self):
        """Test VK API default section"""
        vk_api = SettingsConfig.DEFAULT_SECTIONS["vk_api"]

        # Check required VK API settings
        required_keys = [
            "access_token",
            "api_version",
            "requests_per_second",
            "max_posts_per_request",
        ]
        for key in required_keys:
            assert key in vk_api, f"Missing VK API setting: {key}"

        # Check types and values
        assert isinstance(vk_api["access_token"], str)
        assert isinstance(vk_api["api_version"], str)
        assert isinstance(vk_api["requests_per_second"], (int, float))
        assert vk_api["requests_per_second"] > 0

    def test_monitoring_default_section(self):
        """Test monitoring default section"""
        monitoring = SettingsConfig.DEFAULT_SECTIONS["monitoring"]

        # Check required monitoring settings
        required_keys = [
            "scheduler_interval_seconds",
            "max_concurrent_groups",
            "enabled",
        ]
        for key in required_keys:
            assert key in monitoring, f"Missing monitoring setting: {key}"

        # Check types and values
        assert isinstance(
            monitoring["scheduler_interval_seconds"], (int, float)
        )
        assert monitoring["scheduler_interval_seconds"] > 0
        assert isinstance(monitoring["max_concurrent_groups"], int)
        assert monitoring["max_concurrent_groups"] > 0
        assert isinstance(monitoring["enabled"], bool)

    def test_database_default_section(self):
        """Test database default section"""
        database = SettingsConfig.DEFAULT_SECTIONS["database"]

        # Check required database settings
        required_keys = ["pool_size", "max_overflow", "pool_recycle", "echo"]
        for key in required_keys:
            assert key in database, f"Missing database setting: {key}"

        # Check types and values
        assert isinstance(database["pool_size"], int)
        assert database["pool_size"] > 0
        assert isinstance(database["max_overflow"], int)
        assert database["max_overflow"] >= 0
        assert isinstance(database["echo"], bool)

    def test_security_default_section(self):
        """Test security default section"""
        security = SettingsConfig.DEFAULT_SECTIONS["security"]

        # Check required security settings
        required_keys = [
            "algorithm",
            "access_token_expire_minutes",
            "refresh_token_expire_days",
        ]
        for key in required_keys:
            assert key in security, f"Missing security setting: {key}"

        # Check types and values
        assert isinstance(security["algorithm"], str)
        assert isinstance(security["access_token_expire_minutes"], int)
        assert security["access_token_expire_minutes"] > 0
        assert isinstance(security["refresh_token_expire_days"], int)
        assert security["refresh_token_expire_days"] > 0

    def test_cache_default_section(self):
        """Test cache default section"""
        cache = SettingsConfig.DEFAULT_SECTIONS["cache"]

        # Check required cache settings
        required_keys = ["enabled", "ttl", "max_size", "backend"]
        for key in required_keys:
            assert key in cache, f"Missing cache setting: {key}"

        # Check types and values
        assert isinstance(cache["enabled"], bool)
        assert isinstance(cache["ttl"], int)
        assert cache["ttl"] > 0
        assert isinstance(cache["max_size"], int)
        assert cache["max_size"] > 0
        assert isinstance(cache["backend"], str)

    def test_get_default_settings(self):
        """Test get_default_settings method"""
        settings = SettingsConfig.get_default_settings()

        assert isinstance(settings, dict)
        assert len(settings) > 0

        # Should return a copy, not the original
        assert settings is not SettingsConfig.DEFAULT_SECTIONS

        # Should be equal in content
        assert settings == SettingsConfig.DEFAULT_SECTIONS

    def test_get_critical_sections(self):
        """Test get_critical_sections method"""
        critical_sections = SettingsConfig.get_critical_sections()

        assert isinstance(critical_sections, list)
        assert len(critical_sections) > 0

        # Should return a copy, not the original
        assert critical_sections is not SettingsConfig.CRITICAL_SECTIONS

        # Should be equal in content
        assert critical_sections == SettingsConfig.CRITICAL_SECTIONS

    def test_get_readonly_sections(self):
        """Test get_readonly_sections method"""
        readonly_sections = SettingsConfig.get_readonly_sections()

        assert isinstance(readonly_sections, list)

        # Should return a copy, not the original
        assert readonly_sections is not SettingsConfig.READONLY_SECTIONS

        # Should be equal in content
        assert readonly_sections == SettingsConfig.READONLY_SECTIONS

    def test_is_critical_section(self):
        """Test is_critical_section method"""
        # Test critical sections
        for section in SettingsConfig.CRITICAL_SECTIONS:
            assert SettingsConfig.is_critical_section(section) is True

        # Test non-critical sections
        assert SettingsConfig.is_critical_section("vk_api") is False
        assert SettingsConfig.is_critical_section("nonexistent") is False

    def test_is_readonly_section(self):
        """Test is_readonly_section method"""
        # Test readonly sections
        for section in SettingsConfig.READONLY_SECTIONS:
            assert SettingsConfig.is_readonly_section(section) is True

        # Test non-readonly sections
        assert SettingsConfig.is_readonly_section("vk_api") is False
        assert SettingsConfig.is_readonly_section("nonexistent") is False

    def test_get_cache_config(self):
        """Test get_cache_config method"""
        config = SettingsConfig.get_cache_config()

        assert isinstance(config, dict)
        assert "enabled" in config
        assert "ttl" in config
        assert "prefix" in config
        assert "sections_separately" in config
        assert "values_separately" in config

        # Check values match class attributes
        assert config["enabled"] == SettingsConfig.CACHE_ENABLED
        assert config["ttl"] == SettingsConfig.CACHE_TTL
        assert config["prefix"] == SettingsConfig.CACHE_PREFIX

    def test_get_validation_config(self):
        """Test get_validation_config method"""
        config = SettingsConfig.get_validation_config()

        assert isinstance(config, dict)
        assert "enabled" in config
        assert "strict_mode" in config
        assert "allow_unknown_sections" in config
        assert "allow_unknown_keys" in config

        # Check values match class attributes
        assert config["enabled"] == SettingsConfig.VALIDATION_ENABLED
        assert config["strict_mode"] == SettingsConfig.VALIDATION_STRICT_MODE
        assert (
            config["allow_unknown_sections"]
            == SettingsConfig.VALIDATION_ALLOW_UNKNOWN_SECTIONS
        )
        assert (
            config["allow_unknown_keys"]
            == SettingsConfig.VALIDATION_ALLOW_UNKNOWN_KEYS
        )

    def test_get_audit_config(self):
        """Test get_audit_config method"""
        config = SettingsConfig.get_audit_config()

        assert isinstance(config, dict)
        assert "enabled" in config
        assert "log_changes" in config
        assert "log_access" in config
        assert "retention_days" in config

        # Check values match class attributes
        assert config["enabled"] == SettingsConfig.AUDIT_ENABLED
        assert config["log_changes"] == SettingsConfig.AUDIT_LOG_CHANGES
        assert config["log_access"] == SettingsConfig.AUDIT_LOG_ACCESS
        assert config["retention_days"] == SettingsConfig.AUDIT_RETENTION_DAYS

    def test_get_security_config(self):
        """Test get_security_config method"""
        config = SettingsConfig.get_security_config()

        assert isinstance(config, dict)
        assert "require_auth_for_write" in config
        assert "require_admin_for_critical" in config
        assert "allow_reset_to_defaults" in config
        assert "critical_sections" in config
        assert "readonly_sections" in config

        # Check values match class attributes
        assert (
            config["require_auth_for_write"]
            == SettingsConfig.REQUIRE_AUTH_FOR_WRITE
        )
        assert (
            config["require_admin_for_critical"]
            == SettingsConfig.REQUIRE_ADMIN_FOR_CRITICAL
        )
        assert (
            config["allow_reset_to_defaults"]
            == SettingsConfig.ALLOW_RESET_TO_DEFAULTS
        )
        assert config["critical_sections"] == SettingsConfig.CRITICAL_SECTIONS
        assert config["readonly_sections"] == SettingsConfig.READONLY_SECTIONS

    def test_get_performance_config(self):
        """Test get_performance_config method"""
        config = SettingsConfig.get_performance_config()

        assert isinstance(config, dict)
        assert "max_settings_size" in config
        assert "max_sections_count" in config
        assert "max_values_per_section" in config

        # Check values match class attributes
        assert config["max_settings_size"] == SettingsConfig.MAX_SETTINGS_SIZE
        assert (
            config["max_sections_count"] == SettingsConfig.MAX_SECTIONS_COUNT
        )
        assert (
            config["max_values_per_section"]
            == SettingsConfig.MAX_VALUES_PER_SECTION
        )

    def test_get_metrics_config(self):
        """Test get_metrics_config method"""
        config = SettingsConfig.get_metrics_config()

        assert isinstance(config, dict)
        assert "enabled" in config
        assert "prefix" in config
        assert "update_interval" in config

        # Check values match class attributes
        assert config["enabled"] == SettingsConfig.METRICS_ENABLED
        assert config["prefix"] == SettingsConfig.METRICS_PREFIX
        assert (
            config["update_interval"] == SettingsConfig.METRICS_UPDATE_INTERVAL
        )

    def test_get_logging_config(self):
        """Test get_logging_config method"""
        config = SettingsConfig.get_logging_config()

        assert isinstance(config, dict)
        assert "level" in config
        assert "format" in config
        assert "file" in config

        # Check values match class attributes
        assert config["level"] == SettingsConfig.LOG_LEVEL
        assert config["format"] == SettingsConfig.LOG_FORMAT
        assert config["file"] == SettingsConfig.LOG_FILE

    def test_get_export_config(self):
        """Test get_export_config method"""
        config = SettingsConfig.get_export_config()

        assert isinstance(config, dict)
        assert "format" in config
        assert "compression" in config

        # Check values match class attributes
        assert config["format"] == SettingsConfig.EXPORT_FORMAT
        assert config["compression"] == SettingsConfig.EXPORT_COMPRESSION

    def test_get_import_config(self):
        """Test get_import_config method"""
        config = SettingsConfig.get_import_config()

        assert isinstance(config, dict)
        assert "merge_default" in config
        assert "backup_before_import" in config

        # Check values match class attributes
        assert config["merge_default"] == SettingsConfig.IMPORT_MERGE_DEFAULT
        assert (
            config["backup_before_import"]
            == SettingsConfig.IMPORT_BACKUP_BEFORE_IMPORT
        )

    def test_default_values_reasonable(self):
        """Test that default values are reasonable"""
        # Cache TTL should be reasonable (between 1 second and 1 hour)
        assert 1 <= SettingsConfig.CACHE_TTL <= 3600

        # Max settings size should be reasonable (at least 1MB)
        assert SettingsConfig.MAX_SETTINGS_SIZE >= 1024 * 1024

        # Max sections count should be reasonable
        assert 1 <= SettingsConfig.MAX_SECTIONS_COUNT <= 1000

        # Max values per section should be reasonable
        assert 1 <= SettingsConfig.MAX_VALUES_PER_SECTION <= 1000

        # Critical sections should include important ones
        assert "database" in SettingsConfig.CRITICAL_SECTIONS
        assert "security" in SettingsConfig.CRITICAL_SECTIONS

    def test_boolean_attributes(self):
        """Test that boolean attributes have correct types"""
        boolean_attrs = [
            "ENABLED",
            "CACHE_ENABLED",
            "VALIDATION_ENABLED",
            "AUDIT_ENABLED",
            "EXPORT_COMPRESSION",
            "IMPORT_MERGE_DEFAULT",
            "IMPORT_BACKUP_BEFORE_IMPORT",
            "VALIDATION_STRICT_MODE",
            "VALIDATION_ALLOW_UNKNOWN_SECTIONS",
            "VALIDATION_ALLOW_UNKNOWN_KEYS",
            "AUDIT_LOG_CHANGES",
            "AUDIT_LOG_ACCESS",
            "CACHE_SECTIONS_SEPARATELY",
            "CACHE_VALUES_SEPARATELY",
            "REQUIRE_AUTH_FOR_WRITE",
            "REQUIRE_ADMIN_FOR_CRITICAL",
            "ALLOW_RESET_TO_DEFAULTS",
            "METRICS_ENABLED",
        ]

        for attr in boolean_attrs:
            value = getattr(SettingsConfig, attr)
            assert isinstance(
                value, bool
            ), f"{attr} should be boolean, got {type(value)}"

    def test_string_attributes(self):
        """Test that string attributes have correct types"""
        string_attrs = [
            "EXPORT_FORMAT",
            "CACHE_PREFIX",
            "LOG_LEVEL",
            "LOG_FORMAT",
            "METRICS_PREFIX",
        ]

        for attr in string_attrs:
            value = getattr(SettingsConfig, attr)
            assert isinstance(
                value, str
            ), f"{attr} should be string, got {type(value)}"

    def test_numeric_attributes(self):
        """Test that numeric attributes have correct types and values"""
        numeric_attrs = [
            "CACHE_TTL",
            "AUDIT_RETENTION_DAYS",
            "MAX_SETTINGS_SIZE",
            "MAX_SECTIONS_COUNT",
            "MAX_VALUES_PER_SECTION",
            "METRICS_UPDATE_INTERVAL",
        ]

        for attr in numeric_attrs:
            value = getattr(SettingsConfig, attr)
            assert isinstance(
                value, (int, float)
            ), f"{attr} should be numeric, got {type(value)}"
            assert value > 0, f"{attr} should be positive, got {value}"

    def test_list_attributes(self):
        """Test that list attributes have correct types"""
        list_attrs = ["CRITICAL_SECTIONS", "READONLY_SECTIONS"]

        for attr in list_attrs:
            value = getattr(SettingsConfig, attr)
            assert isinstance(
                value, list
            ), f"{attr} should be list, got {type(value)}"

    def test_settings_config_instance(self):
        """Test that settings_config instance is properly created"""
        assert isinstance(settings_config, SettingsConfig)

        # Test that instance methods work
        default_settings = settings_config.get_default_settings()
        assert isinstance(default_settings, dict)
        assert len(default_settings) > 0

    def test_config_isolation(self):
        """Test that configuration methods return independent copies"""
        # Get multiple copies
        settings1 = SettingsConfig.get_default_settings()
        settings2 = SettingsConfig.get_default_settings()

        # Modify one
        settings1["new_section"] = {"key": "value"}

        # Other should be unchanged
        assert "new_section" not in settings2
        assert settings1 != settings2

    def test_critical_sections_completeness(self):
        """Test that critical sections list is complete"""
        # Critical sections should include system-critical components
        expected_critical = {"database", "security", "cache"}

        actual_critical = set(SettingsConfig.CRITICAL_SECTIONS)
        assert expected_critical.issubset(
            actual_critical
        ), "Missing critical sections"

    def test_readonly_sections_reasonable(self):
        """Test that readonly sections are reasonable"""
        readonly = SettingsConfig.READONLY_SECTIONS

        # Should be a small list
        assert len(readonly) <= 5, "Too many readonly sections"

        # Should include system sections
        assert "system" in readonly, "System section should be readonly"

    def test_performance_limits_reasonable(self):
        """Test that performance limits are reasonable"""
        # Settings size should be reasonable for memory
        assert (
            SettingsConfig.MAX_SETTINGS_SIZE <= 100 * 1024 * 1024
        ), "Max settings size too large"

        # Sections count should be reasonable
        assert (
            SettingsConfig.MAX_SECTIONS_COUNT <= 200
        ), "Max sections count too large"

        # Values per section should be reasonable
        assert (
            SettingsConfig.MAX_VALUES_PER_SECTION <= 500
        ), "Max values per section too large"
