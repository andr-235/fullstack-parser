"""
Сервис для работы с VK API через VKBottle 4.5.2+.

Модуль предоставляет асинхронный интерфейс для взаимодействия с VK API,
используя современные возможности VKBottle с правильной типизацией,
обработкой ошибок и логированием.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog
from vkbottle import API
from vkbottle.api import API as VKBottleAPI
from vkbottle.exception_factory import VKAPIError
from vkbottle_types.objects import (
    GroupsGroupFull,
    WallWallComment,
    WallWallpostFull,
)
from vkbottle_types.responses import (
    WallGetCommentsResponseModel,
    WallGetResponseModel,
)

# Константы
VK_API_VERSION_DEFAULT = "5.199"
SUPPORTED_SORT_VALUES = {"asc", "desc", "smart"}


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
    """Кастомное исключение для ошибок VK API с дополнительной информацией."""

    def __init__(
        self, message: str, error_info: Optional[VKAPIErrorInfo] = None
    ):
        super().__init__(message)
        self.error_info = error_info


class VKBottleService:
    """
    Современный сервис для работы с VK API через VKBottle 4.5.2+.

    Использует актуальные возможности библиотеки:
    - Правильная типизация с vkbottle-types
    - Асинхронные методы с корректной обработкой ошибок
    - Структурированное логирование
    - Middleware-совместимая архитектура
    """

    def __init__(
        self, token: str, api_version: str = VK_API_VERSION_DEFAULT
    ) -> None:
        """
        Инициализация сервиса VK API.

        Args:
            token: VK API access token
            api_version: Версия VK API

        Raises:
            ValueError: Если токен не передан или дефолтный
        """
        if not token or token == "your-vk-app-id":
            raise ValueError(
                "VK_ACCESS_TOKEN не передан или дефолтный! "
                "Проверь переменные окружения и .env."
            )

        self.logger = structlog.get_logger(__name__)
        self.api_version = api_version
        self._token_preview = self._get_token_preview(token)

        # Инициализация VKBottle API с правильной типизацией
        self.api: VKBottleAPI = API(token)

        self.logger.info(
            "VKBottleService инициализирован",
            api_version=api_version,
            token_preview=self._token_preview,
            vkbottle_version="4.5.2+",
        )

    @staticmethod
    def _get_token_preview(token: str) -> str:
        """Создает безопасный превью токена для логирования."""
        if not token or len(token) < 10:
            return "NO_TOKEN"
        return f"{token[:6]}...{token[-4:]}"

    @staticmethod
    def _ensure_group_owner_id(group_id: int) -> int:
        """Гарантирует, что owner_id для группы отрицательный."""
        return -abs(group_id)

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
            f"VK API ошибка в {context}",
            error_code=error_info.error_code,
            error_msg=error_info.error_msg,
            request_params=error_info.request_params,
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
            "Получение постов группы",
            owner_id=owner_id,
            count=count,
            offset=offset,
            api_version=self.api_version,
        )

        try:
            response: WallGetResponseModel = await self.api.wall.get(
                owner_id=owner_id,
                count=count,
                offset=offset,
                v=self.api_version,
            )

            # Извлекаем посты из ответа
            posts = self._extract_posts_from_response(response)

            if not posts:
                self.logger.warning(
                    "VK API вернул пустой ответ при получении постов",
                    group_id=group_id,
                    response_type=type(response).__name__,
                )
                return []

            self.logger.info(
                "Успешно получены посты группы",
                group_id=group_id,
                posts_count=len(posts),
            )

            return posts

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении постов группы"
            ) from e
        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка при получении постов группы",
                group_id=group_id,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении постов: {e}"
            ) from e

    def _extract_posts_from_response(
        self, response: WallGetResponseModel
    ) -> List[Dict[str, Any]]:
        """
        Извлекает посты из ответа VK API с правильной типизацией.

        Args:
            response: Ответ от VK API

        Returns:
            Список постов в виде словарей
        """
        if not hasattr(response, "items") or not response.items:
            return []

        # Конвертируем объекты WallWallpostFull в словари
        posts = []
        for post in response.items:
            if isinstance(post, WallWallpostFull):
                # Используем model_dump() для Pydantic моделей
                if hasattr(post, "model_dump"):
                    posts.append(post.model_dump())
                else:
                    # Fallback для старых версий
                    posts.append(vars(post))
            else:
                # Если это уже словарь
                posts.append(post)

        return posts

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
        # Валидация и нормализация параметров
        if isinstance(sort, str):
            if sort not in SUPPORTED_SORT_VALUES:
                self.logger.warning(
                    "Некорректный sort, заменяю на 'asc'",
                    sort=sort,
                )
                sort = SortOrder.ASC
            else:
                sort = SortOrder(sort)

        # Обеспечиваем отрицательный owner_id для групп
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
            sort=sort.value,
            api_version=self.api_version,
        )

        try:
            response: WallGetCommentsResponseModel = (
                await self.api.wall.get_comments(
                    owner_id=owner_id,
                    post_id=post_id,
                    count=count,
                    offset=offset,
                    sort=sort.value,
                    v=self.api_version,
                )
            )

            # Извлекаем комментарии из ответа
            comments = self._extract_comments_from_response(response)

            self.logger.info(
                "Успешно получены комментарии к посту",
                owner_id=owner_id,
                post_id=post_id,
                comments_count=len(comments),
            )

            return comments

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении комментариев к посту"
            ) from e
        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка при получении комментариев",
                owner_id=owner_id,
                post_id=post_id,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении комментариев: {e}"
            ) from e

    def _extract_comments_from_response(
        self, response: WallGetCommentsResponseModel
    ) -> List[Dict[str, Any]]:
        """
        Извлекает комментарии из ответа VK API с правильной типизацией.

        Args:
            response: Ответ от VK API

        Returns:
            Список комментариев в виде словарей
        """
        if not hasattr(response, "items") or not response.items:
            return []

        # Конвертируем объекты WallWallComment в словари
        comments = []
        for comment in response.items:
            if isinstance(comment, WallWallComment):
                # Используем model_dump() для Pydantic моделей
                if hasattr(comment, "model_dump"):
                    comments.append(comment.model_dump())
                else:
                    # Fallback для старых версий
                    comments.append(vars(comment))
            else:
                # Если это уже словарь
                comments.append(comment)

        return comments

    async def get_group_info(
        self, group_id_or_screen_name: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о группе ВКонтакте.

        Args:
            group_id_or_screen_name: ID группы или screen_name

        Returns:
            Информация о группе в виде словаря или None

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            "Получение информации о группе",
            group_id_or_screen_name=group_id_or_screen_name,
            api_version=self.api_version,
        )

        try:
            response = await self.api.groups.get_by_id(
                group_id=group_id_or_screen_name,
                v=self.api_version,
            )

            # Извлекаем информацию о группе из ответа
            group_info = self._extract_group_info_from_response(response)

            if group_info:
                self.logger.info(
                    "Успешно получена информация о группе",
                    group_id_or_screen_name=group_id_or_screen_name,
                    group_name=group_info.get("name", "Unknown"),
                )
            else:
                self.logger.warning(
                    "VK API вернул пустой ответ при получении информации о группе",
                    group_id_or_screen_name=group_id_or_screen_name,
                )

            return group_info

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении информации о группе"
            ) from e
        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка при получении информации о группе",
                group_id_or_screen_name=group_id_or_screen_name,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении информации о группе: {e}"
            ) from e

    def _extract_group_info_from_response(
        self, response: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Извлекает информацию о группе из ответа VK API.

        Args:
            response: Ответ от VK API

        Returns:
            Информация о группе в виде словаря или None
        """
        # В VKBottle 4.5.2+ API возвращает список объектов напрямую
        if isinstance(response, list) and len(response) > 0:
            group = response[0]
            if isinstance(group, GroupsGroupFull):
                # Используем model_dump() для Pydantic моделей
                if hasattr(group, "model_dump"):
                    return dict(group.model_dump())
                else:
                    # Fallback для старых версий
                    return dict(vars(group))
            else:
                # Если это уже словарь
                return dict(group) if isinstance(group, dict) else None

        # Проверяем альтернативные форматы ответа
        if (
            hasattr(response, "response")
            and isinstance(response.response, list)
            and len(response.response) > 0
        ):
            group = response.response[0]
            if isinstance(group, GroupsGroupFull):
                if hasattr(group, "model_dump"):
                    return dict(group.model_dump())
                else:
                    return dict(vars(group))
            else:
                return dict(group) if isinstance(group, dict) else None

        return None

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
            "Получение информации о пользователе",
            user_id=user_id,
            api_version=self.api_version,
        )

        try:
            response = await self.api.users.get(
                user_ids=[user_id],
                v=self.api_version,
            )

            if response and len(response) > 0:
                user = response[0]
                # Конвертируем в словарь
                if hasattr(user, "model_dump"):
                    user_info = user.model_dump()
                else:
                    user_info = vars(user)

                self.logger.info(
                    "Успешно получена информация о пользователе",
                    user_id=user_id,
                    user_name=f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
                )

                return user_info
            else:
                self.logger.warning(
                    "VK API вернул пустой ответ при получении информации о пользователе",
                    user_id=user_id,
                )
                return None

        except VKAPIError as e:
            raise self._handle_vk_api_error(
                e, "получении информации о пользователе"
            ) from e
        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка при получении информации о пользователе",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при получении информации о пользователе: {e}"
            ) from e

    async def search_groups(
        self, query: str, count: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Поиск групп ВКонтакте по запросу.

        Args:
            query: Поисковый запрос
            count: Количество результатов (максимум 1000)
            offset: Смещение от начала

        Returns:
            Список найденных групп

        Raises:
            VKAPIException: При ошибке VK API
        """
        self.logger.info(
            "Поиск групп ВКонтакте",
            query=query,
            count=count,
            offset=offset,
            api_version=self.api_version,
        )

        try:
            response = await self.api.groups.search(
                q=query,
                count=count,
                offset=offset,
                v=self.api_version,
            )

            if hasattr(response, "items") and response.items:
                groups = []
                for group in response.items:
                    if hasattr(group, "model_dump"):
                        groups.append(group.model_dump())
                    else:
                        groups.append(vars(group))

                self.logger.info(
                    "Успешно найдены группы",
                    query=query,
                    groups_count=len(groups),
                )

                return groups
            else:
                self.logger.info(
                    "По запросу группы не найдены",
                    query=query,
                )
                return []

        except VKAPIError as e:
            raise self._handle_vk_api_error(e, "поиске групп") from e
        except Exception as e:
            self.logger.error(
                "Неожиданная ошибка при поиске групп",
                query=query,
                error=str(e),
                exc_info=True,
            )
            raise VKAPIException(
                f"Неожиданная ошибка при поиске групп: {e}"
            ) from e

    async def close(self) -> None:
        """Закрывает соединения и освобождает ресурсы."""
        try:
            if hasattr(self.api, "close"):
                await self.api.close()
            self.logger.info("VKBottleService закрыт")
        except Exception as e:
            self.logger.error(
                "Ошибка при закрытии VKBottleService", error=str(e)
            )

    async def __aenter__(self):
        """Поддержка async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста."""
        await self.close()
