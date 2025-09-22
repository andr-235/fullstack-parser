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
    """Базовый класс для всех моделей базы данных
    
    Наследуется от DeclarativeBase SQLAlchemy и предоставляет
    общую функциональность для всех моделей в приложении.
    """
    pass


class DatabaseManager:
    """Менеджер базы данных с паттерном singleton"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_engine(self):
        """Получить движок БД"""
        if self._engine is None:
            self._engine = create_async_engine(
                get_database_url(),
                echo=False,
                pool_pre_ping=True
            )
        return self._engine

    def get_session_factory(self):
        """Получить фабрику сессий"""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_factory


def get_database_url() -> str:
    """Получить URL базы данных"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user@localhost:5432/vk_parser"
    )


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


def get_engine():
    """Получить движок БД"""
    return db_manager.get_engine()


def get_session_factory():
    """Получить фабрику сессий"""
    return db_manager.get_session_factory()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД"""
    async with get_session_factory()() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_async_session():
    """Получить сессию БД как контекстный менеджер"""
    return get_session_factory()()
