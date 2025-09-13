"""
Зависимости для модуля Groups
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.database.session import get_db_session
from .service import GroupService


def get_group_service(db: AsyncSession = Depends(get_db_session)) -> GroupService:
    """Получить сервис групп"""
    return GroupService(db)


__all__ = ["get_group_service"]
