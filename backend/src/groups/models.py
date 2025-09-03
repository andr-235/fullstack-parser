"""
SQLAlchemy модели для модуля Groups

Определяет репозиторий и специфические модели для работы с группами VK
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import (
    select,
    and_,
    or_,
    desc,
    func,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Group as BaseGroup
from ..database import get_db_session
from ..exceptions import GroupNotFoundError


class GroupRepository:
    """
    Репозиторий для работы с группами VK

    Предоставляет интерфейс для CRUD операций с группами
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, group_id: int) -> Optional[BaseGroup]:
        """Получить группу по ID"""
        query = select(BaseGroup).where(BaseGroup.id == group_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[BaseGroup]:
        """Получить группу по VK ID"""
        query = select(BaseGroup).where(BaseGroup.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_screen_name(
        self, screen_name: str
    ) -> Optional[BaseGroup]:
        """Получить группу по screen_name"""
        query = select(BaseGroup).where(BaseGroup.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[BaseGroup]:
        """Получить все группы с фильтрацией"""
        query = select(BaseGroup)

        # Фильтр по активности
        if is_active is not None:
            query = query.where(BaseGroup.is_active == is_active)

        # Фильтр по поиску
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    BaseGroup.name.ilike(search_filter),
                    BaseGroup.screen_name.ilike(search_filter),
                    BaseGroup.description.ilike(search_filter),
                )
            )

        query = (
            query.order_by(desc(BaseGroup.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, group_data: Dict[str, Any]) -> BaseGroup:
        """Создать новую группу"""
        group = BaseGroup(**group_data)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update(
        self, group_id: int, update_data: Dict[str, Any]
    ) -> BaseGroup:
        """Обновить группу"""
        group = await self.get_by_id(group_id)
        if not group:
            raise GroupNotFoundError(group_id)

        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)

        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete(self, group_id: int) -> bool:
        """Удалить группу"""
        group = await self.get_by_id(group_id)
        if not group:
            return False

        await self.db.delete(group)
        await self.db.commit()
        return True

    async def activate(self, group_id: int) -> bool:
        """Активировать группу"""
        return await self._update_status(group_id, True)

    async def deactivate(self, group_id: int) -> bool:
        """Деактивировать группу"""
        return await self._update_status(group_id, False)

    async def _update_status(self, group_id: int, is_active: bool) -> bool:
        """Обновить статус группы"""
        try:
            await self.update(group_id, {"is_active": is_active})
            return True
        except GroupNotFoundError:
            return False

    async def count(
        self, is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> int:
        """Подсчитать количество групп"""
        query = select(func.count()).select_from(BaseGroup)

        # Фильтр по активности
        if is_active is not None:
            query = query.where(BaseGroup.is_active == is_active)

        # Фильтр по поиску
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    BaseGroup.name.ilike(search_filter),
                    BaseGroup.screen_name.ilike(search_filter),
                    BaseGroup.description.ilike(search_filter),
                )
            )

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_stats(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику группы"""
        group = await self.get_by_id(group_id)
        if not group:
            return None

        # Получаем статистику комментариев для группы
        from sqlalchemy import select as sa_select
        from ..models import Comment

        comments_query = (
            sa_select(
                func.count(Comment.id).label("total_comments"),
                func.avg(Comment.likes_count).label("avg_likes"),
            )
            .select_from(Comment)
            .where(Comment.group_id == group.vk_id)
        )

        result = await self.db.execute(comments_query)
        stats = result.first()

        return {
            "id": group.id,
            "vk_id": group.vk_id,
            "name": group.name,
            "total_comments": stats.total_comments or 0,
            "avg_likes_per_comment": round(stats.avg_likes or 0, 2),
            "members_count": group.members_count or 0,
            "last_parsed_at": group.last_parsed_at,
        }

    async def get_overall_stats(self) -> Dict[str, Any]:
        """Получить общую статистику по всем группам"""
        # Статистика по группам
        groups_query = select(
            func.count(BaseGroup.id).label("total_groups"),
            func.sum(BaseGroup.members_count).label("total_members"),
            func.count()
            .filter(BaseGroup.is_active == True)
            .label("active_groups"),
        ).select_from(BaseGroup)

        groups_result = await self.db.execute(groups_query)
        groups_stats = groups_result.first()

        # Статистика по комментариям
        from ..models import Comment

        comments_query = select(
            func.count(Comment.id).label("total_comments"),
            func.count()
            .filter(Comment.likes_count > 0)
            .label("comments_with_likes"),
        ).select_from(Comment)

        comments_result = await self.db.execute(comments_query)
        comments_stats = comments_result.first()

        return {
            "total_groups": groups_stats.total_groups or 0,
            "active_groups": groups_stats.active_groups or 0,
            "total_members": groups_stats.total_members or 0,
            "total_comments": comments_stats.total_comments or 0,
            "comments_with_likes": comments_stats.comments_with_likes or 0,
        }

    async def bulk_update(
        self, group_ids: List[int], update_data: Dict[str, Any]
    ) -> int:
        """Массовое обновление групп"""
        from sqlalchemy import update
        from datetime import datetime

        # Добавляем время обновления
        update_data["updated_at"] = datetime.utcnow()

        query = (
            update(BaseGroup)
            .where(BaseGroup.id.in_(group_ids))
            .values(**update_data)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount


# Функции для создания репозитория
async def get_group_repository(
    db: AsyncSession = get_db_session,
) -> GroupRepository:
    """Создать репозиторий групп"""
    return GroupRepository(db)


# Экспорт
__all__ = [
    "GroupRepository",
    "get_group_repository",
]
