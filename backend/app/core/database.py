"""
Database configuration для VK Comments Parser
"""

from functools import lru_cache
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


# Глобальный асинхронный движок SQLAlchemy с оптимизированным connection pooling
@lru_cache(maxsize=1)
def get_async_engine():
    """Получение асинхронного движка с кешированием."""
    return create_async_engine(
        str(settings.database_url),
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"server_settings": {"application_name": "vk_parser_backend"}},
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


async def init_db() -> None:
    """Инициализация базы данных с оптимизацией."""
    try:
        # Проверяем подключение без создания таблиц
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")

        # Создаем таблицы только если их нет (lazy creation)
        async with async_engine.begin() as conn:
            # Проверяем существование хотя бы одной таблицы
            result = await conn.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'vk_groups'
                )
            """
            )
            tables_exist = result.scalar()

            if not tables_exist:
                await conn.run_sync(Base.metadata.create_all)

    except Exception as e:
        # Логируем ошибку, но не падаем
        import logging

        logging.warning(f"Database initialization warning: {e}")
        # Продолжаем работу - таблицы могут быть созданы через миграции
