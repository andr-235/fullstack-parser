"""
Конфигурация для интеграционных тестов

Настраивает:
- Асинхронные фикстуры
- Базу данных для тестов
- HTTP клиент
- Логирование
"""

import asyncio
import logging
import pytest
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db_session
from app.main import app


# Настройка логирования для тестов
logging.basicConfig(
    level=logging.WARNING,  # Уменьшаем уровень логирования для тестов
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Отключаем логи от сторонних библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Создает тестовый engine базы данных"""
    # Используем SQLite для тестов (быстрее чем PostgreSQL)
    test_database_url = "sqlite+aiosqlite:///./test.db"

    engine = create_async_engine(
        test_database_url,
        echo=False,  # Отключаем логи SQL запросов
        future=True,
    )

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очищаем после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для сессии базы данных с автоматическим rollback"""
    async_session_factory = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        # Начинаем транзакцию
        async with session.begin():
            try:
                yield session
            finally:
                # Автоматический rollback после каждого теста
                await session.rollback()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для HTTP клиента"""
    async with AsyncClient(
        app=app, base_url="http://testserver", follow_redirects=True
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def authenticated_client(client, db_session):
    """Фикстура для аутентифицированного клиента"""
    # Здесь можно добавить логику аутентификации если понадобится
    # Пока просто возвращаем обычного клиента
    yield client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестового окружения"""
    # Можно добавить дополнительные настройки окружения
    pass


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Конфигурация настроек для тестов"""
    # Отключаем некоторые проверки в тестах
    original_debug = settings.debug
    settings.debug = True

    yield

    # Восстанавливаем настройки
    settings.debug = original_debug


# Маркеры для pytest
def pytest_configure(config):
    """Конфигурация pytest маркеров"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Плагины pytest-asyncio
pytest_plugins = ["pytest_asyncio"]
