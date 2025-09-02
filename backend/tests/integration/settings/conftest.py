"""
Configuration and fixtures for Settings module integration tests

Provides integration-level fixtures, test data, and setup for testing
complete workflows and component interactions.
"""

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from typing import Dict, Any

from src.settings.service import SettingsService
from src.settings.models import SettingsRepository
from src.settings.config import SettingsConfig


@pytest.fixture
def mock_settings_service():
    """Mock SettingsService for integration tests"""
    service = AsyncMock(spec=SettingsService)

    # Configure common mock responses
    service.get_current_settings = AsyncMock()
    service.update_settings = AsyncMock()
    service.validate_settings = AsyncMock()
    service.reset_to_defaults = AsyncMock()
    service.get_settings_history = AsyncMock()
    service.export_settings = AsyncMock()
    service.import_settings = AsyncMock()

    return service


@pytest.fixture
def mock_settings_repository():
    """Mock SettingsRepository for integration tests"""
    repo = AsyncMock(spec=SettingsRepository)

    # Configure common mock responses
    repo.get_settings = AsyncMock()
    repo.save_settings = AsyncMock()
    repo.get_settings_history = AsyncMock()
    repo.reset_to_defaults = AsyncMock()

    return repo


@pytest.fixture
def sample_settings_data():
    """Sample settings data for integration tests"""
    return {
        "vk_api": {
            "api_version": "5.199",
            "access_token": "test_token",
            "rate_limit": 3,
            "timeout": 30,
        },
        "parser": {
            "max_posts_per_group": 100,
            "max_comments_per_post": 50,
            "batch_size": 10,
            "delay_between_requests": 1.0,
        },
        "storage": {
            "database_url": "sqlite:///test.db",
            "max_connections": 10,
            "connection_timeout": 30,
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file_path": "/var/log/app.log",
        },
    }


@pytest.fixture
def settings_config():
    """SettingsConfig for integration tests"""
    config = SettingsConfig(
        vk_api_token="test_token",
        vk_api_version="5.199",
        database_url="sqlite:///test.db",
        log_level="INFO",
        max_posts_per_group=100,
        max_comments_per_post=50,
    )
    return config
