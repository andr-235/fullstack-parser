"""
Сервис для прямого взаимодействия с VK API
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
import httpx
from datetime import datetime
import time

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

    # VK API лимиты
    MAX_REQUESTS_PER_SECOND = 3  # Лимит запросов в секунду
    MAX_POSTS_PER_REQUEST = 100  # Максимум постов за запрос
    MAX_COMMENTS_PER_REQUEST = 100  # Максимум комментариев за запрос
    MAX_GROUPS_PER_REQUEST = 1000  # Максимум групп за поиск
    MAX_USERS_PER_REQUEST = 1000  # Максимум пользователей за запрос

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

        # Создаем HTTP клиент с настройками для VK API
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=5, max_connections=10
            ),
        )

        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset_time = time.time()

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

    async def _rate_limit(self):
        """Применяет rate limiting для VK API."""
        current_time = time.time()

        # Сброс счетчика каждую секунду
        if current_time - self.rate_limit_reset_time >= 1.0:
            self.request_count = 0
            self.rate_limit_reset_time = current_time

        # Если достигли лимита, ждем
        if self.request_count >= self.MAX_REQUESTS_PER_SECOND:
            wait_time = 1.0 - (current_time - self.rate_limit_reset_time)
            if wait_time > 0:
                self.logger.debug(f"Rate limit: ждем {wait_time:.2f} секунд")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_reset_time = time.time()

        self.request_count += 1

    async def _make_request(
        self, method: str, params: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Выполняет запрос к VK API с rate limiting.

        Args:
            method: Название метода VK API
            params: Параметры запроса

        Returns:
            Ответ от VK API

        Raises:
            VKAPIError: При ошибке VK API
        """
        # Применяем rate limiting
        await self._rate_limit()

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
                error_code = error.get("error_code", 0)
                error_msg = error.get("error_msg", "Unknown error")

                # Обработка специфических ошибок VK API
                if error_code == 6:  # Too many requests per second
                    self.logger.warning(
                        "VK API: слишком много запросов в секунду, ждем..."
                    )
                    await asyncio.sleep(1.0)
                    return await self._make_request(
                        method, params
                    )  # Рекурсивный вызов
                elif error_code == 9:  # Flood control
                    self.logger.warning(
                        "VK API: flood control, ждем 5 секунд..."
                    )
                    await asyncio.sleep(5.0)
                    return await self._make_request(
                        method, params
                    )  # Рекурсивный вызов
                elif error_code == 15:  # Access denied
                    self.logger.error(
                        f"VK API: доступ запрещен для метода {method}"
                    )
                    raise VKAPIError(
                        error_code, error_msg, error.get("request_params")
                    )
                else:
                    raise VKAPIError(
                        code=error_code,
                        message=error_msg,
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
            count: Количество постов (максимум 100)
            offset: Смещение

        Returns:
            Список постов
        """
        owner_id = self._ensure_group_owner_id(group_id)

        params = {
            "owner_id": owner_id,
            "count": min(count, self.MAX_POSTS_PER_REQUEST),
            "offset": offset,
        }

        response = await self._make_request("wall.get", params)
        if isinstance(response, dict):
            return response.get("items", [])
        return []

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
            count: Количество комментариев (максимум 100)
            offset: Смещение
            sort: Сортировка (asc, desc, smart)

        Returns:
            Список комментариев
        """
        # Для групп owner_id должен быть отрицательным
        if owner_id > 0:
            owner_id = -owner_id

        params = {
            "owner_id": owner_id,
            "post_id": post_id,
            "count": min(count, self.MAX_COMMENTS_PER_REQUEST),
            "offset": offset,
            "sort": sort,
            "need_likes": 1,
            "extended": 1,  # Получаем информацию о пользователях и группах
        }

        response = await self._make_request("wall.getComments", params)
        if isinstance(response, dict):
            return response.get("items", [])
        return []

    async def get_all_post_comments(
        self, owner_id: int, post_id: int, sort: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        Получает все комментарии к посту с пагинацией.

        Args:
            owner_id: ID владельца поста (для групп должен быть отрицательным)
            post_id: ID поста
            sort: Сортировка

        Returns:
            Список всех комментариев
        """
        # Для групп owner_id должен быть отрицательным
        if owner_id > 0:
            owner_id = -owner_id

        all_comments = []
        offset = 0
        count = self.MAX_COMMENTS_PER_REQUEST

        while True:
            try:
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

                # Если получили меньше чем запросили, значит это последняя страница
                if len(comments) < count:
                    break

                offset += count

                # Задержка между запросами для соблюдения лимитов
                await asyncio.sleep(0.5)

            except VKAPIError as e:
                if e.code == 15:  # Access denied
                    self.logger.error(
                        f"Доступ запрещен к комментариям поста {post_id}"
                    )
                    break
                else:
                    raise

        self.logger.info(
            f"Получены все комментарии к посту: owner_id={owner_id}, post_id={post_id}, total_comments={len(all_comments)}"
        )

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
        try:
            if isinstance(group_id_or_screen_name, int):
                params = {"group_id": str(abs(group_id_or_screen_name))}
            else:
                params = {"group_id": group_id_or_screen_name}

            response = await self._make_request("groups.getById", params)
            if isinstance(response, list) and response:
                return response[0]
            return None
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
            if isinstance(response, list) and response:
                return response[0]
            return None
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
            count: Количество результатов (максимум 1000)
            offset: Смещение

        Returns:
            Список найденных групп
        """
        params = {
            "q": query,
            "count": min(count, self.MAX_GROUPS_PER_REQUEST),
            "offset": offset,
            "type": "group",
        }

        response = await self._make_request("groups.search", params)
        if isinstance(response, dict):
            return response.get("items", [])
        return []

    async def close(self):
        """Закрывает HTTP клиент."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
