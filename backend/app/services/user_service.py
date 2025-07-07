"""
Сервис для работы с моделью User.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.hashing import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """Сервис для работы с пользователями."""

    def __init__(self):
        super().__init__(User)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Создание нового пользователя с хешированием пароля."""
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Получение пользователя по email."""
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[User]:
        """Получение пользователя по id."""
        return await super().get(db, id=id)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Аутентификация пользователя."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_service = UserService()
