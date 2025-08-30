"""
Unit tests for SettingsRepository

Tests cover all repository methods including:
- get_settings
- save_settings
- get_section
- save_section
- get_value
- save_value
- delete_section
- reset_to_defaults
- validate_settings
- export_settings
- import_settings
- cache management
- health checks
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.settings.models import SettingsRepository
from src.settings.config import SettingsConfig


class TestSettingsRepository:
    """Test suite for SettingsRepository"""

    @pytest.fixture
    def repository(self):
        """Create SettingsRepository instance"""
        return SettingsRepository()

    @pytest.fixture
    def sample_settings(self, sample_settings_data):
        """Sample settings for testing"""
        return sample_settings_data

    @pytest.fixture
    def large_settings(self, generate_large_settings):
        """Large settings for performance testing"""
        return generate_large_settings(0.5)  # 0.5MB

    @pytest.mark.asyncio
    async def test_get_settings_with_cache(self, repository, sample_settings):
        """Test getting settings when cache is valid"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_settings()

        # Assert
        assert result == sample_settings
        # Should return cached result without calling config

    @pytest.mark.asyncio
    async def test_get_settings_without_cache(
        self, repository, sample_settings
    ):
        """Test getting settings when cache is invalid"""
        # Arrange
        with patch("src.settings.models.settings_config") as mock_config:
            mock_config.get_default_settings.return_value = sample_settings

            # Act
            result = await repository.get_settings()

            # Assert
            assert result == sample_settings
            mock_config.get_default_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_settings_cache_expiry(
        self, repository, sample_settings
    ):
        """Test cache expiry functionality"""
        # Arrange
        repository._settings_cache = sample_settings
        # Set timestamp to more than 5 minutes ago
        old_time = datetime.utcnow() - timedelta(minutes=6)
        repository._settings_cache["cache_timestamp"] = old_time.isoformat()

        with patch("src.settings.models.settings_config") as mock_config:
            mock_config.get_default_settings.return_value = sample_settings

            # Act
            result = await repository.get_settings()

            # Assert
            assert result == sample_settings
            mock_config.get_default_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_settings(self, repository, sample_settings):
        """Test saving settings"""
        # Act
        await repository.save_settings(sample_settings)

        # Assert
        assert repository._settings_cache == sample_settings
        assert "cache_timestamp" in repository._settings_cache

    @pytest.mark.asyncio
    async def test_get_section_exists(self, repository, sample_settings):
        """Test getting existing section"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_section("vk_api")

        # Assert
        assert result == sample_settings["vk_api"]

    @pytest.mark.asyncio
    async def test_get_section_not_exists(self, repository, sample_settings):
        """Test getting non-existing section"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_section("nonexistent")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_save_section(self, repository, sample_settings):
        """Test saving section"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )
        new_section = {"new_key": "new_value"}

        # Act
        await repository.save_section("new_section", new_section)

        # Assert
        assert repository._settings_cache["new_section"] == new_section

    @pytest.mark.asyncio
    async def test_get_value_exists(self, repository, sample_settings):
        """Test getting existing setting value"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_value("vk_api", "api_version")

        # Assert
        assert result == "5.199"

    @pytest.mark.asyncio
    async def test_get_value_section_not_exists(
        self, repository, sample_settings
    ):
        """Test getting value when section doesn't exist"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_value("nonexistent_section", "key")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_value_key_not_exists(self, repository, sample_settings):
        """Test getting value when key doesn't exist"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_value("vk_api", "nonexistent_key")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_save_value_existing_section(
        self, repository, sample_settings
    ):
        """Test saving value to existing section"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        await repository.save_value("vk_api", "new_key", "new_value")

        # Assert
        assert repository._settings_cache["vk_api"]["new_key"] == "new_value"

    @pytest.mark.asyncio
    async def test_save_value_new_section(self, repository, sample_settings):
        """Test saving value to new section"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        await repository.save_value("new_section", "key", "value")

        # Assert
        assert repository._settings_cache["new_section"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_delete_section_exists(self, repository, sample_settings):
        """Test deleting existing section"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.delete_section("vk_api")

        # Assert
        assert result is True
        assert "vk_api" not in repository._settings_cache

    @pytest.mark.asyncio
    async def test_delete_section_not_exists(
        self, repository, sample_settings
    ):
        """Test deleting non-existing section"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.delete_section("nonexistent")

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_to_defaults(self, repository, sample_settings):
        """Test resetting settings to defaults"""
        # Arrange
        repository._settings_cache = {"modified": "data"}
        with patch("src.settings.models.settings_config") as mock_config:
            mock_config.get_default_settings.return_value = sample_settings

            # Act
            result = await repository.reset_to_defaults()

            # Assert
            assert result == sample_settings
            assert repository._settings_cache == sample_settings
            assert repository._cache_expiry == {}

    @pytest.mark.asyncio
    async def test_validate_settings_valid(
        self, repository, sample_settings, validation_result
    ):
        """Test validating valid settings"""
        # Act
        result = await repository.validate_settings(sample_settings)

        # Assert
        assert result["valid"] is True
        assert result["issues"] == {}
        assert result["total_sections"] == len(sample_settings)

    @pytest.mark.asyncio
    async def test_validate_settings_size_limit_exceeded(
        self, repository, large_settings, invalid_validation_result
    ):
        """Test validating settings that exceed size limit"""
        # Act
        result = await repository.validate_settings(large_settings)

        # Assert
        assert result["valid"] is False
        assert "size" in result["issues"]

    @pytest.mark.asyncio
    async def test_validate_settings_too_many_sections(
        self, repository, generate_test_settings
    ):
        """Test validating settings with too many sections"""
        # Arrange
        too_many_sections = generate_test_settings(
            60
        )  # Exceeds MAX_SECTIONS_COUNT

        # Act
        result = await repository.validate_settings(too_many_sections)

        # Assert
        assert result["valid"] is False
        assert "sections_count" in result["issues"]

    @pytest.mark.asyncio
    async def test_validate_settings_section_too_many_values(self, repository):
        """Test validating section with too many values"""
        # Arrange
        large_section = {f"key_{i}": f"value_{i}" for i in range(200)}
        settings = {"large_section": large_section}

        # Act
        result = await repository.validate_settings(settings)

        # Assert
        assert result["valid"] is False
        assert "large_section" in result["issues"]
        assert "values_count" in result["issues"]["large_section"]

    @pytest.mark.asyncio
    async def test_validate_settings_invalid_section_type(self, repository):
        """Test validating settings with invalid section type"""
        # Arrange
        invalid_settings = {"invalid_section": "not_a_dict"}

        # Act
        result = await repository.validate_settings(invalid_settings)

        # Assert
        assert result["valid"] is False
        assert "invalid_section" in result["issues"]
        assert "type" in result["issues"]["invalid_section"]

    @pytest.mark.asyncio
    async def test_validate_section_vk_api_valid(self, repository):
        """Test validating valid VK API section"""
        # Arrange
        valid_section = {"requests_per_second": 5, "api_version": "5.199"}

        # Act
        result = await repository._validate_section("vk_api", valid_section)

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_validate_section_vk_api_invalid(self, repository):
        """Test validating invalid VK API section"""
        # Arrange
        invalid_section = {"requests_per_second": -1, "api_version": ""}

        # Act
        result = await repository._validate_section("vk_api", invalid_section)

        # Assert
        assert "requests_per_second" in result
        assert "api_version" in result

    @pytest.mark.asyncio
    async def test_validate_section_monitoring_valid(self, repository):
        """Test validating valid monitoring section"""
        # Arrange
        valid_section = {
            "scheduler_interval_seconds": 300,
            "max_concurrent_groups": 5,
        }

        # Act
        result = await repository._validate_section(
            "monitoring", valid_section
        )

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_validate_section_monitoring_invalid(self, repository):
        """Test validating invalid monitoring section"""
        # Arrange
        invalid_section = {
            "scheduler_interval_seconds": 0,
            "max_concurrent_groups": -1,
        }

        # Act
        result = await repository._validate_section(
            "monitoring", invalid_section
        )

        # Assert
        assert "scheduler_interval_seconds" in result
        assert "max_concurrent_groups" in result

    @pytest.mark.asyncio
    async def test_validate_section_database_valid(self, repository):
        """Test validating valid database section"""
        # Arrange
        valid_section = {"pool_size": 10, "max_overflow": 20}

        # Act
        result = await repository._validate_section("database", valid_section)

        # Assert
        assert result == {}

    @pytest.mark.asyncio
    async def test_validate_section_database_invalid(self, repository):
        """Test validating invalid database section"""
        # Arrange
        invalid_section = {"pool_size": 0, "max_overflow": -1}

        # Act
        result = await repository._validate_section(
            "database", invalid_section
        )

        # Assert
        assert "pool_size" in result
        assert "max_overflow" in result

    @pytest.mark.asyncio
    async def test_export_settings(self, repository, sample_settings):
        """Test exporting settings"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.export_settings("json")

        # Assert
        assert "settings" in result
        assert result["settings"] == sample_settings
        assert "exported_at" in result
        assert "version" in result
        assert "format" in result
        assert result["format"] == "json"
        assert "sections_count" in result
        assert result["sections_count"] == len(sample_settings)

    @pytest.mark.asyncio
    async def test_import_settings_merge_true(
        self, repository, sample_settings, sample_export_data
    ):
        """Test importing settings with merge=True"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.import_settings(
            sample_export_data, merge=True
        )

        # Assert
        # Should contain both original and imported settings
        assert "vk_api" in result
        assert "database" in result

    @pytest.mark.asyncio
    async def test_import_settings_merge_false(
        self, repository, sample_settings, sample_export_data
    ):
        """Test importing settings with merge=False"""
        # Arrange
        repository._settings_cache = sample_settings.copy()
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.import_settings(
            sample_export_data, merge=False
        )

        # Assert
        # Should contain only imported settings
        assert result == sample_export_data["settings"]
        assert "vk_api" in result
        assert "database" not in result  # Original section should be gone

    @pytest.mark.asyncio
    async def test_import_settings_validation_error(self, repository):
        """Test importing invalid settings"""
        # Arrange
        invalid_import_data = {"settings": {"invalid_section": "not_a_dict"}}

        # Act & Assert
        with pytest.raises(ValueError):
            await repository.import_settings(invalid_import_data)

    @pytest.mark.asyncio
    async def test_deep_merge(self, repository):
        """Test deep merging of dictionaries"""
        # Arrange
        base = {
            "vk_api": {"api_version": "5.199", "requests_per_second": 3},
            "database": {"pool_size": 10},
        }
        update = {
            "vk_api": {"requests_per_second": 5},
            "monitoring": {"enabled": True},
        }

        # Act
        result = repository._deep_merge(base, update)

        # Assert
        expected = {
            "vk_api": {"api_version": "5.199", "requests_per_second": 5},
            "database": {"pool_size": 10},
            "monitoring": {"enabled": True},
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_deep_merge_nested(self, repository):
        """Test deep merging of nested dictionaries"""
        # Arrange
        base = {
            "vk_api": {
                "limits": {"posts": 100, "comments": 50},
                "version": "5.199",
            }
        }
        update = {"vk_api": {"limits": {"posts": 200}, "timeout": 30}}

        # Act
        result = repository._deep_merge(base, update)

        # Assert
        expected = {
            "vk_api": {
                "limits": {"posts": 200, "comments": 50},
                "version": "5.199",
                "timeout": 30,
            }
        }
        assert result == expected

    def test_is_cache_valid_true(self, repository, sample_settings):
        """Test cache validity when cache is fresh"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = repository._is_cache_valid()

        # Assert
        assert result is True

    def test_is_cache_valid_false_no_cache(self, repository):
        """Test cache validity when no cache exists"""
        # Act
        result = repository._is_cache_valid()

        # Assert
        assert result is False

    def test_is_cache_valid_false_expired(self, repository, sample_settings):
        """Test cache validity when cache is expired"""
        # Arrange
        repository._settings_cache = sample_settings
        old_time = datetime.utcnow() - timedelta(minutes=10)
        repository._settings_cache["cache_timestamp"] = old_time.isoformat()

        # Act
        result = repository._is_cache_valid()

        # Assert
        assert result is False

    def test_update_cache(self, repository, sample_settings):
        """Test updating cache"""
        # Act
        repository._update_cache(sample_settings)

        # Assert
        assert repository._settings_cache == sample_settings
        assert "cache_timestamp" in repository._settings_cache

    def test_clear_cache(self, repository, sample_settings):
        """Test clearing cache"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._cache_expiry = {"some": "data"}

        # Act
        repository._clear_cache()

        # Assert
        assert repository._settings_cache == {}
        assert repository._cache_expiry == {}

    @pytest.mark.asyncio
    async def test_get_cache_stats(
        self, repository, sample_settings, cache_stats_response
    ):
        """Test getting cache statistics"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.get_cache_stats()

        # Assert
        assert "cache_valid" in result
        assert "cache_age_seconds" in result
        assert "cache_size" in result
        assert "sections_cached" in result
        assert result["cache_valid"] is True
        assert result["sections_cached"] == len(sample_settings)

    @pytest.mark.asyncio
    async def test_get_cache_stats_empty_cache(self, repository):
        """Test getting cache statistics with empty cache"""
        # Act
        result = await repository.get_cache_stats()

        # Assert
        assert result["cache_valid"] is False
        assert result["cache_age_seconds"] == 0
        assert result["cache_size"] == 0
        assert result["sections_cached"] == 0

    @pytest.mark.asyncio
    async def test_health_check_success(self, repository, sample_settings):
        """Test successful health check"""
        # Arrange
        repository._settings_cache = sample_settings
        repository._settings_cache["cache_timestamp"] = (
            datetime.utcnow().isoformat()
        )

        # Act
        result = await repository.health_check()

        # Assert
        assert result["status"] == "healthy"
        assert "cache_stats" in result
        assert result["settings_loaded"] is True
        assert result["sections_count"] == len(sample_settings)
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_check_failure(self, repository):
        """Test health check failure"""
        # Arrange
        repository._settings_cache = {}  # Empty cache

        # Act
        result = await repository.health_check()

        # Assert
        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "timestamp" in result
