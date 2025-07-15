"""
Тесты для конфигурации приложения
"""

import pytest
from app.core.config import Settings


class TestCORSOriginsParsing:
    """Тесты для парсинга CORS_ORIGINS"""

    def test_json_array_format(self):
        """Тест парсинга JSON-массива"""
        settings = Settings(cors_origins='["http://localhost:3000", "https://example.com"]')
        assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]

    def test_comma_separated_format(self):
        """Тест парсинга строки с запятыми"""
        settings = Settings(cors_origins="http://localhost:3000,https://example.com")
        assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]

    def test_empty_string(self):
        """Тест пустой строки"""
        settings = Settings(cors_origins="")
        assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]

    def test_whitespace_only(self):
        """Тест строки только с пробелами"""
        settings = Settings(cors_origins="   ")
        assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]

    def test_invalid_json(self):
        """Тест невалидного JSON"""
        settings = Settings(cors_origins='["invalid json')
        assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]

    def test_single_origin(self):
        """Тест одного origin"""
        settings = Settings(cors_origins="https://example.com")
        assert settings.cors_origins == ["https://example.com"]

    def test_list_input(self):
        """Тест ввода списка"""
        settings = Settings(cors_origins=["http://localhost:3000", "https://example.com"])
        assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]

    def test_none_input(self):
        """Тест None ввода"""
        settings = Settings(cors_origins=None)
        assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


class TestDatabaseSettings:
    """Тесты для настроек базы данных"""

    def test_default_database_url(self):
        """Тест сборки URL базы данных по умолчанию"""
        settings = Settings()
        expected_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser"
        assert str(settings.database.url) == expected_url

    def test_custom_database_url(self):
        """Тест кастомного URL базы данных"""
        settings = Settings(
            database=Settings.DatabaseSettings(
                user="custom_user",
                password="custom_pass",
                host="custom_host",
                port=5433,
                name="custom_db"
            )
        )
        expected_url = "postgresql+asyncpg://custom_user:custom_pass@custom_host:5433/custom_db"
        assert str(settings.database.url) == expected_url


class TestVKSettings:
    """Тесты для настроек VK API"""

    def test_default_vk_settings(self):
        """Тест настроек VK API по умолчанию"""
        settings = Settings()
        assert settings.vk.access_token == "stub_token"
        assert settings.vk.api_version == "5.131"
        assert settings.vk.requests_per_second == 3

    def test_custom_vk_settings(self):
        """Тест кастомных настроек VK API"""
        settings = Settings(
            vk=Settings.VKSettings(
                access_token="custom_token",
                api_version="5.200",
                requests_per_second=5
            )
        )
        assert settings.vk.access_token == "custom_token"
        assert settings.vk.api_version == "5.200"
        assert settings.vk.requests_per_second == 5 