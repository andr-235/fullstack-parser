"""
Тесты для конфигурации приложения
"""

import pytest
from app.core.config import Settings


class TestSettings:
    """Базовые тесты настроек"""

    def test_settings_initialization(self):
        """Тест инициализации настроек"""
        settings = Settings()
        assert settings.app_name == "VK Comments Parser"
        assert settings.api_v1_str == "/api/v1"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_database_settings_exist(self):
        """Тест наличия настроек базы данных"""
        settings = Settings()
        assert hasattr(settings, "database")
        assert hasattr(settings.database, "url")
        assert str(settings.database.url).startswith("postgresql+asyncpg://")

    def test_vk_settings_exist(self):
        """Тест наличия настроек VK"""
        settings = Settings()
        assert hasattr(settings, "vk")
        assert hasattr(settings.vk, "access_token")
        assert hasattr(settings.vk, "api_version")
        assert hasattr(settings.vk, "requests_per_second")

    def test_cors_origins_exist(self):
        """Тест наличия CORS origins"""
        settings = Settings()
        assert hasattr(settings, "cors_origins")
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
