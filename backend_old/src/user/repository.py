"""
Репозиторий пользователей
"""

from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User
from .schemas import UserStatus


class UserRepository:
    """Репозиторий пользователей"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: dict) -> User:
        """Создать пользователя"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()  # Flush to get the ID
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        result = await self.session.execute(
            select(func.count(User.id)).where(User.email == email)
        )
        return result.scalar() > 0

    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True

    async def get_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Получить пользователей с пагинацией"""
        query = select(User)

        # Фильтры
        conditions = []
        if status:
            conditions.append(User.status == status.value)
        if search:
            conditions.append(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Подсчет общего количества
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Получение данных с пагинацией
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def get_stats(self) -> Dict[str, int]:
        """Получить статистику пользователей"""
        # Общее количество
        total_result = await self.session.execute(select(func.count(User.id)))
        total = total_result.scalar()

        # По статусам
        status_result = await self.session.execute(
            select(User.status, func.count(User.id))
            .group_by(User.status)
        )
        status_counts = dict(status_result.fetchall())

        # Суперпользователи
        superuser_result = await self.session.execute(
            select(func.count(User.id)).where(User.is_superuser == True)
        )
        superusers = superuser_result.scalar()

        return {
            "total": total,
            "active": status_counts.get("active", 0),
            "inactive": status_counts.get("inactive", 0),
            "locked": status_counts.get("locked", 0),
            "pending_verification": status_counts.get("pending_verification", 0),
            "superusers": superusers
        }
