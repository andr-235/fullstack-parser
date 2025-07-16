import os
from unittest.mock import AsyncMock, patch

import pytest
from dotenv import load_dotenv

# Загружаем переменные из .env перед импортом приложения
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


# Мокаем базу данных и Redis для всех тестов
@pytest.fixture(autouse=True)
def mock_database():
    """Мокаем базу данных для всех тестов"""
    with patch("app.core.database.async_engine"):
        with patch("app.core.database.AsyncSessionLocal") as mock_session:
            # Создаем мок сессии
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = (
                mock_session_instance
            )
            mock_session.return_value.__aexit__.return_value = None

            yield mock_session_instance


@pytest.fixture(autouse=True)
def mock_redis():
    """Мокаем Redis для всех тестов"""
    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.close.return_value = None
        mock_redis.return_value = mock_redis_instance

        yield mock_redis_instance


@pytest.fixture(autouse=True)
def mock_settings():
    """Мокаем настройки для тестов"""
    with patch("app.core.config.settings") as mock_settings:
        # Устанавливаем тестовые значения
        mock_settings.debug = True
        mock_settings.database.url = (
            "postgresql+asyncpg://test:test@localhost/test"
        )
        mock_settings.redis_url = "redis://localhost:6379/0"
        mock_settings.vk.access_token = "test_token"
        mock_settings.vk.api_version = "5.131"
        mock_settings.get_cors_origins.return_value = ["http://localhost:3000"]

        yield mock_settings
