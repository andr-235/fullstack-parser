"""
Shared test fixtures and configuration for Settings module tests

This module provides common test fixtures, mock objects, and test data
that can be reused across different test files in the Settings test suite.

Fixtures:
- mock_settings_repository: Mock SettingsRepository
- mock_settings_service: Mock SettingsService
- sample_settings_data: Sample settings data for testing
- sample_section_data: Sample section data for testing
- sample_invalid_data: Sample invalid data for validation testing
- mock_request: Mock FastAPI request
- mock_database_session: Mock database session
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, List

from src.settings.models import SettingsRepository
from src.settings.service import SettingsService
from src.settings.config import SettingsConfig


@pytest.fixture
def sample_settings_data():
    """Sample settings data for testing"""
    return {
        "vk_api": {
            "access_token": "test_token_12345",
            "api_version": "5.200",
            "requests_per_second": 3,
            "max_posts_per_request": 100,
        },
        "monitoring": {
            "scheduler_interval_seconds": 300,
            "max_concurrent_groups": 5,
            "enabled": True,
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


@pytest.fixture
def sample_section_data():
    """Sample section data for testing"""
    return {
        "vk_api": {
            "access_token": "new_token_67890",
            "api_version": "5.200",
            "requests_per_second": 5,
        }
    }


@pytest.fixture
def sample_invalid_data():
    """Sample invalid data for validation testing"""
    return {"invalid_section": {"invalid_key": "invalid_value"}}


@pytest.fixture
def sample_export_data():
    """Sample export data for testing"""
    return {
        "settings": {
            "vk_api": {
                "api_version": "5.200",
                "requests_per_second": 3,
            }
        },
        "exported_at": "2024-01-01T00:00:00Z",
        "version": "1.0",
        "format": "json",
    }


@pytest.fixture
def mock_database_session():
    """Create mock database session"""
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_request():
    """Create mock FastAPI request"""
    request = Mock()
    request.method = "GET"
    request.url = Mock()
    request.url.path = "/settings"
    request.headers = {}
    request.query_params = {}
    return request


@pytest.fixture
def mock_settings_repository():
    """Create mock SettingsRepository"""
    repo = Mock(spec=SettingsRepository)

    # Mock async methods
    repo.get_settings = AsyncMock()
    repo.save_settings = AsyncMock()
    repo.get_section = AsyncMock()
    repo.save_section = AsyncMock()
    repo.get_value = AsyncMock()
    repo.save_value = AsyncMock()
    repo.delete_section = AsyncMock()
    repo.reset_to_defaults = AsyncMock()
    repo.validate_settings = AsyncMock()
    repo.export_settings = AsyncMock()
    repo.import_settings = AsyncMock()
    repo.get_cache_stats = AsyncMock()
    repo.health_check = AsyncMock()

    return repo


@pytest.fixture
def mock_settings_service(mock_settings_repository):
    """Create mock SettingsService"""
    service = Mock(spec=SettingsService)

    # Configure service with mock repository
    service.repository = mock_settings_repository
    service.logger = Mock()

    # Mock async methods
    service.get_current_settings = AsyncMock()
    service.update_settings = AsyncMock()
    service.get_section = AsyncMock()
    service.update_section = AsyncMock()
    service.get_setting_value = AsyncMock()
    service.set_setting_value = AsyncMock()
    service.reset_to_defaults = AsyncMock()
    service.validate_settings = AsyncMock()
    service.export_settings = AsyncMock()
    service.import_settings = AsyncMock()
    service.get_health_status = AsyncMock()
    service.get_cache_stats = AsyncMock()
    service.clear_cache = AsyncMock()

    return service


@pytest.fixture
def real_settings_repository():
    """Create real SettingsRepository instance for integration tests"""
    return SettingsRepository()


@pytest.fixture
def real_settings_service():
    """Create real SettingsService instance for integration tests"""
    return SettingsService()


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def cleanup_event_loop():
    """Clean up event loop after each test"""
    yield
    # Cleanup code if needed


@pytest.fixture
def performance_timer():
    """Timer fixture for performance tests"""

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = datetime.now(timezone.utc)

        def stop(self):
            self.end_time = datetime.now(timezone.utc)

        @property
        def duration(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return 0

    return Timer()


@pytest.fixture
def validation_errors():
    """Sample validation errors for testing"""
    return {
        "vk_api": {
            "requests_per_second": "Must be a positive number",
            "api_version": "Must be a non-empty string",
        },
        "monitoring": {
            "scheduler_interval_seconds": "Must be a positive number",
        },
    }


@pytest.fixture
def health_check_response():
    """Sample health check response"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "cache": {
            "cache_valid": True,
            "cache_age_seconds": 120.5,
            "cache_size": 2048,
            "sections_cached": 4,
        },
        "settings_loaded": True,
        "sections_count": 4,
    }


@pytest.fixture
def cache_stats_response():
    """Sample cache stats response"""
    return {
        "cache_valid": True,
        "cache_age_seconds": 60.0,
        "cache_size": 1536,
        "sections_cached": 3,
    }


@pytest.fixture
def export_response():
    """Sample export response"""
    return {
        "settings": {
            "vk_api": {"api_version": "5.199"},
            "database": {"pool_size": 10},
        },
        "exported_at": "2024-01-01T00:00:00Z",
        "version": "1.0",
        "format": "json",
        "sections_count": 2,
    }


@pytest.fixture
def validation_result():
    """Sample validation result"""
    return {
        "valid": True,
        "issues": {},
        "total_sections": 3,
        "sections_with_issues": 0,
    }


@pytest.fixture
def invalid_validation_result():
    """Sample invalid validation result"""
    return {
        "valid": False,
        "issues": {
            "size": "Settings size 2048000 exceeds limit 1048576",
            "sections_count": "Too many sections: 60 > 50",
        },
        "total_sections": 60,
        "sections_with_issues": 2,
    }


@pytest.fixture
def generate_test_settings():
    """Generate test settings data"""

    def _generate(
        section_count: int, values_per_section: int = 5
    ) -> Dict[str, Any]:
        settings = {}
        for i in range(section_count):
            section_name = f"section_{i + 1}"
            section_data = {}
            for j in range(values_per_section):
                key = f"key_{j + 1}"
                value = f"value_{i + 1}_{j + 1}"
                section_data[key] = value
            settings[section_name] = section_data
        return settings

    return _generate


@pytest.fixture
def generate_large_settings():
    """Generate large settings for performance testing"""

    def _generate(size_mb: float) -> Dict[str, Any]:
        """Generate settings that approximate the given size in MB"""
        # Rough estimation: each character is ~1 byte
        target_size = int(size_mb * 1024 * 1024)
        settings = {}

        section_num = 1
        while len(str(settings).encode("utf-8")) < target_size:
            section_name = f"large_section_{section_num}"
            section_data = {}

            key_num = 1
            while len(str(section_data).encode("utf-8")) < (
                target_size // 50
            ):  # Distribute across sections
                key = f"large_key_{key_num}"
                # Create large values
                value = "x" * 1000  # 1KB per value
                section_data[key] = value
                key_num += 1

            settings[section_name] = section_data
            section_num += 1

        return settings

    return _generate


@pytest.fixture
def simulate_repository_error():
    """Simulate repository errors"""

    def _simulate(error_type: str):
        if error_type == "connection_error":
            from ..exceptions import ServiceUnavailableError

            return ServiceUnavailableError("Database connection failed")
        elif error_type == "validation_error":
            from ..exceptions import ValidationError

            return ValidationError("Invalid settings data")
        elif error_type == "timeout_error":
            import asyncio

            return asyncio.TimeoutError("Operation timed out")
        else:
            return Exception(f"Unknown error: {error_type}")

    return _simulate


@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def test_config():
    """Test configuration data"""
    return {
        "enabled": True,
        "cache_enabled": True,
        "cache_ttl": 300,
        "validation_enabled": True,
        "max_settings_size": 1024 * 1024,
        "max_sections_count": 50,
        "max_values_per_section": 100,
    }


@pytest.fixture
def mock_response_factory():
    """Factory for creating mock responses"""

    def _create_response(success: bool, data: Any = None, message: str = None):
        response = {"success": success}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response

    return _create_response


@pytest.fixture
def async_delay():
    """Create async delay for testing"""

    async def _delay(seconds: float):
        await asyncio.sleep(seconds)

    return _delay


@pytest.fixture
def validate_response_structure():
    """Validate response structure"""

    def _validate(response: Dict[str, Any], expected_fields: List[str]):
        """Validate that response contains expected fields"""
        for field in expected_fields:
            assert field in response, f"Missing field: {field}"

        assert "success" in response
        assert isinstance(response["success"], bool)

        if response["success"]:
            assert "data" in response

    return _validate
