"""
VK API Service Module

Этот модуль предоставляет высокоуровневый интерфейс для работы с VK API.
Включает бизнес-логику для получения постов, комментариев, информации о группах
и пользователях с поддержкой кеширования, rate limiting и обработки ошибок.

Основные возможности:
- Получение постов групп с пагинацией
- Получение комментариев к постам
- Поиск групп по запросам
- Получение информации о пользователях
- Валидация токенов доступа
- Кеширование результатов запросов
- Автоматическое логирование операций

Примеры использования:

    # 1. Простое создание экземпляра (рекомендуемый способ)
    from .dependencies import create_vk_api_service

    # Создание экземпляра для внутреннего использования
    vk_service = create_vk_api_service()

    # Использование в бизнес-логике
    posts = await vk_service.get_group_posts(group_id=12345, count=10)
    comments = await vk_service.get_post_comments(
        group_id=12345, post_id=67890, count=50
    )

    # 2. Использование в других сервисах
    class MyService:
        def __init__(self):
            self.vk_api = create_vk_api_service()

        async def my_method(self):
            posts = await self.vk_api.get_group_posts(12345)

    # 3. Передача существующего экземпляра
    existing_service = create_vk_api_service()
    my_service = MyService(vk_api_service=existing_service)

Архитектура:
- BaseVKAPIService: Базовый класс с общими методами
- VKAPIService: Основной сервис с бизнес-логикой
- Декораторы для валидации, кеширования и логирования
- Утилиты для стандартизации ответов

Автор: AI Assistant
Версия: 2.0 (после рефакторинга)
Дата: 2024
"""

import logging
import time
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone

from ..exceptions import (
    ValidationError,
    ServiceUnavailableError,
)
from .exceptions import (
    VKAPIError,
    VKAPIRateLimitError,
    VKAPIAuthError,
    VKAPIAccessDeniedError,
    VKAPIInvalidTokenError,
    VKAPIInvalidParamsError,
    VKAPITimeoutError,
    VKAPINetworkError,
    VKAPIInvalidResponseError,
)
from ..infrastructure.logging import get_winston_logger
from .base import (
    BaseVKAPIService,
    validate_id,
    validate_count,
    cached,
    log_request,
    circuit_breaker,
    rate_limit,
    timeout,
    retry,
)
from .models import VKAPIRepository
from .client import VKAPIClient
from .config import vk_api_config
from .metrics import vk_api_metrics
from .helpers import (
    create_posts_response,
    create_comments_response,
    create_users_response,
    create_groups_response,
    create_post_response,
    create_group_response,
    create_health_response,
    create_stats_response,
    create_limits_response,
    create_token_validation_response,
    create_group_members_response,
)


class VKAPIService(BaseVKAPIService):
    """
    Основной сервис для работы с VK API

    Этот класс наследует от BaseVKAPIService и предоставляет высокоуровневые
    методы для взаимодействия с VK API. Включает автоматическую валидацию
    параметров, кеширование результатов, rate limiting и подробное логирование.

    Атрибуты:
        repository (VKAPIRepository): Репозиторий для работы с данными и кешем
        client (VKAPIClient): Низкоуровневый клиент для HTTP запросов к VK API
        logger (logging.Logger): Логгер для записи операций и ошибок

    Примечания:
        - Все методы являются асинхронными
        - Параметры автоматически валидируются декораторами
        - Результаты кешируются для улучшения производительности
        - Ошибки логируются и преобразуются в стандартные исключения

    Примеры:
        >>> service = VKAPIService(repository, client)
        >>> posts = await service.get_group_posts(12345, count=5)
        >>> print(f"Получено {len(posts['posts'])} постов")
    """

    def __init__(
        self, repository: VKAPIRepository, client: Optional[VKAPIClient] = None
    ):
        # Инициализация базового класса для circuit breakers и rate limiters
        super().__init__(repository, client or VKAPIClient())

        # Используем Winston-подобный логгер для enterprise-grade логирования
        self.logger = get_winston_logger("vk-api-service")
        # Сохраняем стандартный логгер для обратной совместимости
        self._std_logger = logging.getLogger(__name__)

        # Инициализация метрик
        self._metrics = vk_api_metrics

    @log_request("wall.get")
    @cached(
        "group:{group_id}:posts:{count}:{offset}",
        vk_api_config.cache.group_posts_ttl,
    )
    @retry(max_attempts=3, backoff_factor=2.0)  # Повторные попытки при сбоях
    @timeout(25.0)  # Таймаут для получения постов
    @rate_limit(max_calls=100, time_window=60.0)  # Ограничение запросов постов
    @circuit_breaker(
        failure_threshold=5, recovery_timeout=60.0
    )  # Защита от массовых сбоев
    @validate_count(vk_api_config.limits.max_posts_per_request)
    @validate_id("group_id")
    async def get_group_posts(
        self, group_id: int, count: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Получить посты группы с сбором метрик производительности"""
        start_time = time.time()

        try:
            # Получить посты группы с полной защитой от сбоев
            # Этот метод включает все уровни защиты:
            # - Circuit Breaker: Защита от каскадных сбоев (5 неудач → открытие)
            # - Rate Limiting: Контроль частоты (100 запросов/минуту)
            # - Timeout: Защита от зависаний (25 сек)
            # - Retry: Повторные попытки (3 попытки с экспоненциальной задержкой)
            # - Caching: Кеширование результатов (5 мин TTL)
            # - Logging: Подробное логирование всех операций
            # Получаем данные через клиент
            params = {
                "owner_id": -abs(
                    group_id
                ),  # VK API использует отрицательные ID для групп
                "count": count,
                "offset": offset,
            }

            response = await self.client.make_request("wall.get", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            posts_data = response["response"]
            posts = posts_data.get("items", [])

            result = create_posts_response(
                posts=posts,
                total_count=posts_data.get("count", 0),
                requested_count=count,
                offset=offset,
                has_more=len(posts) == count,
            )
            result["group_id"] = group_id
            return result

        except VKAPIAuthError:
            # Re-raise authentication errors without wrapping them
            raise
        except (
            VKAPIRateLimitError,
            VKAPIAccessDeniedError,
            VKAPIInvalidTokenError,
            VKAPIInvalidParamsError,
            VKAPITimeoutError,
            VKAPINetworkError,
            VKAPIInvalidResponseError,
            VKAPIError,
        ):
            # Re-raise VK API errors without wrapping them
            raise
        except Exception as e:
            self.logger.error(
                "Failed to get group posts",
                meta={
                    "group_id": group_id,
                    "count": count,
                    "offset": offset,
                    "error": str(e),
                    "operation": "get_group_posts",
                },
            )
            raise ServiceUnavailableError(
                f"Ошибка получения постов группы: {str(e)}"
            )

    @validate_id("group_id")
    @validate_id("post_id")
    @validate_count(vk_api_config.limits.max_comments_per_request)
    @cached(
        "post:{post_id}:comments:{count}:{offset}:{sort}",
        vk_api_config.cache.post_comments_ttl,
    )
    @log_request("wall.getComments")
    async def get_post_comments(
        self,
        group_id: int,
        post_id: int,
        count: int = 100,
        offset: int = 0,
        sort: str = "asc",
    ) -> Dict[str, Any]:
        """
        Получить комментарии к посту

        Args:
            group_id: ID группы VK
            post_id: ID поста
            count: Количество комментариев
            offset: Смещение
            sort: Сортировка (asc, desc)

        Returns:
            Dict[str, Any]: Комментарии с метаданными
        """
        # Дополнительная валидация сортировки
        if sort not in ["asc", "desc"]:
            raise ValidationError("Неверная сортировка", field="sort")

        try:
            # Получаем данные через клиент
            params = {
                "owner_id": -abs(group_id),
                "post_id": post_id,
                "count": count,
                "offset": offset,
                "sort": sort,
            }

            response = await self.client.make_request(
                "wall.getComments", params
            )

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            comments_data = response["response"]
            comments = comments_data.get("items", [])

            return create_comments_response(
                comments=comments,
                total_count=comments_data.get("count", 0),
                requested_count=count,
                offset=offset,
                has_more=len(comments) == count,
                group_id=group_id,
                post_id=post_id,
                sort=sort,
            )

        except Exception as e:
            self.logger.error(
                "Failed to get post comments",
                meta={
                    "group_id": group_id,
                    "post_id": post_id,
                    "count": count,
                    "offset": offset,
                    "sort": sort,
                    "error": str(e),
                    "operation": "get_post_comments",
                },
            )
            raise ServiceUnavailableError(
                f"Ошибка получения комментариев: {str(e)}"
            )

    @validate_id("group_id")
    @cached("group:{group_id}:info", vk_api_config.cache.group_info_ttl)
    @log_request("groups.getById")
    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """
        Получить информацию о группе

        Args:
            group_id: ID группы VK

        Returns:
            Dict[str, Any]: Информация о группе
        """
        try:
            # Получаем данные через клиент
            params = {
                "group_ids": str(group_id),
                "fields": vk_api_config.group_fields,
            }

            response = await self.client.make_request("groups.getById", params)

            if "response" not in response or not response["response"]:
                raise ServiceUnavailableError(f"Группа {group_id} не найдена")

            group_data = response["response"][0]

            result = {
                "id": group_data.get("id"),
                "name": group_data.get("name", ""),
                "screen_name": group_data.get("screen_name", ""),
                "description": group_data.get("description", ""),
                "members_count": group_data.get("members_count", 0),
                "photo_url": group_data.get("photo_200", ""),
                "is_closed": group_data.get("is_closed", False),
                "type": group_data.get("type", "group"),
            }

            return create_group_response(result)

        except Exception as e:
            self.logger.error(f"Error getting group info for {group_id}: {e}")
            raise ServiceUnavailableError(
                f"Ошибка получения информации о группе: {str(e)}"
            )

    @validate_count(vk_api_config.limits.max_groups_per_request)
    @rate_limit(
        max_calls=20, time_window=60.0
    )  # Дополнительное ограничение на поиск
    @circuit_breaker(
        failure_threshold=3, recovery_timeout=30.0
    )  # Защита от сбоев поиска
    @timeout(15.0)  # Таймаут для поиска
    @retry(
        max_attempts=2, backoff_factor=1.5
    )  # Повторные попытки при временных сбоях
    @cached(
        "search:groups:{query}:{count}:{offset}:{country}:{city}",
        vk_api_config.cache.search_ttl,
    )
    @log_request("groups.search")
    async def search_groups(
        self,
        query: str,
        count: int = 20,
        offset: int = 0,
        country: Optional[int] = None,
        city: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Поиск групп по запросу

        Args:
            query: Поисковый запрос
            count: Количество результатов
            offset: Смещение
            country: ID страны
            city: ID города

        Returns:
            Dict[str, Any]: Результаты поиска
        """
        if not query or not query.strip():
            raise ValidationError(
                "Поисковый запрос не может быть пустым", field="query"
            )

        try:
            # Получаем данные через клиент
            params = {
                "q": query.strip(),
                "count": count,
                "offset": offset,
            }

            if country is not None:
                params["country"] = country
            if city is not None:
                params["city"] = city

            response = await self.client.make_request("groups.search", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            search_data = response["response"]

            return create_groups_response(
                groups=search_data.get("items", []),
                total_count=search_data.get("count", 0),
                requested_count=count,
                offset=offset,
                has_more=len(search_data.get("items", [])) == count,
                query=query,
                country=country,
                city=city,
            )

        except Exception as e:
            self.logger.error(
                f"Error searching groups with query '{query}': {e}"
            )
            raise ServiceUnavailableError(f"Ошибка поиска групп: {str(e)}")

    @rate_limit(
        max_calls=30, time_window=60.0
    )  # Ограничение на запросы пользователей
    @circuit_breaker(
        failure_threshold=5, recovery_timeout=45.0
    )  # Защита от массовых сбоев
    @timeout(20.0)  # Таймаут для получения данных пользователей
    @retry(
        max_attempts=3, backoff_factor=1.8
    )  # Повторные попытки для надежности
    @cached("users:{user_ids}:info", vk_api_config.cache.user_info_ttl)
    @log_request("users.get")
    async def get_user_info(
        self, user_ids: Union[int, List[int]]
    ) -> Dict[str, Any]:
        """
        Получить информацию о пользователе(ях)

        Args:
            user_ids: ID пользователя или список ID

        Returns:
            Dict[str, Any]: Информация о пользователе(ях)
        """
        # Нормализуем входные данные
        if isinstance(user_ids, int):
            user_ids = [user_ids]

        if not user_ids:
            raise ValidationError(
                "Список ID пользователей не может быть пустым",
                field="user_ids",
            )

        if len(user_ids) > vk_api_config.limits.max_users_per_request:
            raise ValidationError(
                f"Слишком много пользователей (макс {vk_api_config.limits.max_users_per_request})",
                field="user_ids",
            )

        try:
            # Получаем данные через клиент
            params = {
                "user_ids": ",".join(map(str, user_ids)),
                "fields": vk_api_config.user_fields,
            }

            response = await self.client.make_request("users.get", params)

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            users_data = response["response"]

            return create_users_response(
                users=users_data,
                requested_ids=user_ids,
                found_count=len(users_data),
            )

        except Exception as e:
            self.logger.error(f"Error getting user info for {user_ids}: {e}")
            raise ServiceUnavailableError(
                f"Ошибка получения информации о пользователях: {str(e)}"
            )

    @validate_id("group_id")
    @validate_count(vk_api_config.limits.max_group_members_per_request)
    @circuit_breaker(
        failure_threshold=5, recovery_timeout=60.0
    )  # Защита от массовых сбоев
    @rate_limit(
        max_calls=10, time_window=60.0
    )  # Строгое ограничение на запросы участников
    @timeout(30.0)  # Таймаут для получения участников
    @retry(max_attempts=3, backoff_factor=2.0)  # Повторные попытки при сбоях
    @cached(
        "group:{group_id}:members:{count}:{offset}",
        vk_api_config.cache.group_members_ttl,
    )
    @log_request("groups.getMembers")
    async def get_group_members(
        self,
        group_id: int,
        count: int = 1000,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Получить участников группы с полной защитой от сбоев

        Этот метод включает все уровни защиты:
        - Circuit Breaker: Защита от каскадных сбоев (5 неудач → открытие)
        - Rate Limiting: Контроль частоты (10 запросов/минуту)
        - Timeout: Защита от зависаний (30 сек)
        - Retry: Повторные попытки (3 попытки с экспоненциальной задержкой)
        - Caching: Кеширование результатов (5 мин TTL)
        - Logging: Подробное логирование всех операций

        Args:
            group_id: ID группы VK (положительное целое число)
            count: Количество участников (1-1000, по умолчанию 1000)
            offset: Смещение для пагинации (по умолчанию 0)

        Returns:
            Dict[str, Any]: Стандартизированный ответ с участниками группы

        Raises:
            ServiceUnavailableError: При превышении лимитов или системных сбоях
            ValidationError: При некорректных входных данных

        Пример:
            >>> members = await service.get_group_members(12345, count=500)
            >>> print(f"Получено {len(members['members'])} участников")
        """
        try:
            # Получаем данные через клиент
            params = {
                "group_id": abs(
                    group_id
                ),  # VK API использует положительные ID для групп
                "count": count,
                "offset": offset,
                "fields": vk_api_config.group_members_fields,  # Поля для получения информации об участниках
            }

            response = await self.client.make_request(
                "groups.getMembers", params
            )

            if "response" not in response:
                raise ServiceUnavailableError("Неверный формат ответа VK API")

            members_data = response["response"]
            members = members_data.get("items", [])
            total_count = members_data.get("count", 0)

            # Определяем, есть ли еще участники для загрузки
            has_more = offset + len(members) < total_count

            return create_group_members_response(
                members=members,
                total_count=total_count,
                requested_count=count,
                offset=offset,
                has_more=has_more,
                group_id=group_id,
            )

        except Exception as e:
            self.logger.error(
                f"Error getting group members for {group_id}: {e}"
            )
            raise ServiceUnavailableError(
                f"Ошибка получения участников группы: {str(e)}"
            )

    @validate_id("group_id")
    @validate_count(50)  # Максимум 50 постов за раз для массовой операции
    @circuit_breaker(
        failure_threshold=5, recovery_timeout=60.0
    )  # Защита от каскадных сбоев
    @rate_limit(
        max_calls=20, time_window=60.0
    )  # Ограничение на массовые операции
    @timeout(30.0)  # Таймаут для массовой операции
    @retry(max_attempts=2, backoff_factor=2.0)  # Повторные попытки при сбоях
    @log_request("bulk_wall.getById")
    async def get_bulk_posts(
        self,
        group_id: int,
        post_ids: List[int],
    ) -> Dict[str, Any]:
        """
        Массовое получение постов с параллельной обработкой

        Этот метод оптимизирован для высокой производительности:
        - Использует asyncio.gather для параллельной обработки запросов
        - Лимитирует количество одновременных запросов для предотвращения перегрузки
        - Обрабатывает ошибки индивидуально для каждого поста
        - Предоставляет детальную статистику выполнения

        Args:
            group_id: ID группы VK
            post_ids: Список ID постов для получения

        Returns:
            Dict[str, Any]: Результаты массового получения постов

        Raises:
            ServiceUnavailableError: При системных сбоях
            ValidationError: При некорректных входных данных
        """
        import asyncio
        from datetime import datetime

        start_time = time.time()

        # Валидация количества постов
        max_bulk_posts = 50  # Максимум постов в одном запросе
        if len(post_ids) > max_bulk_posts:
            raise ValidationError(
                f"Слишком много постов. Максимум: {max_bulk_posts}, запрошено: {len(post_ids)}",
                field="post_ids",
            )

        # Лимит одновременных запросов для предотвращения перегрузки VK API
        concurrency_limit = 10
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def fetch_single_post(post_id: int) -> Optional[Dict[str, Any]]:
            """
            Получить один пост с контролем параллелизма

            Args:
                post_id: ID поста для получения

            Returns:
                Optional[Dict[str, Any]]: Данные поста или None при ошибке
            """
            async with semaphore:
                try:
                    post_data = await self.get_post_by_id(group_id, post_id)
                    return post_data
                except Exception as e:
                    # Логируем ошибку, но не прерываем весь процесс
                    self.logger.warning(
                        f"Не удалось получить пост {post_id} группы {group_id}: {e}"
                    )
                    return None

        # Создаем задачи для параллельного выполнения
        tasks = [fetch_single_post(post_id) for post_id in post_ids]

        # Выполняем все запросы параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        posts = []
        errors = []

        for i, result in enumerate(results):
            post_id = post_ids[i]
            if isinstance(result, Exception):
                errors.append(f"Пост {post_id}: {str(result)}")
                self.logger.error(
                    f"Критическая ошибка при получении поста {post_id}: {result}"
                )
            elif result is not None:
                posts.append(result)
            # Если result is None, значит пост пропущен (уже залогировано выше)

        # Записываем метрики выполнения
        duration = time.time() - start_time
        self._metrics.record_bulk_operation(
            total_items=len(post_ids),
            success_count=len(posts),
            duration=duration,
        )

        # Логируем итоговую статистику
        success_rate = len(posts) / len(post_ids) * 100
        self.logger.info(
            f"Массовое получение постов завершено: "
            f"запрос {len(post_ids)} постов, "
            f"успешно {len(posts)}, "
            f"ошибок {len(errors)}, "
            f"успешность {success_rate:.1f}%, "
            f"время {duration:.2f}с"
        )

        return {
            "posts": posts,
            "total_requested": len(post_ids),
            "total_found": len(posts),
            "group_id": group_id,
            "fetched_at": datetime.now(timezone.utc).isoformat() + "Z",
            "errors": errors if errors else None,
            "success_rate": round(success_rate, 1),
            "processing_time_seconds": round(duration, 2),
        }

    @validate_id("group_id")
    @validate_id("post_id")
    @log_request("wall.getById")
    async def get_post_by_id(
        self, group_id: int, post_id: int
    ) -> Dict[str, Any]:
        """
        Получить пост по ID

        Args:
            group_id: ID группы VK
            post_id: ID поста

        Returns:
            Dict[str, Any]: Информация о посте
        """
        try:
            # Получаем данные через клиент
            params = {
                "posts": f"-{abs(group_id)}_{post_id}",
            }

            response = await self.client.make_request("wall.getById", params)

            if "response" not in response or not response["response"]:
                raise ServiceUnavailableError(f"Пост {post_id} не найден")

            post_data = response["response"][0]

            result = {
                "id": post_data.get("id"),
                "owner_id": post_data.get("owner_id"),
                "from_id": post_data.get("from_id"),
                "created_by": post_data.get("created_by"),
                "date": post_data.get("date"),
                "text": post_data.get("text", ""),
                "attachments": post_data.get("attachments", []),
                "comments": post_data.get("comments", {}),
                "likes": post_data.get("likes", {}),
                "reposts": post_data.get("reposts", {}),
                "views": post_data.get("views", {}),
                "is_pinned": post_data.get("is_pinned", False),
            }

            return create_post_response(result)

        except Exception as e:
            self.logger.error(
                f"Error getting post {post_id} from group {group_id}: {e}"
            )
            raise ServiceUnavailableError(f"Ошибка получения поста: {str(e)}")

    @rate_limit(
        max_calls=5, time_window=60.0
    )  # Строгое ограничение на валидацию токенов
    @circuit_breaker(
        failure_threshold=2, recovery_timeout=60.0
    )  # Быстрое восстановление
    @timeout(10.0)  # Быстрый таймаут для токенов
    @retry(max_attempts=2, backoff_factor=1.2)  # Минимум повторных попыток
    @log_request("users.get")
    async def validate_access_token(self) -> Dict[str, Any]:
        """
        Проверить валидность токена доступа

        Returns:
            Dict[str, Any]: Результат проверки токена
        """
        try:
            # Проверяем токен через получение информации о текущем пользователе
            params = {"fields": "id,first_name,last_name"}

            response = await self.client.make_request("users.get", params)

            if "response" in response and response["response"]:
                user_info = response["response"][0]
                return create_token_validation_response(
                    valid=True,
                    user_id=user_info.get("id"),
                    user_name=f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                )
            else:
                return create_token_validation_response(
                    valid=False, error="Invalid response format"
                )

        except Exception as e:
            return create_token_validation_response(valid=False, error=str(e))

    async def get_api_limits(self) -> Dict[str, Any]:
        """
        Получить текущие лимиты VK API

        Returns:
            Dict[str, Any]: Информация о лимитах API
        """
        client_stats = self.client.get_stats()

        return create_limits_response(
            max_requests_per_second=vk_api_config.rate_limit.max_requests_per_second,
            max_posts_per_request=vk_api_config.limits.max_posts_per_request,
            max_comments_per_request=vk_api_config.limits.max_comments_per_request,
            max_groups_per_request=vk_api_config.limits.max_groups_per_request,
            max_users_per_request=vk_api_config.limits.max_users_per_request,
            current_request_count=client_stats["current_request_count"],
            last_request_time=client_stats["last_request_time"],
            time_until_reset=client_stats["time_until_reset"],
        )

    async def get_resilience_stats(self) -> Dict[str, Any]:
        """
        Получить статистику устойчивости системы

        Returns:
            Dict[str, Any]: Статистика circuit breakers и rate limiters
        """
        # Базовый метод асинхронный; вызываем его асинхронно
        base_stats = await super().get_resilience_stats()
        return base_stats

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику сервиса

        Returns:
            Dict[str, Any]: Статистика
        """
        client_stats = self.client.get_stats()
        repo_stats = await self.repository.get_stats()

        return create_stats_response(
            client_stats=client_stats,
            repository_stats=repo_stats,
            cache_enabled=vk_api_config.cache.enabled,
            token_configured=vk_api_config.is_token_configured,
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье сервиса VK API

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            # Проверяем клиент
            client_health = await self.client.health_check()

            # Проверяем репозиторий
            repo_health = await self.repository.health_check()

            # Общий статус
            overall_status = (
                "healthy"
                if (
                    client_health["status"] == "healthy"
                    and repo_health["status"] == "healthy"
                )
                else "unhealthy"
            )

            return create_health_response(
                status=overall_status,
                client_status=client_health,
                repository_status=repo_health,
                error=None,
            )

        except Exception as e:
            return create_health_response(status="unhealthy", error=str(e))


# Экспорт
__all__ = [
    "VKAPIService",
]
