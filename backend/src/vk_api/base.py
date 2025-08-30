"""
Base Classes and Decorators for VK API Module

Этот модуль содержит базовые классы, декораторы и утилиты для работы с VK API.
Предоставляет переиспользуемые паттерны для уменьшения дублирования кода и
обеспечения一致ности архитектуры.

Основные компоненты:
- BaseVKAPIService: Базовый класс с общими методами для всех сервисов
- Декораторы для валидации, кеширования и логирования
- TimestampMixin: Утилиты для работы с временными метками
- Обработчики ошибок и валидации ответов API

Архитектурные принципы:
- DRY (Don't Repeat Yourself): Устранение дублирования кода
- SOLID: Разделение ответственности между классами
- Clean Code: Читаемый и поддерживаемый код
- Error Handling: Централизованная обработка ошибок

Примеры использования:

    # Использование декораторов
    @validate_id("group_id")
    @cached("group:{group_id}:data", 300)
    @log_request("groups.getById")
    async def get_group_data(self, group_id: int):
        # Бизнес-логика здесь
        pass

    # Использование базового класса
    class MyVKService(BaseVKAPIService):
        def __init__(self):
            super().__init__(repository, client)

Автор: AI Assistant
Версия: 1.0
Дата: 2024
"""

import time
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, Union
from functools import wraps
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

from ..exceptions import ValidationError, ServiceUnavailableError
from .config import vk_api_config


class CircuitBreakerState(Enum):
    """Состояния circuit breaker"""

    CLOSED = "closed"  # Нормальная работа
    OPEN = "open"  # Открыт - блокирует запросы
    HALF_OPEN = "half_open"  # Полуоткрыт - тестирует восстановление


class RateLimitStrategy(Enum):
    """Стратегии rate limiting"""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker"""

    failure_threshold: int = 5  # Количество неудач для открытия
    recovery_timeout: float = 60.0  # Время ожидания перед тестированием
    success_threshold: int = 3  # Количество успехов для закрытия
    timeout: float = 30.0  # Таймаут для запроса


@dataclass
class RateLimiterConfig:
    """Конфигурация rate limiter"""

    max_calls: int = 10  # Максимум вызовов
    time_window: float = 60.0  # Временное окно в секундах
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW


@dataclass
class CircuitBreakerStats:
    """Статистика circuit breaker"""

    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    total_requests: int = 0
    total_failures: int = 0


@dataclass
class RateLimiterStats:
    """Статистика rate limiter"""

    calls_in_window: int = 0
    window_start: float = field(default_factory=time.time)
    total_calls: int = 0
    total_rejected: int = 0


class BaseVKAPIService:
    """
    Базовый класс для всех VK API сервисов

    Этот абстрактный базовый класс предоставляет общие методы и паттерны
    для работы с VK API. Включает функциональность для:

    - Кеширования результатов запросов
    - Валидации входных параметров
    - Обработки и логирования ошибок
    - Стандартизации ответов API
    - Логирования запросов

    Наследники должны реализовывать специфичную бизнес-логику,
    используя предоставляемые базовые методы.

    Атрибуты:
        repository: Репозиторий для работы с данными и кешем
        client: HTTP клиент для запросов к VK API
        logger: Логгер для записи операций и ошибок

    Методы:
        _execute_with_cache: Выполнение запроса с кешированием
        _validate_id: Валидация ID параметров
        _validate_count: Валидация количества элементов
        _create_response: Создание стандартизированного ответа
        _log_request: Логирование запросов
        _handle_api_error: Централизованная обработка ошибок
        _validate_api_response: Валидация ответов API

    Примеры:
        >>> class MyService(BaseVKAPIService):
        ...     @validate_id("user_id")
        ...     @cached("user:{user_id}", 300)
        ...     async def get_user(self, user_id: int):
        ...         return await self._execute_with_cache(
        ...             f"user:{user_id}",
        ...             300,
        ...             lambda: self.client.get_user(user_id)
        ...         )
    """

    def __init__(self, repository=None, client=None):
        self.repository = repository
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

        # Инициализация менеджеров устойчивости
        self._circuit_breakers: Dict[str, CircuitBreakerStats] = {}
        self._rate_limiters: Dict[str, RateLimiterStats] = {}

        # Конфигурации по умолчанию
        self._default_circuit_config = CircuitBreakerConfig()
        self._default_rate_config = RateLimiterConfig()

    async def _execute_with_cache(
        self,
        cache_key: str,
        ttl_seconds: int,
        api_call: Callable,
    ) -> Dict[str, Any]:
        """
        Выполнить API вызов с кешированием

        Args:
            cache_key: Ключ кеша
            ttl_seconds: Время жизни кеша
            api_call: Функция API вызова (lambda без аргументов)

        Returns:
            Dict[str, Any]: Результат API вызова
        """
        # Проверяем кеш
        cached_result = await self.repository.get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Выполняем API вызов
        result = await api_call()

        # Сохраняем в кеш
        await self.repository.save_cached_result(
            cache_key, result, ttl_seconds
        )

        return result

    def _validate_id(
        self, value: int, field_name: str, allow_zero: bool = False
    ) -> None:
        """
        Валидировать ID

        Args:
            value: Значение для валидации
            field_name: Название поля для сообщения об ошибке
            allow_zero: Разрешать ли нулевое значение

        Raises:
            ValidationError: Если валидация не пройдена
        """
        if (
            not isinstance(value, int) or value <= 0
            if not allow_zero
            else value < 0
        ):
            raise ValidationError(f"Неверный {field_name}", field=field_name)

    def _validate_count(
        self, count: int, max_count: int, field_name: str = "count"
    ) -> int:
        """
        Валидировать и ограничить количество элементов

        Args:
            count: Запрошенное количество
            max_count: Максимально допустимое количество
            field_name: Название поля

        Returns:
            int: Валидированное количество

        Raises:
            ValidationError: Если валидация не пройдена
        """
        if count <= 0:
            raise ValidationError(
                f"Количество {field_name} должно быть положительным",
                field=field_name,
            )

        return min(count, max_count)

    def _create_response(
        self,
        data: Any,
        total_count: Optional[int] = None,
        has_more: bool = False,
        offset: int = 0,
        requested_count: Optional[int] = None,
        **additional_fields,
    ) -> Dict[str, Any]:
        """
        Создать стандартизированный ответ API

        Args:
            data: Основные данные ответа
            total_count: Общее количество элементов
            has_more: Есть ли еще элементы
            offset: Смещение
            requested_count: Запрошенное количество
            **additional_fields: Дополнительные поля

        Returns:
            Dict[str, Any]: Стандартизированный ответ
        """
        base_response = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "has_more": has_more,
            "offset": offset,
            **additional_fields,
        }

        if total_count is not None:
            base_response["total_count"] = total_count
        if requested_count is not None:
            base_response["requested_count"] = requested_count

        return base_response

    async def _log_request(
        self,
        method: str,
        params: Dict[str, Any],
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Логировать запрос к VK API

        Args:
            method: Метод VK API
            params: Параметры запроса
            response_time: Время ответа
            success: Успешность запроса
            error_message: Сообщение об ошибке
        """
        if vk_api_config.logging.log_requests or (
            not success and vk_api_config.logging.log_errors
        ):
            level = logging.INFO if success else logging.ERROR
            status = "SUCCESS" if success else "FAILED"

            message = f"VK API {method} - {status} - {response_time:.2f}s - params: {len(params)} items"

            if success:
                self.logger.info(
                    message,
                    meta={
                        "method": method,
                        "response_time": response_time,
                        "params_count": len(params),
                        "status": status,
                    },
                )
            else:
                self.logger.error(
                    message,
                    meta={
                        "method": method,
                        "response_time": response_time,
                        "params_count": len(params),
                        "status": status,
                        "error_message": error_message,
                    },
                )

            if error_message:
                self.logger.error(
                    f"VK API Error: {error_message}",
                    meta={"method": method, "error_message": error_message},
                )

    async def _handle_api_error(
        self, error: Exception, context: str, method: Optional[str] = None
    ) -> None:
        """
        Обработать ошибку API с логированием и перевыбросом

        Args:
            error: Исключение
            context: Контекст ошибки для логирования
            method: Метод VK API

        Raises:
            ServiceUnavailableError: Перевыбрасываемая ошибка сервиса
        """
        error_msg = f"{context}: {str(error)}"
        self.logger.error(error_msg)

        if method:
            await self._log_request(
                method=method,
                params={},
                response_time=0.0,
                success=False,
                error_message=error_msg,
            )

        from ..exceptions import ServiceUnavailableError

        raise ServiceUnavailableError(error_msg)

    async def _validate_api_response(
        self, response: Dict[str, Any], expected_field: str = "response"
    ) -> Dict[str, Any]:
        """
        Валидировать ответ VK API

        Args:
            response: Ответ от VK API
            expected_field: Ожидаемое поле в ответе

        Returns:
            Dict[str, Any]: Валидированные данные ответа

        Raises:
            ServiceUnavailableError: Если ответ невалиден
        """
        if expected_field not in response:
            await self._handle_api_error(
                ValueError(
                    f"Invalid VK API response format - missing '{expected_field}' field"
                ),
                "API Response Validation",
            )

        return response[expected_field]

    # Методы управления circuit breaker
    def _get_circuit_breaker_stats(
        self, method_name: str
    ) -> CircuitBreakerStats:
        """Получить статистику circuit breaker для метода"""
        if method_name not in self._circuit_breakers:
            self._circuit_breakers[method_name] = CircuitBreakerStats()
        return self._circuit_breakers[method_name]

    def _can_execute_request(
        self, method_name: str, config: CircuitBreakerConfig
    ) -> bool:
        """Проверить, можно ли выполнить запрос"""
        stats = self._get_circuit_breaker_stats(method_name)
        current_time = time.time()

        if stats.state == CircuitBreakerState.CLOSED:
            return True
        elif stats.state == CircuitBreakerState.OPEN:
            # Проверяем, прошло ли время восстановления
            if stats.last_failure_time and (
                current_time - stats.last_failure_time
                >= config.recovery_timeout
            ):
                stats.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(
                    f"Circuit breaker {method_name} moved to HALF_OPEN"
                )
                return True
            return False
        elif stats.state == CircuitBreakerState.HALF_OPEN:
            return True

        return False

    def _record_success(
        self, method_name: str, config: CircuitBreakerConfig
    ) -> None:
        """Записать успешный запрос"""
        stats = self._get_circuit_breaker_stats(method_name)
        current_time = time.time()

        stats.total_requests += 1
        stats.last_success_time = current_time

        if stats.state == CircuitBreakerState.HALF_OPEN:
            stats.success_count += 1
            if stats.success_count >= config.success_threshold:
                stats.state = CircuitBreakerState.CLOSED
                stats.failure_count = 0
                stats.success_count = 0
                self.logger.info(
                    f"Circuit breaker {method_name} moved to CLOSED"
                )

    def _record_failure(
        self, method_name: str, config: CircuitBreakerConfig
    ) -> None:
        """Записать неудачный запрос"""
        stats = self._get_circuit_breaker_stats(method_name)
        current_time = time.time()

        stats.total_requests += 1
        stats.total_failures += 1
        stats.failure_count += 1
        stats.last_failure_time = current_time

        if stats.state == CircuitBreakerState.HALF_OPEN:
            stats.state = CircuitBreakerState.OPEN
            stats.success_count = 0
            self.logger.warning(f"Circuit breaker {method_name} moved to OPEN")
        elif (
            stats.state == CircuitBreakerState.CLOSED
            and stats.failure_count >= config.failure_threshold
        ):
            stats.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker {method_name} moved to OPEN")

    # Методы управления rate limiter
    def _get_rate_limiter_stats(self, method_name: str) -> RateLimiterStats:
        """Получить статистику rate limiter для метода"""
        if method_name not in self._rate_limiters:
            self._rate_limiters[method_name] = RateLimiterStats()
        return self._rate_limiters[method_name]

    def _can_make_request(
        self, method_name: str, config: RateLimiterConfig
    ) -> bool:
        """Проверить, можно ли сделать запрос в рамках rate limit"""
        stats = self._get_rate_limiter_stats(method_name)
        current_time = time.time()

        # Сброс окна, если прошло время
        if current_time - stats.window_start >= config.time_window:
            stats.calls_in_window = 0
            stats.window_start = current_time

        return stats.calls_in_window < config.max_calls

    def _record_request(self, method_name: str, allowed: bool = True) -> None:
        """Записать запрос в статистику rate limiter"""
        stats = self._get_rate_limiter_stats(method_name)

        stats.total_calls += 1
        if not allowed:
            stats.total_rejected += 1
        else:
            stats.calls_in_window += 1

    def get_resilience_stats(self) -> Dict[str, Any]:
        """Получить статистику устойчивости системы"""
        return {
            "circuit_breakers": {
                name: {
                    "state": stats.state.value,
                    "failure_count": stats.failure_count,
                    "success_count": stats.success_count,
                    "total_requests": stats.total_requests,
                    "total_failures": stats.total_failures,
                }
                for name, stats in self._circuit_breakers.items()
            },
            "rate_limiters": {
                name: {
                    "calls_in_window": stats.calls_in_window,
                    "total_calls": stats.total_calls,
                    "total_rejected": stats.total_rejected,
                    "window_start": stats.window_start,
                }
                for name, stats in self._rate_limiters.items()
            },
        }


def validate_id(field_name: str, allow_zero: bool = False):
    """
    Декоратор для валидации ID параметров

    Args:
        field_name: Название поля для валидации
        allow_zero: Разрешать ли нулевое значение

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Извлекаем значение ID из аргументов
            if field_name in kwargs:
                value = kwargs[field_name]
            else:
                # Предполагаем, что ID - первый позиционный аргумент после self
                value = args[1] if len(args) > 1 else None

            if value is not None:
                self._validate_id(value, field_name, allow_zero)

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def validate_count(max_count: int, field_name: str = "count"):
    """
    Декоратор для валидации количества элементов

    Args:
        max_count: Максимально допустимое количество
        field_name: Название поля

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Извлекаем значение count из аргументов
            if field_name in kwargs:
                count = kwargs[field_name]
                validated_count = self._validate_count(
                    count, max_count, field_name
                )
                kwargs[field_name] = validated_count
            else:
                # Ищем count в позиционных аргументах
                for i, arg in enumerate(args[1:], 1):  # Пропускаем self
                    if isinstance(arg, int) and arg > 0:
                        validated_count = self._validate_count(
                            arg, max_count, field_name
                        )
                        args = list(args)
                        args[i] = validated_count
                        break

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def cached(cache_key_template: str, ttl_seconds: int):
    """
    Декоратор для кеширования результатов методов

    Args:
        cache_key_template: Шаблон ключа кеша
        ttl_seconds: Время жизни кеша

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Получаем сигнатуру функции для обработки параметров по умолчанию
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            try:
                # Генерируем ключ кеша с учетом всех параметров (включая по умолчанию)
                all_kwargs = dict(bound_args.arguments)
                del all_kwargs['self']  # Удаляем self из параметров

                cache_key = cache_key_template.format(**all_kwargs)

                # Используем базовый метод кеширования
                return await self._execute_with_cache(
                    cache_key, ttl_seconds, lambda: func(self, *args, **kwargs)
                )
            except KeyError:
                # Если не хватает параметров для ключа кеша, выполняем без кеширования
                return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def log_request(method_name: str):
    """
    Декоратор для логирования запросов

    Args:
        method_name: Название метода для логирования

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()

            try:
                result = await func(self, *args, **kwargs)
                response_time = time.time() - start_time

                await self._log_request(
                    method_name, kwargs, response_time, True
                )

                return result

            except Exception as e:
                response_time = time.time() - start_time

                await self._log_request(
                    method_name, kwargs, response_time, False, str(e)
                )

                raise

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 3,
    timeout: float = 30.0,
):
    """
    Декоратор Circuit Breaker для защиты от каскадных сбоев

    Args:
        failure_threshold: Количество неудач для открытия circuit breaker
        recovery_timeout: Время ожидания перед тестированием восстановления
        success_threshold: Количество успехов для закрытия circuit breaker
        timeout: Таймаут для запроса

    Returns:
        Callable: Декорированная функция

    Примеры:
        >>> @circuit_breaker(failure_threshold=3, recovery_timeout=30)
        ... async def api_call(self):
        ...     # Ваш код здесь
        ...     pass
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        timeout=timeout,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            method_name = f"{func.__name__}"

            # Проверяем, можно ли выполнить запрос
            if not self._can_execute_request(method_name, config):
                self.logger.warning(
                    f"Circuit breaker {method_name} is OPEN, request blocked"
                )
                raise ServiceUnavailableError(
                    f"Service {method_name} is temporarily unavailable"
                )

            try:
                # Выполняем запрос с таймаутом
                result = await asyncio.wait_for(
                    func(self, *args, **kwargs), timeout=config.timeout
                )

                # Записываем успех
                self._record_success(method_name, config)
                return result

            except asyncio.TimeoutError:
                error_msg = f"Request timeout for {method_name}"
                self.logger.warning(error_msg)
                self._record_failure(method_name, config)
                raise ServiceUnavailableError(error_msg)

            except Exception as e:
                # Записываем неудачу
                self._record_failure(method_name, config)
                raise

        return wrapper

    return decorator


def rate_limit(
    max_calls: int = 10,
    time_window: float = 60.0,
    strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW,
):
    """
    Декоратор Rate Limiter для контроля частоты запросов

    Args:
        max_calls: Максимальное количество вызовов в окне времени
        time_window: Размер окна времени в секундах
        strategy: Стратегия rate limiting

    Returns:
        Callable: Декорированная функция

    Примеры:
        >>> @rate_limit(max_calls=5, time_window=30)
        ... async def api_call(self):
        ...     # Ваш код здесь
        ...     pass
    """
    config = RateLimiterConfig(
        max_calls=max_calls,
        time_window=time_window,
        strategy=strategy,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            method_name = f"{func.__name__}"

            # Проверяем rate limit
            if not self._can_make_request(method_name, config):
                self.logger.warning(
                    f"Rate limit exceeded for {method_name} "
                    f"({config.max_calls} calls per {config.time_window}s)"
                )
                self._record_request(method_name, allowed=False)
                raise ServiceUnavailableError(
                    f"Rate limit exceeded for {method_name}"
                )

            # Записываем разрешенный запрос
            self._record_request(method_name, allowed=True)

            # Выполняем функцию
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def timeout(seconds: float = 30.0):
    """
    Декоратор для установки таймаута на выполнение функции

    Args:
        seconds: Таймаут в секундах

    Returns:
        Callable: Декорированная функция

    Примеры:
        >>> @timeout(10.0)
        ... async def slow_api_call(self):
        ...     # Ваш код здесь
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(self, *args, **kwargs), timeout=seconds
                )
            except asyncio.TimeoutError:
                method_name = f"{func.__name__}"
                error_msg = f"Timeout {seconds}s exceeded for {method_name}"
                self.logger.error(error_msg)
                raise ServiceUnavailableError(error_msg)

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
):
    """
    Декоратор для повторных попыток выполнения функции

    Args:
        max_attempts: Максимальное количество попыток
        backoff_factor: Коэффициент увеличения задержки
        max_delay: Максимальная задержка между попытками
        exceptions: Исключения, при которых делать повторные попытки

    Returns:
        Callable: Декорированная функция

    Примеры:
        >>> @retry(max_attempts=3, backoff_factor=1.5)
        ... async def unreliable_api_call(self):
        ...     # Ваш код здесь
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            method_name = f"{func.__name__}"
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(self, *args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = min(backoff_factor**attempt, max_delay)
                        self.logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {method_name}, "
                            f"retrying in {delay:.2f}s: {str(e)}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        self.logger.error(
                            f"All {max_attempts} attempts failed for {method_name}: {str(e)}"
                        )

            raise last_exception

        return wrapper

    return decorator


class TimestampMixin:
    """
    Миксин для работы с timestamp
    """

    @staticmethod
    def get_current_timestamp() -> str:
        """
        Получить текущий timestamp в формате ISO

        Returns:
            str: Текущий timestamp
        """
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def parse_timestamp(timestamp: Union[int, str]) -> datetime:
        """
        Парсить timestamp

        Args:
            timestamp: Timestamp для парсинга

        Returns:
            datetime: Объект datetime
        """
        if isinstance(timestamp, int):
            return datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        else:
            raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")


# Экспорт
__all__ = [
    "BaseVKAPIService",
    "validate_id",
    "validate_count",
    "cached",
    "log_request",
    "circuit_breaker",
    "rate_limit",
    "timeout",
    "retry",
    "CircuitBreakerState",
    "RateLimitStrategy",
    "CircuitBreakerConfig",
    "RateLimiterConfig",
    "CircuitBreakerStats",
    "RateLimiterStats",
    "TimestampMixin",
]
