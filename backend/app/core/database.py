"""
Database configuration для VK Comments Parser
"""

from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Единая конвенция для именования индексов и ключей
# https://alembic.sqlalchemy.org/en/latest/naming.html
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


# Base class для моделей
class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    metadata = metadata


# Глобальный асинхронный движок SQLAlchemy с оптимизированным connection pooling
@lru_cache(maxsize=1)
def get_async_engine():
    """Получение асинхронного движка с кешированием."""
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "server_settings": {"application_name": "vk_parser_backend"}
        },
    )


async_engine = get_async_engine()

# Фабрика асинхронных сессий с оптимизацией
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_async_session() -> AsyncSession:
    """Получение асинхронной сессии для ARQ задач."""
    return AsyncSessionLocal()


async def init_db() -> None:
    """Инициализация базы данных с оптимизацией и
    повторными попытками подключения.
    """
    import asyncio
    import logging

    max_retries = 10
    delay = 2  # секунд между попытками
    for attempt in range(1, max_retries + 1):
        try:
            # Проверяем подключение без создания таблиц
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            # Проверяем подключение к базе данных
            # Таблицы создаются через миграции Alembic
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            break  # успех, выходим из цикла
        except Exception as e:
            logging.warning(
                f"Database initialization attempt {attempt} failed: {e}"
            )
            if attempt == max_retries:
                logging.error(
                    "Max retries reached. Could not connect to the database."
                )
                break
            await asyncio.sleep(delay)


# Updated $(date)
# Updated Чт 24 июл 2025 10:31:33 +10
