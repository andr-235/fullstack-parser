"""
Репозиторий пользователей для auth модуля
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user_model import UserModel


class UserRepository:
    """Репозиторий пользователей для аутентификации"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Получить пользователя по email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> UserModel:
        """Создать пользователя"""
        user = UserModel(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: UserModel) -> UserModel:
        """Обновить пользователя"""
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None