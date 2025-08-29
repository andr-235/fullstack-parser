"""
GroupManager - сервис для управления VK группами

Принципы SOLID:
- Single Responsibility: только управление группами (CRUD)
- Open/Closed: легко добавлять новые методы управления
- Liskov Substitution: можно заменить на другую реализацию
- Interface Segregation: чистый интерфейс для управления группами
- Dependency Inversion: зависит от абстракций (AsyncSession)
"""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vk_group import VKGroup
from app.schemas.vk_group import VKGroupCreate, VKGroupUpdate, VKGroupRead
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class GroupManager(BaseService[VKGroup, VKGroupCreate, VKGroupUpdate]):
    """
    Сервис для управления VK группами.

    Предоставляет высокоуровневый интерфейс для:
    - Создания и обновления групп
    - Поиска групп по различным критериям
    - Получения групп с пагинацией
    - Удаления групп
    """

    def __init__(self):
        """
        Инициализация менеджера групп.
        """
        super().__init__(VKGroup)
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[VKGroup]:
        """
        Получить группу по ее ID.

        Args:
            db: Сессия базы данных
            id: ID группы

        Returns:
            Объект группы или None
        """
        try:
            return await self.get(db, id)
        except Exception as e:
            logger.error(f"Error getting group by ID {id}: {e}")
            return None

    async def get_by_screen_name(
        self, db: AsyncSession, screen_name: str
    ) -> Optional[VKGroup]:
        """
        Получить группу по ее короткому имени.

        Args:
            db: Сессия базы данных
            screen_name: Короткое имя группы

        Returns:
            Объект группы или None
        """
        try:
            result = await db.execute(
                select(self.model).where(self.model.screen_name == screen_name)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"Error getting group by screen_name {screen_name}: {e}"
            )
            return None

    async def get_by_vk_id(
        self, db: AsyncSession, vk_id: int
    ) -> Optional[VKGroup]:
        """
        Получить группу по ее VK ID.

        Args:
            db: Сессия базы данных
            vk_id: VK ID группы

        Returns:
            Объект группы или None
        """
        try:
            result = await db.execute(
                select(self.model).where(self.model.vk_id == vk_id)
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting group by VK ID {vk_id}: {e}")
            return None

    async def get_active_groups(
        self, db: AsyncSession, limit: int = 100, offset: int = 0
    ) -> List[VKGroup]:
        """
        Получить список активных групп.

        Args:
            db: Сессия базы данных
            limit: Максимальное количество групп
            offset: Смещение для пагинации

        Returns:
            Список активных групп
        """
        try:
            query = select(self.model).where(self.model.is_active == True)
            result = await db.execute(query.limit(limit).offset(offset))
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting active groups: {e}")
            return []

    async def get_groups_count(
        self, db: AsyncSession, active_only: bool = True
    ) -> int:
        """
        Получить количество групп.

        Args:
            db: Сессия базы данных
            active_only: Только активные группы

        Returns:
            Количество групп
        """
        try:
            from sqlalchemy import func

            query = select(func.count()).select_from(self.model)
            if active_only:
                query = query.where(self.model.is_active == True)

            result = await db.execute(query)
            return result.scalar()

        except Exception as e:
            logger.error(f"Error counting groups: {e}")
            return 0

    async def create_group(
        self, db: AsyncSession, group_data: VKGroupCreate
    ) -> VKGroup:
        """
        Создать новую группу.

        Args:
            db: Сессия базы данных
            group_data: Данные для создания группы

        Returns:
            Созданная группа

        Raises:
            ValueError: Если группа с таким screen_name уже существует
        """
        try:
            # Определяем screen_name для проверки существования
            screen_name = (
                group_data.screen_name or group_data.vk_id_or_screen_name
            )

            # Проверяем существование группы с таким же screen_name
            existing = await self.get_by_screen_name(db, screen_name)
            if existing:
                raise ValueError(
                    f"Group with screen_name '{screen_name}' already exists"
                )

            # Подготавливаем данные для создания VKGroup
            group_dict = group_data.model_dump()

            # Удаляем поле vk_id_or_screen_name, так как VKGroup его не знает
            group_dict.pop("vk_id_or_screen_name", None)

            # Если screen_name не указан, используем vk_id_or_screen_name
            if not group_dict.get("screen_name"):
                # Если это число, то это VK ID, иначе screen_name
                if group_data.vk_id_or_screen_name.isdigit():
                    group_dict["vk_id"] = int(group_data.vk_id_or_screen_name)
                    # Для VK ID нужно будет получить screen_name из VK API
                    # Пока оставим пустым или сгенерируем временный
                    group_dict["screen_name"] = (
                        f"id{group_data.vk_id_or_screen_name}"
                    )
                else:
                    group_dict["screen_name"] = group_data.vk_id_or_screen_name

            # Создаем новую группу
            new_group = self.model(**group_dict)
            db.add(new_group)
            await db.commit()
            await db.refresh(new_group)

            logger.info(
                f"Group created successfully: {new_group.screen_name}",
                group_id=new_group.id,
                vk_id=new_group.vk_id,
            )

            return new_group

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating group: {e}")
            raise

    async def update_group(
        self, db: AsyncSession, group_id: int, update_data: VKGroupUpdate
    ) -> Optional[VKGroup]:
        """
        Обновить группу.

        Args:
            db: Сессия базы данных
            group_id: ID группы в базе данных
            update_data: Данные для обновления

        Returns:
            Обновленная группа или None если не найдена
        """
        try:
            group = await self.get_by_id(db, group_id)
            if not group:
                return None

            # Обновляем только переданные поля
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(group, field, value)

            await db.commit()
            await db.refresh(group)

            logger.info(
                f"Group updated successfully: {group.screen_name}",
                group_id=group.id,
            )

            return group

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating group {group_id}: {e}")
            raise

    async def delete_group(self, db: AsyncSession, group_id: int) -> bool:
        """
        Удалить группу.

        Args:
            db: Сессия базы данных
            group_id: ID группы

        Returns:
            True если группа удалена, False если не найдена
        """
        try:
            group = await self.get_by_id(db, group_id)
            if not group:
                return False

            await db.delete(group)
            await db.commit()

            logger.info(
                f"Group deleted successfully: {group.screen_name}",
                group_id=group.id,
            )

            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting group {group_id}: {e}")
            raise

    async def toggle_group_status(
        self, db: AsyncSession, group_id: int
    ) -> Optional[VKGroup]:
        """
        Переключить статус активности группы.

        Args:
            db: Сессия базы данных
            group_id: ID группы

        Returns:
            Обновленная группа или None если не найдена
        """
        try:
            group = await self.get_by_id(db, group_id)
            if not group:
                return None

            # Переключаем статус
            group.is_active = not group.is_active
            await db.commit()
            await db.refresh(group)

            logger.info(
                f"Group status toggled: {group.screen_name} -> {group.is_active}",
                group_id=group.id,
            )

            return group

        except Exception as e:
            await db.rollback()
            logger.error(f"Error toggling group status {group_id}: {e}")
            raise

    async def search_groups(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20,
        offset: int = 0,
        active_only: bool = True,
    ) -> List[VKGroup]:
        """
        Поиск групп по имени или screen_name.

        Args:
            db: Сессия базы данных
            query: Поисковый запрос
            limit: Максимальное количество результатов
            offset: Смещение для пагинации
            active_only: Только активные группы

        Returns:
            Список найденных групп
        """
        try:
            from sqlalchemy import or_, func

            search_query = f"%{query}%"
            sql_query = select(self.model).where(
                or_(
                    self.model.name.ilike(search_query),
                    self.model.screen_name.ilike(search_query),
                )
            )

            if active_only:
                sql_query = sql_query.where(self.model.is_active == True)

            result = await db.execute(sql_query.limit(limit).offset(offset))

            groups = result.scalars().all()
            logger.info(f"Found {len(groups)} groups for query '{query}'")

            return groups

        except Exception as e:
            logger.error(f"Error searching groups with query '{query}': {e}")
            return []
