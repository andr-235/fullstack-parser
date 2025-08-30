"""
Unit tests for SettingsService

Tests cover all service methods including:
- get_current_settings
- update_settings
- get_section
- update_section
- get_setting_value
- set_setting_value
- reset_to_defaults
- validate_settings
- export_settings
- import_settings
- get_health_status
- get_cache_stats
- clear_cache
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.settings.service import SettingsService
from src.settings.config import SettingsConfig
from src.exceptions import ValidationError, ServiceUnavailableError


class TestSettingsService:
    """Test suite for SettingsService"""

    @pytest.fixture
    def service(self, mock_settings_repository, mock_logger):
        """Create SettingsService instance with mocked dependencies"""
        service = SettingsService(repository=mock_settings_repository)
        service.logger = mock_logger
        return service

    @pytest.fixture
    def sample_settings(self, sample_settings_data):
        """Sample settings for testing"""
        return sample_settings_data

    @pytest.fixture
    def sample_updates(self):
        """Sample settings updates"""
        return {
            "vk_api": {"requests_per_second": 5, "api_version": "5.200"},
            "monitoring": {"enabled": False},
        }

    @pytest.mark.asyncio
    async def test_get_current_settings_success(
        self, service, sample_settings, mock_settings_repository
    ):
        """Test successful retrieval of current settings"""
        # Arrange
        mock_settings_repository.get_settings.return_value = sample_settings

        # Act
        result = await service.get_current_settings()

        # Assert
        assert result == sample_settings
        mock_settings_repository.get_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_settings_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test failure in retrieving current settings"""
        # Arrange
        mock_settings_repository.get_settings.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.get_current_settings()

        assert "ERROR_SETTINGS_LOAD_FAILED" in str(exc_info.value)
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_success(
        self,
        service,
        sample_settings,
        sample_updates,
        mock_settings_repository,
        mock_logger,
    ):
        """Test successful settings update"""
        # Arrange
        mock_settings_repository.get_settings.return_value = sample_settings
        expected_updated = {
            "vk_api": {
                "access_token": "test_token_12345",
                "api_version": "5.200",  # Updated
                "requests_per_second": 5,  # Updated
                "max_posts_per_request": 100,
            },
            "monitoring": {
                "scheduler_interval_seconds": 300,
                "max_concurrent_groups": 5,
                "enabled": False,  # Updated
            },
            "database": {
                "pool_size": 10,
                "max_overflow": 20,
                "echo": False,
            },
            "logging": {
                "level": "INFO",
                "format": "json",
            },
        }

        # Act
        result = await service.update_settings(sample_updates)

        # Assert
        assert result == expected_updated
        mock_settings_repository.get_settings.assert_called_once()
        mock_settings_repository.save_settings.assert_called_once_with(
            expected_updated
        )
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_with_validation_failure(
        self, service, sample_settings, mock_settings_repository
    ):
        """Test settings update with validation failure"""
        # Arrange
        invalid_updates = {
            "vk_api": {
                "requests_per_second": -1,  # Invalid negative value
            }
        }
        mock_settings_repository.get_settings.return_value = sample_settings
        mock_settings_repository.validate_settings.side_effect = (
            ValidationError("Invalid settings")
        )

        # Act & Assert
        with pytest.raises(ValidationError):
            await service.update_settings(invalid_updates)

    @pytest.mark.asyncio
    async def test_update_settings_save_failure(
        self,
        service,
        sample_settings,
        sample_updates,
        mock_settings_repository,
        mock_logger,
    ):
        """Test settings update with save failure"""
        # Arrange
        mock_settings_repository.get_settings.return_value = sample_settings
        mock_settings_repository.save_settings.side_effect = Exception(
            "Save failed"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.update_settings(sample_updates)

        assert "ERROR_SETTINGS_UPDATE_FAILED" in str(exc_info.value)
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_section_success(
        self, service, sample_settings, mock_settings_repository
    ):
        """Test successful section retrieval"""
        # Arrange
        section_name = "vk_api"
        expected_section = sample_settings[section_name]
        mock_settings_repository.get_section.return_value = expected_section

        # Act
        result = await service.get_section(section_name)

        # Assert
        assert result == expected_section
        mock_settings_repository.get_section.assert_called_once_with(
            section_name
        )

    @pytest.mark.asyncio
    async def test_get_section_not_found(
        self, service, mock_settings_repository
    ):
        """Test section retrieval when section doesn't exist"""
        # Arrange
        section_name = "nonexistent"
        mock_settings_repository.get_section.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.get_section(section_name)

        assert "ERROR_INVALID_SETTINGS_SECTION" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_section_repository_error(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test section retrieval with repository error"""
        # Arrange
        section_name = "vk_api"
        mock_settings_repository.get_section.side_effect = Exception(
            "Repository error"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError):
            await service.get_section(section_name)

        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_section_success(
        self,
        service,
        sample_section_data,
        mock_settings_repository,
        mock_logger,
    ):
        """Test successful section update"""
        # Arrange
        section_name = "vk_api"
        section_data = sample_section_data[section_name]
        mock_settings_repository.get_section.return_value = {
            "existing": "data"
        }

        # Act
        result = await service.update_section(section_name, section_data)

        # Assert
        assert result == section_data
        mock_settings_repository.get_section.assert_called_once_with(
            section_name
        )
        mock_settings_repository.save_section.assert_called_once_with(
            section_name, section_data
        )
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_section_not_found(
        self, service, mock_settings_repository
    ):
        """Test section update when section doesn't exist"""
        # Arrange
        section_name = "nonexistent"
        section_data = {"key": "value"}
        mock_settings_repository.get_section.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError):
            await service.update_section(section_name, section_data)

    @pytest.mark.asyncio
    async def test_update_section_validation_error(
        self, service, mock_settings_repository
    ):
        """Test section update with validation error"""
        # Arrange
        section_name = "vk_api"
        invalid_data = {"requests_per_second": -1}
        mock_settings_repository.get_section.return_value = {
            "existing": "data"
        }

        # Act & Assert
        with pytest.raises(ValidationError):
            await service.update_section(section_name, invalid_data)

    @pytest.mark.asyncio
    async def test_get_setting_value_success(
        self, service, mock_settings_repository
    ):
        """Test successful setting value retrieval"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        expected_value = "5.199"
        mock_settings_repository.get_value.return_value = expected_value

        # Act
        result = await service.get_setting_value(section_name, key)

        # Assert
        assert result == expected_value
        mock_settings_repository.get_value.assert_called_once_with(
            section_name, key
        )

    @pytest.mark.asyncio
    async def test_get_setting_value_not_found(
        self, service, mock_settings_repository
    ):
        """Test setting value retrieval when value doesn't exist"""
        # Arrange
        section_name = "vk_api"
        key = "nonexistent_key"
        mock_settings_repository.get_value.return_value = None

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.get_setting_value(section_name, key)

        assert "ERROR_SETTING_NOT_FOUND" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_setting_value_success(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test successful setting value update"""
        # Arrange
        section_name = "vk_api"
        key = "api_version"
        value = "5.200"
        expected_section = {"api_version": "5.200", "requests_per_second": 3}
        mock_settings_repository.get_section.return_value = {
            "api_version": "5.199",
            "requests_per_second": 3,
        }

        # Act
        result = await service.set_setting_value(section_name, key, value)

        # Assert
        assert result == expected_section
        mock_settings_repository.save_value.assert_called_once_with(
            section_name, key, value
        )
        mock_settings_repository.get_section.assert_called_once_with(
            section_name
        )
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_setting_value_validation_error(
        self, service, mock_settings_repository
    ):
        """Test setting value update with validation error"""
        # Arrange
        section_name = "vk_api"
        key = "requests_per_second"
        invalid_value = -1

        # Act & Assert
        with pytest.raises(ValidationError):
            await service.set_setting_value(section_name, key, invalid_value)

    @pytest.mark.asyncio
    async def test_reset_to_defaults_success(
        self, service, sample_settings, mock_settings_repository, mock_logger
    ):
        """Test successful reset to defaults"""
        # Arrange
        mock_settings_repository.reset_to_defaults.return_value = (
            sample_settings
        )

        # Act
        result = await service.reset_to_defaults()

        # Assert
        assert result == sample_settings
        mock_settings_repository.reset_to_defaults.assert_called_once()
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_to_defaults_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test reset to defaults failure"""
        # Arrange
        mock_settings_repository.reset_to_defaults.side_effect = Exception(
            "Reset failed"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError):
            await service.reset_to_defaults()

        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_settings_success(
        self,
        service,
        sample_settings,
        validation_result,
        mock_settings_repository,
    ):
        """Test successful settings validation"""
        # Arrange
        mock_settings_repository.validate_settings.return_value = (
            validation_result
        )

        # Act
        result = await service.validate_settings(sample_settings)

        # Assert
        assert result == validation_result
        mock_settings_repository.validate_settings.assert_called_once_with(
            sample_settings
        )

    @pytest.mark.asyncio
    async def test_validate_settings_without_params(
        self,
        service,
        sample_settings,
        validation_result,
        mock_settings_repository,
    ):
        """Test settings validation without parameters (uses current settings)"""
        # Arrange
        mock_settings_repository.get_settings.return_value = sample_settings
        mock_settings_repository.validate_settings.return_value = (
            validation_result
        )

        # Act
        result = await service.validate_settings()

        # Assert
        assert result == validation_result
        mock_settings_repository.get_settings.assert_called_once()
        mock_settings_repository.validate_settings.assert_called_once_with(
            sample_settings
        )

    @pytest.mark.asyncio
    async def test_validate_settings_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test settings validation failure"""
        # Arrange
        mock_settings_repository.validate_settings.side_effect = Exception(
            "Validation failed"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.validate_settings()

        assert "ERROR_SETTINGS_VALIDATION_FAILED" in str(exc_info.value)
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_settings_success(
        self, service, export_response, mock_settings_repository, mock_logger
    ):
        """Test successful settings export"""
        # Arrange
        format_type = "json"
        mock_settings_repository.export_settings.return_value = export_response

        # Act
        result = await service.export_settings(format_type)

        # Assert
        assert result == export_response
        mock_settings_repository.export_settings.assert_called_once_with(
            format_type
        )
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_settings_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test settings export failure"""
        # Arrange
        mock_settings_repository.export_settings.side_effect = Exception(
            "Export failed"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError):
            await service.export_settings()

        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_settings_success(
        self,
        service,
        sample_export_data,
        mock_settings_repository,
        mock_logger,
    ):
        """Test successful settings import"""
        # Arrange
        import_data = sample_export_data
        merge = True
        expected_result = import_data["settings"]
        mock_settings_repository.import_settings.return_value = expected_result

        # Act
        result = await service.import_settings(import_data, merge)

        # Assert
        assert result == expected_result
        mock_settings_repository.import_settings.assert_called_once_with(
            import_data, merge
        )
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_settings_invalid_data(self, service):
        """Test settings import with invalid data"""
        # Arrange
        invalid_data = {"no_settings_field": True}

        # Act & Assert
        with pytest.raises(ValidationError):
            await service.import_settings(invalid_data)

    @pytest.mark.asyncio
    async def test_import_settings_failure(
        self,
        service,
        sample_export_data,
        mock_settings_repository,
        mock_logger,
    ):
        """Test settings import failure"""
        # Arrange
        mock_settings_repository.import_settings.side_effect = Exception(
            "Import failed"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError):
            await service.import_settings(sample_export_data)

        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_health_status_success(
        self, service, health_check_response, mock_settings_repository
    ):
        """Test successful health status retrieval"""
        # Arrange
        mock_settings_repository.health_check.return_value = {
            "status": "healthy",
            "cache_entries": 5,
            "total_requests": 100,
        }
        mock_settings_repository.get_cache_stats.return_value = {
            "cache_valid": True,
            "cache_age_seconds": 120.5,
            "cache_size": 2048,
            "sections_cached": 4,
        }

        # Act
        result = await service.get_health_status()

        # Assert
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "cache" in result
        assert result["settings_loaded"] is True
        assert result["sections_count"] == 4

    @pytest.mark.asyncio
    async def test_get_health_status_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test health status retrieval failure"""
        # Arrange
        mock_settings_repository.health_check.side_effect = Exception(
            "Health check failed"
        )

        # Act
        result = await service.get_health_status()

        # Assert
        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "timestamp" in result
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cache_stats_success(
        self, service, cache_stats_response, mock_settings_repository
    ):
        """Test successful cache stats retrieval"""
        # Arrange
        mock_settings_repository.get_cache_stats.return_value = (
            cache_stats_response
        )

        # Act
        result = await service.get_cache_stats()

        # Assert
        assert result == cache_stats_response
        mock_settings_repository.get_cache_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cache_stats_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test cache stats retrieval failure"""
        # Arrange
        mock_settings_repository.get_cache_stats.side_effect = Exception(
            "Cache stats failed"
        )

        # Act
        result = await service.get_cache_stats()

        # Assert
        assert result == {"error": "Cache stats failed"}
        mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_cache_success(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test successful cache clearing"""
        # Arrange
        mock_settings_repository.get_settings.return_value = {}

        # Act
        result = await service.clear_cache()

        # Assert
        assert result is True
        mock_settings_repository.get_settings.assert_called_once()
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_cache_failure(
        self, service, mock_settings_repository, mock_logger
    ):
        """Test cache clearing failure"""
        # Arrange
        mock_settings_repository.get_settings.side_effect = Exception(
            "Cache clear failed"
        )

        # Act
        result = await service.clear_cache()

        # Assert
        assert result is False
        mock_logger.error.assert_called_once()

    def test_merge_settings_basic(self, service):
        """Test basic settings merging"""
        # Arrange
        base = {
            "vk_api": {"api_version": "5.199", "requests_per_second": 3},
            "database": {"pool_size": 10},
        }
        updates = {
            "vk_api": {"requests_per_second": 5},
            "monitoring": {"enabled": True},
        }

        # Act
        result = service._merge_settings(base, updates)

        # Assert
        expected = {
            "vk_api": {"api_version": "5.199", "requests_per_second": 5},
            "database": {"pool_size": 10},
            "monitoring": {"enabled": True},
        }
        assert result == expected

    def test_merge_settings_overwrite_non_dict(self, service):
        """Test merging when update value is not a dict"""
        # Arrange
        base = {"vk_api": {"api_version": "5.199"}}
        updates = {"vk_api": "new_value"}

        # Act
        result = service._merge_settings(base, updates)

        # Assert
        assert result == {"vk_api": "new_value"}

    async def test_validate_section_size_limit(self, service):
        """Test section size validation"""
        # Arrange
        section_name = "test_section"
        large_section = {
            f"key_{i}": f"value_{i}" for i in range(200)
        }  # Exceeds MAX_VALUES_PER_SECTION

        # Act & Assert
        with pytest.raises(ValidationError):
            await service._validate_section(section_name, large_section)

    async def test_validate_setting_value_vk_api(self, service):
        """Test VK API setting value validation"""
        # Valid cases
        await service._validate_setting_value(
            "vk_api", "requests_per_second", 5
        )
        await service._validate_setting_value("vk_api", "api_version", "5.199")

        # Invalid cases
        with pytest.raises(ValidationError):
            await service._validate_setting_value(
                "vk_api", "requests_per_second", -1
            )

        with pytest.raises(ValidationError):
            await service._validate_setting_value("vk_api", "api_version", "")

    async def test_validate_setting_value_monitoring(self, service):
        """Test monitoring setting value validation"""
        # Valid cases
        await service._validate_setting_value(
            "monitoring", "scheduler_interval_seconds", 300.5
        )
        await service._validate_setting_value(
            "monitoring", "max_concurrent_groups", 10
        )

        # Invalid cases
        with pytest.raises(ValidationError):
            await service._validate_setting_value(
                "monitoring", "scheduler_interval_seconds", 0
            )

        with pytest.raises(ValidationError):
            await service._validate_setting_value(
                "monitoring", "max_concurrent_groups", 0
            )

    async def test_validate_setting_value_database(self, service):
        """Test database setting value validation"""
        # Valid cases
        await service._validate_setting_value("database", "pool_size", 20)

        # Invalid cases
        with pytest.raises(ValidationError):
            await service._validate_setting_value("database", "pool_size", 0)

    async def test_validate_vk_api_section(self, service):
        """Test VK API section validation"""
        # Valid section
        valid_section = {"requests_per_second": 5, "api_version": "5.199"}
        result = await service._validate_vk_api_section(valid_section)
        assert result == {}

        # Invalid section
        invalid_section = {"requests_per_second": -1, "api_version": ""}
        result = await service._validate_vk_api_section(invalid_section)
        assert "requests_per_second" in result
        assert "api_version" in result

    async def test_validate_monitoring_section(self, service):
        """Test monitoring section validation"""
        # Valid section
        valid_section = {
            "scheduler_interval_seconds": 300,
            "max_concurrent_groups": 5,
        }
        result = await service._validate_monitoring_section(valid_section)
        assert result == {}

        # Invalid section
        invalid_section = {
            "scheduler_interval_seconds": 0,
            "max_concurrent_groups": -1,
        }
        result = await service._validate_monitoring_section(invalid_section)
        assert "scheduler_interval_seconds" in result
        assert "max_concurrent_groups" in result

    async def test_validate_database_section(self, service):
        """Test database section validation"""
        # Valid section
        valid_section = {"pool_size": 10, "max_overflow": 20}
        result = await service._validate_database_section(valid_section)
        assert result == {}

        # Invalid section
        invalid_section = {"pool_size": 0, "max_overflow": -1}
        result = await service._validate_database_section(invalid_section)
        assert "pool_size" in result
        assert "max_overflow" in result
