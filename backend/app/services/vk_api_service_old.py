"""
Сервис для прямого взаимодействия с VK API
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

import httpx

logger = logging.getLogger(__name__)


class VKAPIError(Exception):
    """Исключение для ошибок VK API."""

    def __init__(
        self,
        code: int,
        message: str,
        request_params: Optional[List[Dict]] = None,
    ):
        self.code = code
        self.message = message
        self.request_params = request_params
        super().__init__(f"VK API Error {code}: {message}")


class VKAPIService:
    """Сервис для прямого взаимодействия с VK API."""

    def __init__(self, token: str, api_version: str = "5.131"):
        """
        Инициализация сервиса.

        Args:
            token: Токен доступа VK API
            api_version: Версия VK API
        """
        self.token = token
        self.api_version = api_version
        self.base_url = "https://api.vk.com/method"
        self.logger = logger

        # Создаем HTTP клиент
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=5, max_connections=10
            ),
        )

        self.logger.info(
            f"VKAPIService инициализирован, версия API: {api_version}"
        )

    def _get_token_preview(self) -> str:
        """Возвращает превью токена для логирования."""
        if len(self.token) > 8:
            return f"{self.token[:4]}...{self.token[-4:]}"
        return "***"

    def _ensure_group_owner_id(self, group_id: int) -> int:
        """Преобразует ID группы в owner_id для VK API."""
        return -abs(group_id)

    async def _make_request(
        self, method: str, params: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Выполняет запрос к VK API.

        Args:
            method: Название метода VK API
            params: Параметры запроса

        Returns:
            Ответ от VK API

        Raises:
            VKAPIError: При ошибке VK API
        """
        # Добавляем обязательные параметры
        params.update({"access_token": self.token, "v": self.api_version})

        url = f"{self.base_url}/{method}"

        try:
            self.logger.debug(f"VK API запрос: {method}, параметры: {params}")

            response = await self.client.post(url, data=params)
            response.raise_for_status()

            data = response.json()

            # Проверяем на ошибки VK API
            if "error" in data:
                error = data["error"]
                raise VKAPIError(
                    code=error.get("error_code", 0),
                    message=error.get("error_msg", "Unknown error"),
                    request_params=error.get("request_params"),
                )

            return data.get("response", {})

        except httpx.HTTPError as e:
            self.logger.error(f"HTTP ошибка при запросе к VK API: {e}")
            raise VKAPIError(0, f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при запросе к VK API: {e}")
            raise VKAPIError(0, f"Unexpected error: {e}")

    async def get_group_posts(
        self, group_id: int, count: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получает посты группы.

        Args:
            group_id: ID группы
            count: Количество постов
            offset: Смещение

        Returns:
            Список постов
        """
        owner_id = self._ensure_group_owner_id(group_id)

        params = {
            "owner_id": owner_id,
            "count": min(count, 100),  # VK API ограничение
            "offset": offset,
        }

        response = await self._make_request("wall.get", params)
        return response.get("items", [])

    async def get_post_comments(
        self,
        owner_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
    ) -> List[Dict[str, Any]]:
        """
        Получает комментарии к посту.

        Args:
            owner_id: ID владельца поста
            post_id: ID поста
            count: Количество комментариев
            offset: Смещение
            sort: Сортировка (asc, desc, smart)

        Returns:
            Список комментариев
        """
        params = {
            "owner_id": owner_id,
            "post_id": post_id,
            "count": min(count, 100),  # VK API ограничение
            "offset": offset,
            "sort": sort,
            "need_likes": 1,
            "extended": 1,  # Получаем информацию о пользователях и группах
        }

        response = await self._make_request("wall.getComments", params)
        return response.get("items", [])

    async def get_all_post_comments(
        self, owner_id: int, post_id: int, sort: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        Получает все комментарии к посту.

        Args:
            owner_id: ID владельца поста
            post_id: ID поста
            sort: Сортировка

        Returns:
            Список всех комментариев
        """
        all_comments = []
        offset = 0
        count = 100

        while True:
            comments = await self.get_post_comments(
                owner_id=owner_id,
                post_id=post_id,
                count=count,
                offset=offset,
                sort=sort,
            )

            if not comments:
                break

            all_comments.extend(comments)

            if len(comments) < count:
                break

            offset += count

            # Небольшая задержка чтобы не перегружать API
            await asyncio.sleep(0.1)

        return all_comments

    async def get_group_info(
        self, group_id_or_screen_name: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о группе.

        Args:
            group_id_or_screen_name: ID группы или screen_name

        Returns:
            Информация о группе или None
        """
        if isinstance(group_id_or_screen_name, int):
            params = {"group_ids": abs(group_id_or_screen_name)}
        else:
            params = {"screen_name": group_id_or_screen_name}

        try:
            response = await self._make_request("groups.getById", params)
            return (
                response[0]
                if isinstance(response, list) and response
                else None
            )
        except VKAPIError as e:
            if e.code == 100:  # Group not found
                return None
            raise

    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе.

        Args:
            user_id: ID пользователя

        Returns:
            Информация о пользователе или None
        """
        params = {
            "user_ids": user_id,
            "fields": "first_name,last_name,screen_name,photo_100",
        }

        try:
            response = await self._make_request("users.get", params)
            return (
                response[0]
                if isinstance(response, list) and response
                else None
            )
        except VKAPIError as e:
            if e.code == 113:  # User not found
                return None
            raise

    async def search_groups(
        self, query: str, count: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Ищет группы по запросу.

        Args:
            query: Поисковый запрос
            count: Количество результатов
            offset: Смещение

        Returns:
            Список найденных групп
        """
        params = {
            "q": query,
            "count": min(count, 1000),  # VK API ограничение
            "offset": offset,
            "type": "group",
        }

        response = await self._make_request("groups.search", params)
        return response.get("items", [])

    async def close(self):
        """Закрывает HTTP клиент."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
