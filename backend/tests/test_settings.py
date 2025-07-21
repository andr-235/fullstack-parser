"""
Тесты для системы настроек
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1.settings import (
    ApplicationSettings,
    DatabaseSettings,
    LoggingSettings,
    MonitoringSettings,
    UISettings,
    VKAPISettings,
)
from app.main import app
from app.services.settings_service import SettingsService

client = TestClient(app)


class TestSettingsAPI:
    """Тесты API настроек"""

    @patch("app.services.settings_service.get_settings_service")
    def test_get_settings(self, mock_get_service):
        """Тест получения настроек"""
        # Подготавливаем мок
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        expected_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="test_token",
                api_version="5.131",
                requests_per_second=3,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        mock_service.get_current_settings.return_value = expected_settings

        # Выполняем запрос
        response = client.get("/api/v1/settings/")

        # Проверяем результат
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Настройки успешно загружены"
        assert data["settings"]["vk_api"]["access_token"] == "test_token"
        assert data["settings"]["vk_api"]["api_version"] == "5.131"

    @patch("app.services.settings_service.get_settings_service")
    def test_update_settings(self, mock_get_service):
        """Тест обновления настроек"""
        # Подготавливаем мок
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        updated_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="new_token",
                api_version="5.131",
                requests_per_second=5,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        mock_service.update_settings.return_value = updated_settings

        # Выполняем запрос
        update_data = {
            "vk_api": {
                "access_token": "new_token",
                "api_version": "5.131",
                "requests_per_second": 5,
            }
        }

        response = client.put("/api/v1/settings/", json=update_data)

        # Проверяем результат
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Настройки успешно обновлены"
        assert data["settings"]["vk_api"]["access_token"] == "new_token"
        assert data["settings"]["vk_api"]["requests_per_second"] == 5

    @patch("app.services.settings_service.get_settings_service")
    def test_reset_settings(self, mock_get_service):
        """Тест сброса настроек"""
        # Подготавливаем мок
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        default_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="",
                api_version="5.131",
                requests_per_second=3,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        mock_service.reset_to_defaults.return_value = default_settings

        # Выполняем запрос
        response = client.post("/api/v1/settings/reset")

        # Проверяем результат
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Настройки сброшены к значениям по умолчанию"
        assert data["settings"]["vk_api"]["access_token"] == ""

    @patch("app.services.settings_service.get_settings_service")
    def test_get_settings_health(self, mock_get_service):
        """Тест проверки здоровья настроек"""
        # Подготавливаем мок
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        health_status = {
            "valid": True,
            "database_connected": True,
            "redis_connected": True,
            "vk_api_accessible": True,
            "last_check": "2024-01-01T12:00:00",
        }

        mock_service.get_health_status.return_value = health_status

        # Выполняем запрос
        response = client.get("/api/v1/settings/health")

        # Проверяем результат
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["settings_valid"] is True
        assert data["database_connected"] is True
        assert data["redis_connected"] is True
        assert data["vk_api_accessible"] is True


class TestSettingsValidation:
    """Тесты валидации настроек"""

    def test_vk_api_settings_validation(self):
        """Тест валидации настроек VK API"""
        # Валидные настройки
        valid_settings = VKAPISettings(
            access_token="valid_token",
            api_version="5.131",
            requests_per_second=3,
        )
        assert valid_settings.access_token == "valid_token"
        assert valid_settings.requests_per_second == 3

        # Невалидные настройки (должны вызвать ошибку)
        with pytest.raises(ValueError):
            VKAPISettings(
                access_token="",  # Пустой токен
                api_version="5.131",
                requests_per_second=3,
            )

    def test_monitoring_settings_validation(self):
        """Тест валидации настроек мониторинга"""
        # Валидные настройки
        valid_settings = MonitoringSettings(
            scheduler_interval_seconds=300,
            max_concurrent_groups=10,
            group_delay_seconds=1,
            auto_start_scheduler=False,
        )
        assert valid_settings.scheduler_interval_seconds == 300
        assert valid_settings.max_concurrent_groups == 10

        # Невалидные настройки (должны вызвать ошибку)
        with pytest.raises(ValueError):
            MonitoringSettings(
                scheduler_interval_seconds=30,  # Слишком мало
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            )


class TestSettingsService:
    """Тесты сервиса настроек"""

    @pytest.mark.asyncio
    async def test_get_current_settings(self):
        """Тест получения текущих настроек"""
        service = SettingsService()

        # Мокаем settings
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.vk.access_token = "test_token"
            mock_settings.vk.api_version = "5.131"
            mock_settings.vk.requests_per_second = 3
            mock_settings.monitoring.scheduler_interval_seconds = 300
            mock_settings.monitoring.max_concurrent_groups = 10
            mock_settings.monitoring.group_delay_seconds = 1
            mock_settings.monitoring.auto_start_scheduler = False
            mock_settings.log_level = "INFO"

            settings = await service.get_current_settings()

            assert settings.vk_api.access_token == "test_token"
            assert settings.vk_api.api_version == "5.131"
            assert settings.monitoring.scheduler_interval_seconds == 300

    @pytest.mark.asyncio
    async def test_validate_settings(self):
        """Тест валидации настроек"""
        service = SettingsService()

        # Валидные настройки
        valid_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="valid_token",
                api_version="5.131",
                requests_per_second=3,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        # Не должно вызывать исключение
        await service._validate_settings(valid_settings)

        # Невалидные настройки
        invalid_settings = ApplicationSettings(
            vk_api=VKAPISettings(
                access_token="",  # Пустой токен
                api_version="5.131",
                requests_per_second=3,
            ),
            monitoring=MonitoringSettings(
                scheduler_interval_seconds=300,
                max_concurrent_groups=10,
                group_delay_seconds=1,
                auto_start_scheduler=False,
            ),
            database=DatabaseSettings(
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            ),
            logging=LoggingSettings(
                level="INFO",
                format="json",
                include_timestamp=True,
            ),
            ui=UISettings(
                theme="system",
                auto_refresh=True,
                refresh_interval=30,
                items_per_page=20,
                show_notifications=True,
            ),
        )

        # Должно вызывать исключение
        with pytest.raises(
            ValueError, match="VK API токен не может быть пустым"
        ):
            await service._validate_settings(invalid_settings)
