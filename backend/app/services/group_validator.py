"""
GroupValidator - сервис для валидации VK групп через API

Принципы SOLID:
- Single Responsibility: только валидация групп через VK API
- Open/Closed: легко добавлять новые проверки
- Liskov Substitution: можно заменить на другую реализацию валидации
- Interface Segregation: чистый интерфейс для валидации
- Dependency Inversion: зависит от VKAPIService
"""

import logging
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vk_group import VKGroup
from app.services.vk_api_service import VKAPIService

logger = logging.getLogger(__name__)


class GroupValidator:
    """
    Сервис для валидации VK групп через VK API.

    Предоставляет высокоуровневый интерфейс для:
    - Проверки существования групп в VK
    - Получения актуальных данных о группах
    - Валидации screen_name и VK ID
    - Обновления данных групп из VK API
    """

    def __init__(self, vk_service: VKAPIService):
        """
        Инициализация валидатора групп.

        Args:
            vk_service: Сервис для работы с VK API
        """
        self.vk_service = vk_service
        self.logger = logging.getLogger(__name__)

    async def validate_screen_name(self, screen_name: str) -> bool:
        """
        Проверить существование группы по screen_name.

        Args:
            screen_name: Короткое имя группы

        Returns:
            True если группа существует, False иначе
        """
        try:
            group_data = await self.vk_service.get_group_info(screen_name)
            exists = group_data is not None

            logger.info(f"Screen name validation: {screen_name} -> {exists}")
            return exists

        except Exception as e:
            logger.error(f"Error validating screen_name {screen_name}: {e}")
            return False

    async def validate_vk_id(self, vk_id: int) -> bool:
        """
        Проверить существование группы по VK ID.

        Args:
            vk_id: VK ID группы

        Returns:
            True если группа существует, False иначе
        """
        try:
            group_data = await self.vk_service.get_group_info(str(vk_id))
            exists = group_data is not None

            logger.info(f"VK ID validation: {vk_id} -> {exists}")
            return exists

        except Exception as e:
            logger.error(f"Error validating VK ID {vk_id}: {e}")
            return False

    async def get_group_data_from_vk(self, identifier: str) -> Optional[Dict]:
        """
        Получить данные группы из VK API.

        Args:
            identifier: screen_name или VK ID группы

        Returns:
            Данные группы из VK API или None
        """
        try:
            group_data = await self.vk_service.get_group_info(identifier)

            if group_data:
                logger.info(f"Retrieved group data from VK: {identifier}")
                return group_data
            else:
                logger.warning(f"Group not found in VK: {identifier}")
                return None

        except Exception as e:
            logger.error(
                f"Error getting group data from VK for {identifier}: {e}"
            )
            return None

    async def extract_screen_name(self, identifier: str) -> Optional[str]:
        """
        Извлечь screen_name из полного URL или идентификатора.

        Args:
            identifier: URL группы, screen_name или VK ID

        Returns:
            screen_name группы или None
        """
        try:
            import re

            # Удаляем протоколы и домены
            identifier = re.sub(r"https?://(www\.)?vk\.com/", "", identifier)

            # Удаляем параметры запроса
            identifier = identifier.split("?")[0].split("#")[0]

            # Проверяем что это screen_name (не цифры)
            if identifier and not identifier.isdigit():
                # Проверяем через VK API
                if await self.validate_screen_name(identifier):
                    return identifier

            # Если это цифры или невалидный screen_name
            logger.warning(f"Invalid group identifier: {identifier}")
            return None

        except Exception as e:
            logger.error(
                f"Error extracting screen_name from {identifier}: {e}"
            )
            return None

    async def validate_group_access(self, group_id: int) -> bool:
        """
        Проверить доступ к контенту группы.

        Args:
            group_id: VK ID группы

        Returns:
            True если есть доступ, False иначе
        """
        try:
            # Пробуем получить посты группы
            posts = await self.vk_service.get_group_posts(group_id, count=1)
            has_access = len(posts) > 0

            logger.info(f"Group access validation: {group_id} -> {has_access}")
            return has_access

        except Exception as e:
            logger.error(f"Error validating access to group {group_id}: {e}")
            return False

    async def refresh_group_data(self, db_group: VKGroup) -> Optional[Dict]:
        """
        Обновить данные группы из VK API.

        Args:
            db_group: Объект группы из базы данных

        Returns:
            Актуальные данные из VK API или None
        """
        try:
            # Используем screen_name если есть, иначе VK ID
            identifier = db_group.screen_name or str(db_group.vk_id)

            vk_data = await self.get_group_data_from_vk(identifier)

            if vk_data:
                logger.info(
                    f"Group data refreshed from VK: {db_group.screen_name}",
                    group_id=db_group.id,
                    vk_id=db_group.vk_id,
                )

            return vk_data

        except Exception as e:
            logger.error(
                f"Error refreshing group data for {db_group.screen_name}: {e}"
            )
            return None

    async def compare_with_vk_data(
        self, db_group: VKGroup, vk_data: Dict
    ) -> Dict:
        """
        Сравнить данные группы из БД с данными из VK API.

        Args:
            db_group: Группа из базы данных
            vk_data: Данные из VK API

        Returns:
            Словарь с различиями
        """
        try:
            differences = {}

            # Сравниваем основные поля
            if db_group.name != vk_data.get("name"):
                differences["name"] = {
                    "old": db_group.name,
                    "new": vk_data.get("name"),
                }

            if db_group.screen_name != vk_data.get("screen_name"):
                differences["screen_name"] = {
                    "old": db_group.screen_name,
                    "new": vk_data.get("screen_name"),
                }

            if db_group.vk_id != vk_data.get("id"):
                differences["vk_id"] = {
                    "old": db_group.vk_id,
                    "new": vk_data.get("id"),
                }

            # Сравниваем количество участников (если есть)
            if hasattr(db_group, "member_count") and vk_data.get(
                "members_count"
            ):
                if db_group.member_count != vk_data.get("members_count"):
                    differences["member_count"] = {
                        "old": db_group.member_count,
                        "new": vk_data.get("members_count"),
                    }

            logger.info(
                f"Compared group data: {len(differences)} differences found",
                group_id=db_group.id,
                differences=differences,
            )

            return differences

        except Exception as e:
            logger.error(
                f"Error comparing group data for {db_group.screen_name}: {e}"
            )
            return {}

    async def validate_multiple_groups(
        self, identifiers: list[str]
    ) -> Dict[str, bool]:
        """
        Проверить существование нескольких групп.

        Args:
            identifiers: Список screen_name или VK ID групп

        Returns:
            Словарь с результатами валидации {identifier: is_valid}
        """
        try:
            results = {}

            for identifier in identifiers:
                if identifier.isdigit():
                    # Это VK ID
                    is_valid = await self.validate_vk_id(int(identifier))
                else:
                    # Это screen_name
                    is_valid = await self.validate_screen_name(identifier)

                results[identifier] = is_valid

            logger.info(f"Validated {len(identifiers)} groups")
            return results

        except Exception as e:
            logger.error(f"Error validating multiple groups: {e}")
            return {}
