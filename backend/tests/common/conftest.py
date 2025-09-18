"""
Общие fixtures для тестов модуля common
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.common.database import Base, DatabaseManager
from backend.src.common.redis_client import RedisClient


@pytest.fixture
def event_loop():
    """Фикстура для event loop в асинхронных тестах"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_redis_client():
    """Мок Redis клиента для тестирования"""
    mock_client = AsyncMock(spec=redis.Redis)
    mock_client.ping.return_value = True
    mock_client.get.return_value = "test_value"
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    mock_client.exists.return_value = 1
    mock_client.expire.return_value = True
    mock_client.hget.return_value = "hash_value"
    mock_client.hset.return_value = True
    mock_client.hgetall.return_value = {"key": "value"}
    mock_client.hdel.return_value = 1
    mock_client.sadd.return_value = 1
    mock_client.smembers.return_value = {"member1", "member2"}
    mock_client.srem.return_value = 1
    mock_client.lpush.return_value = 2
    mock_client.rpush.return_value = 2
    mock_client.lpop.return_value = "item"
    mock_client.rpop.return_value = "item"
    mock_client.llen.return_value = 5
    mock_client.ttl.return_value = 3600
    mock_client.keys.return_value = ["key1", "key2"]
    mock_client.scan.return_value = (0, ["key1", "key2"])
    mock_client.setnx.return_value = True
    return mock_client


@pytest.fixture
async def redis_client_fixture(mock_redis_client):
    """Фикстура Redis клиента с моком"""
    with patch('backend.src.common.redis_client.redis.from_url', return_value=mock_redis_client):
        client = RedisClient()
        yield client
        await client.close()


@pytest.fixture
async def mock_db_session():
    """Мок сессии базы данных"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit.return_value = None
    mock_session.rollback.return_value = None
    mock_session.close.return_value = None
    return mock_session


@pytest.fixture
async def mock_session_factory(mock_db_session):
    """Мок фабрики сессий"""
    mock_factory = AsyncMock()
    mock_factory.return_value = mock_db_session
    return mock_factory


@pytest.fixture
async def mock_engine():
    """Мок движка базы данных"""
    mock_engine = AsyncMock()
    return mock_engine


@pytest.fixture
def mock_env_vars():
    """Фикстура для установки тестовых переменных окружения"""
    original_env = dict(os.environ)

    # Устанавливаем тестовые значения
    os.environ.update({
        "REDIS_URL": "redis://localhost:6379/1",
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
        "CELERY_TASK_ALWAYS_EAGER": "true"
    })

    yield

    # Восстанавливаем оригинальные значения
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
async def test_database_manager(mock_env_vars, mock_engine, mock_session_factory):
    """Фикстура DatabaseManager с моками"""
    # Сбрасываем singleton
    DatabaseManager._instance = None
    DatabaseManager._engine = None
    DatabaseManager._session_factory = None

    with patch('backend.src.common.database.create_async_engine', return_value=mock_engine), \
         patch('backend.src.common.database.async_sessionmaker', return_value=mock_session_factory):

        manager = DatabaseManager()
        yield manager


@pytest.fixture
async def test_redis_client(mock_env_vars, mock_redis_client):
    """Фикстура RedisClient с моками"""
    with patch('backend.src.common.redis_client.redis.from_url', return_value=mock_redis_client):
        client = RedisClient()
        yield client
        await client.close()


@pytest.fixture
def mock_logger():
    """Мок логгера"""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_celery_app():
    """Мок Celery приложения"""
    app = MagicMock()
    app.task = MagicMock()
    app.config_from_object = MagicMock()
    app.autodiscover_tasks = MagicMock()
    return app


@pytest.fixture
def mock_celery_task():
    """Мок Celery задачи"""
    task = MagicMock()
    task.name = "test_task"
    task.request = MagicMock()
    task.request.id = "test_task_id"
    task.request.retries = 0
    task.request.hostname = "test_worker"
    task.request.utcnow.return_value.isoformat.return_value = "2023-01-01T00:00:00"
    return task