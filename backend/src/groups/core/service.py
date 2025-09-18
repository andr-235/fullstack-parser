"""
Сервис для работы с группами VK.

Предоставляет бизнес-логику для управления группами VK,
включая CRUD операции, валидацию, пагинацию и аналитику.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .exceptions import GroupAlreadyExistsError, GroupNotFoundError, GroupValidationError
from .models import Group
from .repository import GroupRepository


# Константы
DEFAULT_GROUPS_LIMIT = 50
MAX_GROWTH_DAYS = 365


class GroupService:
    """Сервис для работы с группами VK.

    Предоставляет высокоуровневый интерфейс для операций с группами,
    включая CRUD, валидацию данных, массовые операции и аналитику.
    Использует GroupRepository для абстракции доступа к данным.
    """

    def __init__(self, db):
        """Инициализация сервиса с репозиторием.

        Args:
            db: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.repository = GroupRepository(db)

    async def get_group(self, group_id: int) -> Group:
        """Получить группу по ID.

        Args:
            group_id: Уникальный идентификатор группы в базе данных.

        Returns:
            Объект группы.

        Raises:
            NotFoundError: Если группа с указанным ID не найдена.
        """
        group = await self.repository.get_by_id(group_id)
        if not group:
            raise GroupNotFoundError(f"Группа с ID {group_id} не найдена")
        return group

    async def get_groups(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_GROUPS_LIMIT,
        offset: int = 0,
    ) -> List[Group]:
        """Получить список групп с фильтрацией и пагинацией.

        Args:
            is_active: Фильтр по активности группы. None - все группы.
            search: Поисковый запрос для имени, screen_name или описания.
            limit: Максимальное количество возвращаемых групп.
            offset: Смещение для пагинации.

        Returns:
            Список объектов групп, отсортированных по дате создания (новые сначала).
        """
        return await self.repository.get_groups(
            is_active=is_active, search=search, limit=limit, offset=offset
        )

    async def create_group(self, group_data: dict) -> Group:
        """Создать новую группу.

        Args:
            group_data: Данные для создания группы.

        Returns:
            Созданный объект группы.

        Raises:
            ValidationError: Если обязательные поля отсутствуют или данные некорректны.
        """
        # Валидация обязательных полей
        required_fields = ["vk_id", "screen_name", "name"]
        for field in required_fields:
            if field not in group_data or not group_data[field]:
                raise ValidationError(f"Обязательное поле '{field}' не заполнено")

        # Проверка уникальности VK ID
        existing = await self.repository.get_by_vk_id(group_data["vk_id"])
        if existing:
            raise ValidationError("Группа с таким VK ID уже существует")

        # Проверка уникальности screen_name
        existing_screen = await self.repository.get_by_screen_name(group_data["screen_name"])
        if existing_screen:
            raise ValidationError("Группа с таким screen_name уже существует")

        return await self.repository.create(group_data)

    async def update_group(self, group_id: int, update_data: dict) -> Group:
        """Обновить группу.

        Args:
            group_id: ID группы для обновления.
            update_data: Данные для обновления.

        Returns:
            Обновленный объект группы.

        Raises:
            NotFoundError: Если группа не найдена.
            ValidationError: Если данные некорректны.
        """
        group = await self.get_group(group_id)

        # Проверка уникальности screen_name при обновлении
        if "screen_name" in update_data:
            existing = await self.repository.get_by_screen_name(update_data["screen_name"])
            if existing and existing.id != group_id:
                raise ValidationError("Группа с таким screen_name уже существует")

        return await self.repository.update(group, update_data)

    async def delete_group(self, group_id: int) -> bool:
        """Удалить группу.

        Args:
            group_id: ID группы для удаления.

        Returns:
            True при успешном удалении.

        Raises:
            NotFoundError: Если группа не найдена.
        """
        group = await self.get_group(group_id)
        await self.repository.delete(group)
        return True

    async def activate_group(self, group_id: int) -> Group:
        """Активировать группу.

        Args:
            group_id: ID группы для активации.

        Returns:
            Активированная группа.

        Raises:
            NotFoundError: Если группа не найдена.
        """
        return await self.update_group(group_id, {"is_active": True})

    async def deactivate_group(self, group_id: int) -> Group:
        """Деактивировать группу.

        Args:
            group_id: ID группы для деактивации.

        Returns:
            Деактивированная группа.

        Raises:
            NotFoundError: Если группа не найдена.
        """
        return await self.update_group(group_id, {"is_active": False})

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Получить группу по VK ID.

        Args:
            vk_id: ID группы в VK.

        Returns:
            Объект группы или None, если не найдена.
        """
        return await self.repository.get_by_vk_id(vk_id)

    async def get_group_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Получить группу по screen_name.

        Args:
            screen_name: Короткое имя группы.

        Returns:
            Объект группы или None, если не найдена.
        """
        return await self.repository.get_by_screen_name(screen_name)

    async def bulk_activate(self, group_ids: List[int]) -> dict:
        """Массовое включение групп.

        Args:
            group_ids: Список ID групп для активации.

        Returns:
            Словарь с результатами операции.
        """
        success_count = await self.repository.bulk_update_active_status(group_ids, True)
        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
        }

    async def bulk_deactivate(self, group_ids: List[int]) -> dict:
        """Массовое отключение групп.

        Args:
            group_ids: Список ID групп для деактивации.

        Returns:
            Словарь с результатами операции.
        """
        success_count = await self.repository.bulk_update_active_status(group_ids, False)
        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
        }

    async def count_groups(
        self, is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> int:
        """Подсчитать количество групп с фильтрами.

        Args:
            is_active: Фильтр по активности группы. None - все группы.
            search: Поисковый запрос для имени, screen_name или описания.

        Returns:
            Количество групп, соответствующих фильтрам.
        """
        return await self.repository.count_groups(is_active=is_active, search=search)

    async def get_active_groups_count(self) -> int:
        """Получить количество активных групп.

        Returns:
            Количество активных групп.
        """
        return await self.repository.get_active_groups_count()

    async def get_groups_count_by_period(self, days: int = 30) -> int:
        """Получить количество групп за период.

        Args:
            days: Количество дней для анализа.

        Returns:
            Количество групп, созданных за указанный период.
        """
        return await self.repository.get_groups_count_by_period(days)

    async def get_groups_growth_percentage(self, days: int = 30) -> float:
        """Получить процент роста групп за период.

        Args:
            days: Количество дней для анализа роста (максимум 365 дней).

        Returns:
            Процент роста групп за указанный период.

        Raises:
            ValidationError: Если days превышает максимальное значение.
        """
        if days > MAX_GROWTH_DAYS:
            raise ValidationError(f"Количество дней не может превышать {MAX_GROWTH_DAYS}")

        current_period = await self.get_groups_count_by_period(days)
        # Предыдущий период: от days до days*2 дней назад
        previous_period_start = datetime.utcnow() - timedelta(days=days * 2)
        previous_period_end = datetime.utcnow() - timedelta(days=days)
        previous_period_query = await self.repository.get_groups_count_by_period_custom(
            previous_period_start, previous_period_end
        )

        if previous_period_query == 0:
            return 100.0 if current_period > 0 else 0.0

        return ((current_period - previous_period_query) / previous_period_query) * 100


__all__ = ["GroupService"]
