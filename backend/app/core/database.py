"""
Database configuration для VK Comments Parser
"""

from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

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


# Async SQLAlchemy engine
async_engine = create_async_engine(settings.database_url, echo=settings.debug)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Инициализация базы данных."""
    async with async_engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
