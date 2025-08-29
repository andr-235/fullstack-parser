"""
Repository для работы с группами (DDD Infrastructure Layer)

Интерфейс и реализация репозитория для VK групп
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.group import Group, GroupContent, GroupStats


class GroupRepositoryInterface(ABC):
    """Интерфейс репозитория для групп"""

    @abstractmethod
    async def save(self, group: Group) -> Group:
        """Сохранить группу"""
        pass

    @abstractmethod
    async def find_by_id(self, group_id: int) -> Optional[Group]:
        """Найти группу по ID"""
        pass

    @abstractmethod
    async def find_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Найти группу по VK ID"""
        pass

    @abstractmethod
    async def find_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Найти группу по screen_name"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Group]:
        """Найти все группы"""
        pass

    @abstractmethod
    async def find_active_groups(self) -> List[Group]:
        """Найти активные группы"""
        pass

    @abstractmethod
    async def delete(self, group_id: int) -> bool:
        """Удалить группу"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Подсчитать количество групп"""
        pass


class GroupRepository(GroupRepositoryInterface):
    """Реализация репозитория для групп с SQLAlchemy"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, group: Group) -> Group:
        """Сохранить группу"""
        from ..models.group import VKGroupModel

        if group.id is None:
            # Создаем новую группу
            model = VKGroupModel.from_domain_dict(group.get_display_info())
            self.db.add(model)
            await self.db.commit()
            await self.db.refresh(model)

            # Обновляем ID в доменной сущности
            group.id = model.id
        else:
            # Обновляем существующую группу
            query = select(VKGroupModel).where(VKGroupModel.id == group.id)
            result = await self.db.execute(query)
            model = result.scalar_one_or_none()

            if model:
                model.update_from_domain_dict(group.get_display_info())
                await self.db.commit()

        return group

    async def find_by_id(self, group_id: int) -> Optional[Group]:
        """Найти группу по ID"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel).where(VKGroupModel.id == group_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Преобразуем в доменную сущность
        data = model.to_domain_dict()

        content = GroupContent(
            vk_id=data["vk_id"],
            screen_name=data["screen_name"],
            name=data["name"],
            description=data["description"],
            members_count=data["members_count"],
            photo_url=data["photo_url"],
            is_closed=data["is_closed"],
        )

        stats = GroupStats(
            total_posts_parsed=data["total_posts_parsed"],
            total_comments_found=data["total_comments_found"],
            last_parsed_at=data["last_parsed_at"],
        )

        return Group(
            id=data["id"],
            content=content,
            stats=stats,
            is_active=data["is_active"],
            max_posts_to_check=data["max_posts_to_check"],
        )

    async def find_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Найти группу по VK ID"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel).where(VKGroupModel.vk_id == vk_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return await self._model_to_domain_entity(model)

    async def find_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Найти группу по screen_name"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel).where(
            VKGroupModel.screen_name == screen_name
        )
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return await self._model_to_domain_entity(model)

    async def find_all(self) -> List[Group]:
        """Найти все группы"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel)
        result = await self.db.execute(query)
        models = result.scalars().all()

        groups = []
        for model in models:
            group = await self._model_to_domain_entity(model)
            if group:
                groups.append(group)

        return groups

    async def find_active_groups(self) -> List[Group]:
        """Найти активные группы"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel).where(VKGroupModel.is_active == True)
        result = await self.db.execute(query)
        models = result.scalars().all()

        groups = []
        for model in models:
            group = await self._model_to_domain_entity(model)
            if group:
                groups.append(group)

        return groups

    async def delete(self, group_id: int) -> bool:
        """Удалить группу"""
        from ..models.group import VKGroupModel

        query = select(VKGroupModel).where(VKGroupModel.id == group_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.db.delete(model)
        await self.db.commit()
        return True

    async def count(self) -> int:
        """Подсчитать количество групп"""
        from ..models.group import VKGroupModel
        from sqlalchemy import func

        query = select(func.count(VKGroupModel.id))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def _model_to_domain_entity(self, model) -> Optional[Group]:
        """Преобразовать SQLAlchemy модель в доменную сущность"""
        try:
            data = model.to_domain_dict()

            content = GroupContent(
                vk_id=data["vk_id"],
                screen_name=data["screen_name"],
                name=data["name"],
                description=data["description"],
                members_count=data["members_count"],
                photo_url=data["photo_url"],
                is_closed=data["is_closed"],
            )

            stats = GroupStats(
                total_posts_parsed=data["total_posts_parsed"],
                total_comments_found=data["total_comments_found"],
                last_parsed_at=data["last_parsed_at"],
            )

            return Group(
                id=data["id"],
                content=content,
                stats=stats,
                is_active=data["is_active"],
                max_posts_to_check=data["max_posts_to_check"],
            )

        except Exception as e:
            print(f"Error converting model to domain entity: {e}")
            return None
