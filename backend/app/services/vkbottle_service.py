from typing import List, Optional

import requests  # type: ignore
import structlog
from vkbottle.api import API

VK_API_VERSION_DEFAULT = "5.199"
SUPPORTED_SORT_VALUES = {"asc", "desc", "smart"}


class VKAPIException(Exception):
    """Кастомное исключение для ошибок VK API."""

    pass


class VKBottleService:
    """
    Сервис для работы с VK API через VKBottle.

    Args:
        token (str): VK API access token
        api_version (str): Версия VK API
    """

    def __init__(
        self, token: str, api_version: str = VK_API_VERSION_DEFAULT
    ) -> None:
        if not token or token == "your-vk-app-id":
            raise ValueError(
                "[VKBottleService] VK_ACCESS_TOKEN не передан или дефолтный! Проверь переменные окружения и .env."
            )
        self.logger = structlog.get_logger(__name__)
        # self.logger.warning(f"VKBottleService: создаём API с токеном: {repr(token)}")  # УДАЛЕНО: не логируем токен
        self.api = API(token)
        self.logger.info(
            f"VKBottleService: self.api создан, тип: {type(self.api)}, dir: {dir(self.api)}"
        )
        # Логируем только структуру, не содержимое токена
        try:
            self.logger.debug(
                f"VKBottleService: self.api.__dict__ = {list(self.api.__dict__.keys())}"
            )
        except Exception as e:
            self.logger.error(
                f"VKBottleService: Ошибка при логировании структуры self.api: {e}"
            )
        self.api_version = api_version
        self._token_preview = self._get_token_preview(token)
        self.logger.info(
            "VKBottleService инициализирован",
            api_version=api_version,
            token_preview=self._token_preview,
        )

    @staticmethod
    def _get_token_preview(token: str) -> str:
        if not token or len(token) < 10:
            return "NO_TOKEN"
        return f"{token[:6]}...{token[-4:]}"

    @staticmethod
    def _ensure_group_owner_id(group_id: int) -> int:
        """Гарантирует, что owner_id для группы отрицательный."""
        return -abs(group_id)

    async def get_group_posts(
        self, group_id: int, count: int = 100, offset: int = 0
    ) -> List[dict]:
        """
        Получить посты группы ВКонтакте.

        Args:
            group_id (int): ID группы ВКонтакте
            count (int): Количество постов
            offset (int): Смещение
        Returns:
            List[dict]: Список постов
        Raises:
            VKAPIException: При ошибке VK API
        """
        owner_id = self._ensure_group_owner_id(group_id)
        self.logger.info(
            "Получение постов группы",
            owner_id=owner_id,
            count=count,
            offset=offset,
            api_version=self.api_version,
        )
        try:
            response = await self.api.wall.get(
                owner_id=owner_id,
                count=count,
                offset=offset,
                v=self.api_version,
            )
            items = (
                response.items
                if hasattr(response, "items")
                else response.get("items", [])
            )
            if not items:
                self.logger.warning(
                    "VK API вернул пустой или неожиданный ответ при получении постов",
                    group_id=group_id,
                    response=str(response),
                )
                return []
            return items
        except Exception as e:
            self.logger.error(
                "Ошибка VK API при получении постов группы",
                group_id=group_id,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Ошибка VK API при получении постов: {e}"
            ) from e

    async def get_post_comments(
        self,
        owner_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
    ) -> List[dict]:
        """
        Получить комментарии к посту ВКонтакте через VKBottle API.

        Args:
            owner_id (int): ID владельца стены (отрицательный для групп)
            post_id (int): ID поста
            count (int): Количество комментариев
            offset (int): Смещение
            sort (str): Сортировка (asc, desc, smart)
        Returns:
            List[dict]: Список комментариев
        Raises:
            VKAPIException: При ошибке VK API
        """
        if sort not in SUPPORTED_SORT_VALUES:
            self.logger.warning(
                "Некорректный sort, заменяю на 'asc'",
                sort=sort,
            )
            sort = "asc"
        if owner_id > 0:
            self.logger.info(
                "owner_id был положительным, меняю на отрицательный",
                owner_id=owner_id,
            )
            owner_id = -owner_id
        self.logger.info(
            "Получение комментариев к посту",
            owner_id=owner_id,
            post_id=post_id,
            count=count,
            offset=offset,
            sort=sort,
            api_version=self.api_version,
            token_preview=self._token_preview,
        )
        try:
            response = await self.api.wall.get_comments(
                owner_id=owner_id,
                post_id=post_id,
                count=count,
                offset=offset,
                sort=sort,
                v=self.api_version,
            )
            items = response.items if hasattr(response, "items") else []
            return items
        except Exception as e:
            self.logger.error(
                "VK API error при получении комментариев",
                owner_id=owner_id,
                post_id=post_id,
                error=str(e),
                exc_info=True,
            )
            # Для отладки — прямой запрос
            self._log_direct_vk_request(
                owner_id=owner_id,
                post_id=post_id,
                count=count,
                offset=offset,
                sort=sort,
            )
            raise VKAPIException(
                f"Ошибка VK API при получении комментариев: {e}"
            ) from e

    def _log_direct_vk_request(
        self,
        owner_id: int,
        post_id: int,
        count: int,
        offset: int,
        sort: str,
    ) -> None:
        """
        Выполняет прямой запрос к VK API через requests для отладки и логирует ответ.
        """
        try:
            token = (
                self.api._API__token
                if hasattr(self.api, "_API__token")
                else None
            )
            if not token:
                self.logger.warning(
                    "Не удалось получить токен для прямого запроса"
                )
                return
            params = {
                "owner_id": owner_id,
                "post_id": post_id,
                "count": count,
                "offset": offset,
                "sort": sort,
                "v": self.api_version,
                "access_token": token,
            }
            r = requests.get(
                "https://api.vk.com/method/wall.getComments",
                params=params,
                timeout=10,
            )
            self.logger.info(
                "[DEBUG VK API direct] Ответ VK API",
                status_code=r.status_code,
                text=r.text,
            )
        except Exception as req_e:
            self.logger.error(
                "[DEBUG VK API direct] Ошибка прямого запроса",
                error=str(req_e),
                exc_info=True,
            )

    async def get_group_info(
        self, group_id_or_screen_name: str | int
    ) -> Optional[dict]:
        """
        Получить информацию о группе ВКонтакте.

        Args:
            group_id_or_screen_name (str | int): ID группы или screen_name
        Returns:
            Optional[dict]: Информация о группе или None
        Raises:
            VKAPIException: При ошибке VK API
        """
        try:
            if isinstance(group_id_or_screen_name, str):
                # Если передан screen_name, используем groups.getById
                response = await self.api.groups.get_by_id(
                    group_id=group_id_or_screen_name,
                    v=self.api_version,
                )
            else:
                # Если передан числовой ID
                response = await self.api.groups.get_by_id(
                    group_id=group_id_or_screen_name,
                    v=self.api_version,
                )

            # VKBottle API возвращает список объектов, берем первый элемент
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            elif hasattr(response, "__getitem__") and len(response) > 0:
                return response[0]
            else:
                self.logger.warning(
                    "VK API вернул пустой или неожиданный ответ при получении информации о группе",
                    group_id_or_screen_name=group_id_or_screen_name,
                    response=str(response),
                )
                return None
        except Exception as e:
            self.logger.error(
                "Ошибка VK API при получении информации о группе",
                group_id_or_screen_name=group_id_or_screen_name,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Ошибка VK API при получении информации о группе: {e}"
            ) from e
