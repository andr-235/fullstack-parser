"""
Общие фикстуры для всех тестов

Содержит общие настройки, фикстуры и утилиты для тестирования
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.shared.config import settings
from src.shared.infrastructure.database.session import DatabaseSession


# Настройка тестовой базы данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_vk_parser"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Тестовый движок базы данных"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Создаем тестовую схему
    async with engine.begin() as conn:
        # Здесь можно добавить создание тестовых таблиц
        pass
    
    yield engine
    
    # Очищаем после тестов
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Тестовая сессия базы данных"""
    async_session = sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_client() -> TestClient:
    """Тестовый клиент FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Мок Redis для тестов"""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.keys.return_value = []
    return mock_redis


@pytest.fixture
def mock_celery():
    """Мок Celery для тестов"""
    mock_celery = AsyncMock()
    mock_celery.send_task.return_value = Mock(id="test-task-id")
    return mock_celery


@pytest.fixture
def mock_vk_api():
    """Мок VK API для тестов"""
    mock_vk = Mock()
    mock_vk.wall.get.return_value = {
        "items": [
            {
                "id": 1,
                "text": "Test post",
                "comments": {"count": 5}
            }
        ]
    }
    return mock_vk


@pytest.fixture
def auth_headers():
    """Заголовки аутентификации для тестов"""
    return {
        "Authorization": "Bearer test-token"
    }


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_superuser": False
    }


# Фикстуры для модуля auth
@pytest.fixture
def mock_user_repository():
    """Мок репозитория пользователей"""
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = False
    mock_repo.get_paginated.return_value = ([], 0)
    mock_repo.get_stats.return_value = {
        "total": 0,
        "active": 0,
        "inactive": 0,
        "locked": 0,
        "pending_verification": 0,
        "superusers": 0
    }
    return mock_repo


@pytest.fixture
def mock_password_service():
    """Мок сервиса паролей"""
    mock_service = AsyncMock()
    mock_service.hash_password.return_value = "hashed_password"
    mock_service.verify_password.return_value = True
    return mock_service


@pytest.fixture
def mock_jwt_service():
    """Мок JWT сервиса"""
    mock_service = AsyncMock()
    mock_service.create_access_token.return_value = "access_token"
    mock_service.create_refresh_token.return_value = "refresh_token"
    mock_service.validate_token.return_value = {"sub": "1", "email": "test@example.com"}
    mock_service.decode_token.return_value = {"sub": "1", "email": "test@example.com"}
    return mock_service


# Утилиты для тестов
class TestDataFactory:
    """Фабрика тестовых данных"""
    
    @staticmethod
    def create_user_data(**kwargs):
        """Создать тестовые данные пользователя"""
        default_data = {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "is_superuser": False,
            "status": "active",
            "email_verified": True
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_post_data(**kwargs):
        """Создать тестовые данные поста"""
        default_data = {
            "id": 1,
            "text": "Test post",
            "likes": {"count": 10},
            "comments": {"count": 5},
            "reposts": {"count": 2}
        }
        default_data.update(kwargs)
        return default_data


@pytest.fixture
def test_data_factory():
    """Фабрика тестовых данных"""
    return TestDataFactory


# Настройки pytest
def pytest_configure(config):
    """Настройка pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit тесты"
    )
    config.addinivalue_line(
        "markers", "integration: Integration тесты"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end тесты"
    )
    config.addinivalue_line(
        "markers", "slow: Медленные тесты"
    )