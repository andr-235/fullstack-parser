"""
Низкоуровневый клиент для работы с VK API

Реализует HTTP запросы к VK API с обработкой ошибок и rate limiting
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlencode

import aiohttp

from .config import vk_api_config
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
from .config import (
    VK_ERROR_ACCESS_DENIED,
    VK_ERROR_INVALID_REQUEST,
    VK_ERROR_TOO_MANY_REQUESTS,
    VK_ERROR_AUTH_FAILED,
    VK_ERROR_PERMISSION_DENIED,
    USER_AGENTS,
)


class VKAPIClient:
    """
    Низкоуровневый клиент для работы с VK API

    Предоставляет методы для выполнения HTTP запросов к VK API
    с автоматической обработкой ошибок, rate limiting и повторами
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Инициализация VK API клиента

        Args:
            access_token: Токен доступа к VK API
            session: HTTP сессия (опционально)
            logger: Логгер для записи событий
        """
        self.access_token = access_token or vk_api_config.access_token
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset_time = time.time()

        # Статистика
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        await self.close_session()

    async def ensure_session(self):
        """Убедиться, что HTTP сессия создана"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    total=vk_api_config.connection.timeout
                ),
                headers={
                    "User-Agent": USER_AGENTS[0],
                    "Accept": "application/json",
                },
            )

    async def close_session(self):
        """Закрыть HTTP сессию"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def make_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        http_method: str = "GET",
    ) -> Dict[str, Any]:
        """
        Выполнить запрос к VK API

        Args:
            method: Метод VK API
            params: Параметры запроса
            http_method: HTTP метод

        Returns:
            Dict[str, Any]: Ответ VK API

        Raises:
            VKAPIError: Ошибка VK API
        """
        # Применяем rate limiting
        await self._apply_rate_limit()

        # Подготавливаем параметры
        request_params = self._prepare_params(method, params or {})

        # Строим URL
        url = f"{vk_api_config.base_url}{method}"

        # Выполняем запрос с повторами
        return await self._execute_with_retry(
            url, request_params, http_method, method
        )

    async def _execute_with_retry(
        self,
        url: str,
        params: Dict[str, Any],
        http_method: str,
        vk_method: str,
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """
        Выполнить запрос с механизмом повтора

        Args:
            url: URL запроса
            params: Параметры запроса
            http_method: HTTP метод
            vk_method: Метод VK API
            attempt: Номер попытки

        Returns:
            Dict[str, Any]: Ответ VK API
        """
        try:
            # Выполняем запрос
            response_data = await self._execute_request(
                url, params, http_method, vk_method
            )

            # Проверяем на ошибки VK API
            self._check_vk_error(response_data, vk_method)

            # Увеличиваем счетчик успешных запросов
            self.successful_requests += 1

            return response_data

        except (
            VKAPIRateLimitError,
            VKAPITimeoutError,
            VKAPINetworkError,
        ) as e:
            # Эти ошибки можно повторять
            if attempt < vk_api_config.retry.max_attempts:
                wait_time = min(
                    vk_api_config.retry.backoff_factor**attempt,
                    vk_api_config.retry.max_delay,
                )

                self.logger.warning(
                    f"VK API request failed (attempt {attempt}/{vk_api_config.retry.max_attempts}), "
                    f"retrying in {wait_time:.2f}s: {e}"
                )

                await asyncio.sleep(wait_time)
                return await self._execute_with_retry(
                    url, params, http_method, vk_method, attempt + 1
                )
            else:
                # Исчерпаны попытки повтора
                self.failed_requests += 1
                raise e

        except Exception as e:
            # Другие ошибки не повторяем
            self.failed_requests += 1
            raise e

    async def _execute_request(
        self,
        url: str,
        params: Dict[str, Any],
        http_method: str,
        vk_method: str,
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос

        Args:
            url: URL запроса
            params: Параметры запроса
            http_method: HTTP метод
            vk_method: Метод VK API

        Returns:
            Dict[str, Any]: Ответ сервера

        Raises:
            VKAPITimeoutError: Превышено время ожидания
            VKAPINetworkError: Ошибка сети
            VKAPIInvalidResponseError: Неверный формат ответа
        """
        start_time = time.time()

        try:
            # Убеждаемся, что сессия существует
            await self.ensure_session()
            assert (
                self.session is not None
            )  # Для mypy: сессия гарантированно существует

            # Логируем запрос
            self.logger.debug(f"VK API Request: {vk_method} - {params}")

            # Выполняем запрос
            if http_method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_text = await response.text()
                    response_time = time.time() - start_time

                    # Логируем ответ
                    self.logger.debug(
                        f"VK API Response: {vk_method} - {response.status} - {response_time:.2f}s"
                    )

                    # Проверяем статус ответа
                    if response.status == 429:
                        raise VKAPIRateLimitError(method=vk_method)
                    elif response.status >= 500:
                        raise VKAPINetworkError(
                            f"Server error: {response.status}"
                        )
                    elif response.status >= 400:
                        raise VKAPIError(
                            f"Client error: {response.status}",
                            method=vk_method,
                        )

                    # Парсим JSON ответ
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError as e:
                        raise VKAPIInvalidResponseError(
                            response_text, f"Invalid JSON response: {str(e)}"
                        )
            else:
                # Для POST запросов
                async with self.session.post(url, data=params) as response:
                    response_text = await response.text()
                    response_time = time.time() - start_time

                    # Аналогичная обработка
                    if response.status == 429:
                        raise VKAPIRateLimitError(method=vk_method)
                    elif response.status >= 500:
                        raise VKAPINetworkError(
                            f"Server error: {response.status}"
                        )
                    elif response.status >= 400:
                        raise VKAPIError(
                            f"Client error: {response.status}",
                            method=vk_method,
                        )

                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError as e:
                        raise VKAPIInvalidResponseError(
                            response_text, f"Invalid JSON response: {str(e)}"
                        )

        except asyncio.TimeoutError:
            raise VKAPITimeoutError(
                timeout=vk_api_config.connection.timeout, method=vk_method
            )
        except aiohttp.ClientError as e:
            raise VKAPINetworkError(
                f"Network error: {str(e)}", {"method": vk_method}
            )

    def _prepare_params(
        self, method: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Подготовить параметры запроса

        Args:
            method: Метод VK API
            params: Исходные параметры

        Returns:
            Dict[str, Any]: Подготовленные параметры
        """
        # Базовые параметры
        prepared_params = {
            "access_token": self.access_token,
            "v": vk_api_config.api_version,
        }

        # Добавляем пользовательские параметры
        prepared_params.update(params)

        # Удаляем None значения
        prepared_params = {
            k: v for k, v in prepared_params.items() if v is not None
        }

        return prepared_params

    def _check_vk_error(self, response: Dict[str, Any], method: str):
        """
        Проверить ответ VK API на ошибки

        Args:
            response: Ответ VK API
            method: Метод VK API

        Raises:
            VKAPIError: Ошибка VK API
        """
        if "error" in response:
            error_info = response["error"]
            error_code = error_info.get("error_code", 0)
            error_msg = error_info.get("error_msg", "Unknown error")

            # Определяем тип ошибки
            if error_code == VK_ERROR_ACCESS_DENIED:
                raise VKAPIAuthError(f"Access denied: {error_msg}")
            elif error_code == VK_ERROR_TOO_MANY_REQUESTS:
                raise VKAPIRateLimitError(method=method)
            elif error_code == VK_ERROR_INVALID_REQUEST:
                raise VKAPIInvalidParamsError(
                    error_info.get("request_params", {}),
                    f"Invalid request: {error_msg}",
                )
            elif error_code == VK_ERROR_AUTH_FAILED:
                raise VKAPIInvalidTokenError(
                    f"Authentication failed: {error_msg}"
                )
            elif error_code == VK_ERROR_PERMISSION_DENIED:
                raise VKAPIAccessDeniedError(method, error_msg)
            else:
                raise VKAPIError(
                    error_msg,
                    error_code=error_code,
                    method=method,
                    details=error_info,
                )

    async def _apply_rate_limit(self):
        """
        Применить rate limiting

        Raises:
            VKAPIRateLimitError: Превышен лимит запросов
        """
        current_time = time.time()

        # Сброс счетчика каждую секунду
        if current_time - self.rate_limit_reset_time >= 1.0:
            self.request_count = 0
            self.rate_limit_reset_time = current_time

        # Проверяем лимит
        if (
            self.request_count
            >= vk_api_config.rate_limit.max_requests_per_second
        ):
            wait_time = 1.0 - (current_time - self.rate_limit_reset_time)
            if wait_time > 0:
                self.logger.info(
                    f"Rate limit reached, waiting {wait_time:.2f}s"
                )
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_reset_time = time.time()

        self.request_count += 1
        self.total_requests += 1
        self.last_request_time = current_time

    def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику клиента

        Returns:
            Dict[str, Any]: Статистика использования
        """
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "current_request_count": self.request_count,
            "last_request_time": self.last_request_time,
            "rate_limit_reset_time": self.rate_limit_reset_time,
            "time_until_reset": max(
                0, 1.0 - (time.time() - self.rate_limit_reset_time)
            ),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье подключения к VK API

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            # Проверяем токен доступа
            if not self.access_token:
                return {
                    "status": "unhealthy",
                    "error": "Access token not configured",
                    "timestamp": time.time(),
                }

            # Выполняем тестовый запрос
            test_params = {
                "user_ids": "1",
                "fields": vk_api_config.user_fields,
            }
            response = await self.make_request("users.get", test_params)

            if "response" in response and len(response["response"]) > 0:
                stats = self.get_stats()
                return {
                    "status": "healthy",
                    "response_time": time.time(),
                    "timestamp": time.time(),
                    **stats,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Invalid response format",
                    "timestamp": time.time(),
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            }

    def get_token_preview(self) -> str:
        """
        Получить превью токена для логирования

        Returns:
            str: Превью токена
        """
        if self.access_token and len(self.access_token) > 8:
            return f"{self.access_token[:4]}...{self.access_token[-4:]}"
        return "***"


# Экспорт
__all__ = [
    "VKAPIClient",
]
