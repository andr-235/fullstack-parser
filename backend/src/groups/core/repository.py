"""
Репозиторий для работы с группами VK.

Предоставляет абстракцию доступа к данным групп,
инкапсулируя логику запросов к базе данных.
"""

from typing import List, Optional

from sqlalchemy import Select, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Group


class GroupRepository:
    """Репозиторий для операций с группами в базе данных.

    Предоставляет высокоуровневый интерфейс для CRUD операций
    с группами, абстрагируя детали работы с SQLAlchemy.
    """

    def __init__(self, db: AsyncSession):
        """Инициализация репозитория с сессией базы данных.

        Args:
            db: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.db = db

    async def get_by_id(self, group_id: int) -> Optional[Group]:
        """Получить группу по ID.

        Args:
            group_id: Уникальный идентификатор группы.

        Returns:
            Объект группы или None, если не найдена.
        """
        query = select(Group).where(Group.id == group_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Получить группу по VK ID.

        Args:
            vk_id: ID группы в VK.

        Returns:
            Объект группы или None, если не найдена.
        """
        query = select(Group).where(Group.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Получить группу по screen_name.

        Args:
            screen_name: Короткое имя группы.

        Returns:
            Объект группы или None, если не найдена.
        """
        query = select(Group).where(Group.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Group]:
        """Получить список групп с фильтрацией и пагинацией.

        Args:
            is_active: Фильтр по активности группы.
            search: Поисковый запрос для имени, screen_name или описания.
            limit: Максимальное количество возвращаемых групп.
            offset: Смещение для пагинации.

        Returns:
            Список объектов групп.
        """
        query = select(Group)

        if is_active is not None:
            query = query.where(Group.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Group.name.ilike(search_filter),
                    Group.screen_name.ilike(search_filter),
                    Group.description.ilike(search_filter),
                )
            )

        query = query.order_by(desc(Group.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, group_data: dict) -> Group:
        """Создать новую группу.

        Args:
            group_data: Данные для создания группы.

        Returns:
            Созданная группа.
        """
        group = Group(**group_data)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update(self, group: Group, update_data: dict) -> Group:
        """Обновить группу.

        Args:
            group: Объект группы для обновления.
            update_data: Данные для обновления.

        Returns:
            Обновленная группа.
        """
        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)

        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete(self, group: Group) -> None:
        """Удалить группу.

        Args:
            group: Объект группы для удаления.
        """
        await self.db.delete(group)
        await self.db.commit()

    async def bulk_update_active_status(
        self, group_ids: List[int], is_active: bool
    ) -> int:
        """Массовое обновление статуса активности групп.

        Args:
            group_ids: Список ID групп.
            is_active: Новый статус активности.

        Returns:
            Количество обновленных групп.
        """
        from datetime import datetime
        update_data = {"is_active": is_active, "updated_at": datetime.utcnow()}
        query = update(Group).where(Group.id.in_(group_ids)).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount