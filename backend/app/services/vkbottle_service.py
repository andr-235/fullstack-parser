"""
Сервис для работы с VK API через VKBottle
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx
from vkbottle import API


# Создаем собственный класс VKAPIError
class VKAPIError(Exception):
    """Исключение для ошибок VK API."""

    def __init__(self):
        super().__init__()
        self.code = 0
        self.description = ""
        self.request_params = None


from vkbottle.modules import logger as vkbottle_logger

# Отключаем логи VKBottle для уменьшения шума
vkbottle_logger.setLevel(logging.WARNING)

# Константы
VK_API_VERSION_DEFAULT = "5.131"


class SortOrder(str, Enum):
    """Поддерживаемые значения сортировки комментариев."""

    ASC = "asc"
    DESC = "desc"
    SMART = "smart"


@dataclass
class VKAPIErrorInfo:
    """Информация об ошибке VK API."""

    error_code: int
    error_msg: str
    request_params: Optional[List[Dict[str, Any]]] = None


class VKAPIException(Exception):
    """Исключение для ошибок VK API."""

    def __init__(
        self, message: str, error_info: Optional[VKAPIErrorInfo] = None
    ):
        super().__init__(message)
        self.error_info = error_info


class VKBottleService:
    """Сервис для работы с VK API через VKBottle."""

    def __init__(
        self, token: str, api_version: str = VK_API_VERSION_DEFAULT
    ) -> None:
        """
        Инициализация сервиса.

        Args:
            token: Токен доступа VK API
            api_version: Версия VK API
        """
        self._token = token
        self.api_version = api_version
        self.logger = logging.getLogger(__name__)

        # Создаем API клиент
        self.api = API(token=token)

        self.logger.info(
            f"VKBottleService инициализирован, токен: {self._get_token_preview(token)}, версия API: {api_version}"
        )

    @staticmethod
    def _get_token_preview(token: str) -> str:
        """Возвращает превью токена для логирования."""
        if len(token) > 8:
            return f"{token[:4]}...{token[-4:]}"
        return "***"

    @staticmethod
    def _ensure_group_owner_id(group_id: int) -> int:
        """Преобразует ID группы в owner_id для VK API."""
        return -abs(group_id)

    def _create_vk_api_error(self, error_data: Any) -> VKAPIError:
        """Создает объект VKAPIError из данных ошибки."""
        error = VKAPIError()
        if isinstance(error_data, dict):
            error.code = error_data.get("error_code", 0)
            error.description = error_data.get("error_msg", str(error_data))
            error.request_params = error_data.get("request_params")
        else:
            error.code = 0
            error.description = str(error_data)
        return error

    def _handle_vk_api_error(
        self, error: VKAPIError, context: str
    ) -> VKAPIException:
        """
        Обрабатывает ошибки VK API и создает информативное исключение.

        Args:
            error: Объект ошибки VK API
            context: Контекст операции для логирования

        Returns:
            VKAPIException с детальной информацией об ошибке
        """
        error_info = VKAPIErrorInfo(
            error_code=getattr(error, "code", 0),
            error_msg=getattr(error, "description", str(error)),
            request_params=getattr(error, "request_params", None),
        )

        self.logger.error(
            f"VK API ошибка в {context}: {error_info.error_msg} (код: {error_info.error_code})"
        )

        return VKAPIException(
            f"VK API ошибка в {context}: {error_info.error_msg} (код: {error_info.error_code})",
            error_info,
        )

    async def get_group_posts(
        self, group_id: int, count: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получить посты группы ВКонтакте.

        Args:
            group_id: ID группы ВКонтакте
            count: Количество постов (максимум 100)
            offset: Смещение от начала

        Returns:
            Список постов в виде словарей

        Raises:
            VKAPIException: При ошибке VK API
        """
        owner_id = self._ensure_group_owner_id(group_id)

        self.logger.info(
            f"Получение постов группы: owner_id={owner_id}, count={count}, offset={offset}, api_version={self.api_version}"
        )

        try:
            # Используем прямые HTTP запросы к VK API для получения постов
            url = "https://api.vk.com/method/wall.get"
            params = {
                "owner_id": owner_id,
                "count": count,
                "offset": offset,
                "access_token": self._token,
                "v": self.api_version,
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "error" in data:
                    error_data = data["error"]
                    if isinstance(error_data, dict):
                        error = VKAPIError()
                        error.code = error_data.get("error_code", 0)
                        error.description = error_data.get(
                            "error_msg", str(error_data)
                        )
                        error.request_params = error_data.get("request_params")
                        raise error
                    else:
                        error = VKAPIError()
                        error.code = 0
                        error.description = str(error_data)
                        raise error

                if "response" in data and data["response"]:
                    posts = data["response"]["items"]
                    print(
                        f"[VK DEBUG] Получено {len(posts)} постов для группы {group_id}"
                    )
                    print(f"[VK DEBUG] Полный ответ VK API: {data}")
                    self.logger.info(
                        f"Успешно получены посты через HTTP API: group_id={group_id}, posts_count={len(posts)}, response_keys={list(data['response'].keys())}"
                    )

                    # Логируем первый пост для отладки
                    if posts:
                        first_post = posts[0]
                        print(
                            f"[VK DEBUG] Первый пост: ID={first_post.get('id')}, Owner ID={first_post.get('owner_id')}"
                        )
                        print(
                            f"[VK DEBUG] Первый пост полностью: {first_post}"
                        )
                        self.logger.info(
                            f"Пример структуры поста: post_keys={list(first_post.keys())}, post_id={first_post.get('id')}, post_owner_id={first_post.get('owner_id')}, post_text_preview={(first_post.get('text', '')[:100] + '...') if first_post.get('text') else 'empty'}, post_type={type(first_post).__name__}"
                        )
                    else:
                        self.logger.warning(
                            f"VK API вернул пустой список постов: group_id={group_id}"
                        )

                    return posts
                else:
                    self.logger.warning(
                        f"VK API вернул пустой ответ при получении постов: group_id={group_id}"
                    )
                    return []

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении постов группы"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка при получении постов группы: group_id={group_id}, error={str(e)}",
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении постов: {e}"
            ) from e

    async def get_post_comments(
        self,
        owner_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: Union[str, SortOrder] = SortOrder.ASC,
    ) -> List[Dict[str, Any]]:
        """
        Получить комментарии к посту ВКонтакте.

        Args:
            owner_id: ID владельца стены (отрицательный для групп)
            post_id: ID поста
            count: Количество комментариев (максимум 100)
            offset: Смещение от начала
            sort: Сортировка комментариев

        Returns:
            Список комментариев в виде словарей

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            f"Получение комментариев к посту: owner_id={owner_id}, post_id={post_id}, count={count}, offset={offset}, sort={sort}"
        )

        try:
            # Используем прямые HTTP запросы к VK API
            url = "https://api.vk.com/method/wall.getComments"
            params = {
                "owner_id": owner_id,
                "post_id": post_id,
                "count": count,
                "offset": offset,
                "sort": sort,
                "access_token": self._token,
                "v": self.api_version,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "error" in data:
                    error_data = data["error"]
                    if isinstance(error_data, dict):
                        error = VKAPIError()
                        error.code = error_data.get("error_code", 0)
                        error.description = error_data.get(
                            "error_msg", str(error_data)
                        )
                        error.request_params = error_data.get("request_params")
                        raise error
                    else:
                        error = VKAPIError()
                        error.code = 0
                        error.description = str(error_data)
                        raise error

                if "response" in data and data["response"]:
                    comments = data["response"]["items"]
                    self.logger.info(
                        f"Успешно получены комментарии через HTTP API: owner_id={owner_id}, post_id={post_id}, comments_count={len(comments)}"
                    )
                    return comments
                else:
                    self.logger.warning(
                        f"VK API вернул пустой ответ при получении комментариев: owner_id={owner_id}, post_id={post_id}"
                    )
                    return []

        except VKAPIError as e:
            raise self._handle_vk_api_error(e, "получении комментариев") from e
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка при получении комментариев: owner_id={owner_id}, post_id={post_id}, error={str(e)}",
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении комментариев: {e}"
            ) from e

    async def get_all_post_comments(
        self,
        owner_id: int,
        post_id: int,
        sort: Union[str, SortOrder] = SortOrder.ASC,
    ) -> List[Dict[str, Any]]:
        """
        Получить ВСЕ комментарии к посту ВКонтакте (с пагинацией).

        Args:
            owner_id: ID владельца стены (отрицательный для групп)
            post_id: ID поста
            sort: Сортировка комментариев

        Returns:
            Список всех комментариев в виде словарей

        Raises:
            VKAPIException: При ошибке VK API
        """
        all_comments = []
        offset = 0
        count = 100  # Максимум за один запрос

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

                # Добавляем небольшую задержку чтобы не превысить лимиты VK API
                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении комментариев с пагинацией: owner_id={owner_id}, post_id={post_id}, offset={offset}, error={str(e)}"
                )
                break

        self.logger.info(
            f"Получены все комментарии к посту: owner_id={owner_id}, post_id={post_id}, total_comments={len(all_comments)}"
        )

        return all_comments

    async def get_group_info(
        self, group_id_or_screen_name: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о группе ВКонтакте.

        Args:
            group_id_or_screen_name: ID группы или короткое имя

        Returns:
            Информация о группе в виде словаря или None

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            f"Получение информации о группе: group_id_or_screen_name={group_id_or_screen_name}"
        )

        try:
            # Используем прямые HTTP запросы к VK API
            url = "https://api.vk.com/method/groups.getById"
            params = {
                "group_id": group_id_or_screen_name,
                "access_token": self._token,
                "v": self.api_version,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "error" in data:
                    error_data = data["error"]
                    if isinstance(error_data, dict):
                        error = VKAPIError()
                        error.code = error_data.get("error_code", 0)
                        error.description = error_data.get(
                            "error_msg", str(error_data)
                        )
                        error.request_params = error_data.get("request_params")
                        raise error
                    else:
                        error = VKAPIError()
                        error.code = 0
                        error.description = str(error_data)
                        raise error

                if "response" in data and data["response"]:
                    group_info = data["response"][0]
                    self.logger.info(
                        f"Успешно получена информация о группе через HTTP API: group_id_or_screen_name={group_id_or_screen_name}, group_name={group_info.get('name', 'Unknown')}, group_keys={list(group_info.keys())}, group_id={group_info.get('id')}, group_screen_name={group_info.get('screen_name')}"
                    )
                    return group_info
                else:
                    self.logger.warning(
                        f"VK API вернул пустой ответ при получении информации о группе: group_id_or_screen_name={group_id_or_screen_name}"
                    )
                    return None

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении информации о группе"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка при получении информации о группе: group_id_or_screen_name={group_id_or_screen_name}, error={str(e)}",
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении информации о группе: {e}"
            ) from e

    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о пользователе ВКонтакте.

        Args:
            user_id: ID пользователя

        Returns:
            Информация о пользователе в виде словаря или None

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            f"Получение информации о пользователе: user_id={user_id}"
        )

        try:
            # Используем прямые HTTP запросы к VK API
            url = "https://api.vk.com/method/users.get"
            params = {
                "user_ids": user_id,
                "fields": "id,first_name,last_name,screen_name,photo_100",
                "access_token": self._token,
                "v": self.api_version,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "error" in data:
                    error_data = data["error"]
                    if isinstance(error_data, dict):
                        error = VKAPIError()
                        error.code = error_data.get("error_code", 0)
                        error.description = error_data.get(
                            "error_msg", str(error_data)
                        )
                        error.request_params = error_data.get("request_params")
                        raise error
                    else:
                        error = VKAPIError()
                        error.code = 0
                        error.description = str(error_data)
                        raise error

                if "response" in data and data["response"]:
                    user_info = data["response"][0]
                    self.logger.info(
                        f"Успешно получена информация о пользователе через HTTP API: user_id={user_id}, user_name={user_info.get('first_name', '')} {user_info.get('last_name', '')}, user_keys={list(user_info.keys())}"
                    )
                    return user_info
                else:
                    self.logger.warning(
                        f"VK API вернул пустой ответ при получении информации о пользователе: user_id={user_id}"
                    )
                    return None

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении информации о пользователе"
            ) from e
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка при получении информации о пользователе: user_id={user_id}, error={str(e)}",
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении информации о пользователе: {e}"
            ) from e

    async def search_groups(
        self, query: str, count: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Поиск групп ВКонтакте.

        Args:
            query: Поисковый запрос
            count: Количество результатов
            offset: Смещение от начала

        Returns:
            Список найденных групп

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            f"Поиск групп: query={query}, count={count}, offset={offset}"
        )

        try:
            # Используем прямые HTTP запросы к VK API
            url = "https://api.vk.com/method/groups.search"
            params = {
                "q": query,
                "count": count,
                "offset": offset,
                "access_token": self._token,
                "v": self.api_version,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()

                if "error" in data:
                    error_data = data["error"]
                    if isinstance(error_data, dict):
                        error = VKAPIError()
                        error.code = error_data.get("error_code", 0)
                        error.description = error_data.get(
                            "error_msg", str(error_data)
                        )
                        error.request_params = error_data.get("request_params")
                        raise error
                    else:
                        error = VKAPIError()
                        error.code = 0
                        error.description = str(error_data)
                        raise error

                if "response" in data and data["response"]:
                    groups = data["response"]["items"]
                    self.logger.info(
                        f"Успешно получены результаты поиска групп через HTTP API: query={query}, groups_count={len(groups)}"
                    )
                    return groups
                else:
                    self.logger.warning(
                        f"VK API вернул пустой ответ при поиске групп: query={query}"
                    )
                    return []

        except VKAPIError as e:
            raise self._handle_vk_api_error(e, "поиске групп") from e
        except Exception as e:
            self.logger.error(
                f"Неожиданная ошибка при поиске групп: query={query}, error={str(e)}",
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при поиске групп: {e}"
            ) from e

    async def close(self) -> None:
        """Закрывает соединения."""
        # VKBottle API не требует явного закрытия
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
