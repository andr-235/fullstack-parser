"""
База данных и сессии
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def get_database_url() -> str:
    """Получить URL базы данных"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/vk_parser"
    )


def get_engine():
    """Получить движок БД"""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=False,
            pool_pre_ping=True
        )
    return _engine


def get_session_factory():
    """Получить фабрику сессий"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД"""
    async with get_session_factory()() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
