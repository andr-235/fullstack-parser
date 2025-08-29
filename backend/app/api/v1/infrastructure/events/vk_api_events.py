"""
Domain Events для VK API операций (DDD Infrastructure Layer)

Конкретные реализации Domain Events для работы с VK API
в рамках DDD архитектуры.
"""

from typing import List, Optional, Dict, Any
from .domain_event_publisher import DomainEvent


class VKAPIRequestEvent(DomainEvent):
    """
    Событие выполнения запроса к VK API

    Генерируется при каждом запросе к VK API.
    """

    def __init__(
        self,
        method: str,
        parameters: Dict[str, Any],
        request_id: str,
        response_time: Optional[float] = None,
        success: bool = True,
        error_code: Optional[int] = None,
    ):
        """
        Args:
            method: Метод VK API
            parameters: Параметры запроса
            request_id: Уникальный ID запроса
            response_time: Время ответа в секундах
            success: Успешность запроса
            error_code: Код ошибки (если есть)
        """
        super().__init__(request_id)
        self.method = method
        self.parameters = parameters
        self.response_time = response_time
        self.success = success
        self.error_code = error_code

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "method": self.method,
            "parameters": self.parameters,
            "response_time": self.response_time,
            "success": self.success,
            "error_code": self.error_code,
        }


class VKAPIRateLimitEvent(DomainEvent):
    """
    Событие достижения rate limit VK API

    Генерируется при достижении лимита запросов.
    """

    def __init__(
        self,
        method: str,
        wait_time: float,
        request_count: int,
        limit_exceeded: bool = True,
    ):
        """
        Args:
            method: Метод, вызвавший ограничение
            wait_time: Время ожидания в секундах
            request_count: Количество выполненных запросов
            limit_exceeded: Превышен ли лимит
        """
        super().__init__("rate_limit")
        self.method = method
        self.wait_time = wait_time
        self.request_count = request_count
        self.limit_exceeded = limit_exceeded

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "method": self.method,
            "wait_time": self.wait_time,
            "request_count": self.request_count,
            "limit_exceeded": self.limit_exceeded,
        }


class VKAPITokenValidationEvent(DomainEvent):
    """
    Событие валидации токена VK API

    Генерируется при проверке валидности токена доступа.
    """

    def __init__(
        self,
        token_valid: bool,
        user_id: Optional[int] = None,
        permissions: Optional[List[str]] = None,
        validation_error: Optional[str] = None,
    ):
        """
        Args:
            token_valid: Валидность токена
            user_id: ID пользователя VK
            permissions: Список разрешений
            validation_error: Ошибка валидации (если есть)
        """
        super().__init__("token_validation")
        self.token_valid = token_valid
        self.user_id = user_id
        self.permissions = permissions or []
        self.validation_error = validation_error

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "token_valid": self.token_valid,
            "user_id": self.user_id,
            "permissions": self.permissions,
            "validation_error": self.validation_error,
        }


class VKAPIDataFetchedEvent(DomainEvent):
    """
    Событие получения данных из VK API

    Генерируется при успешном получении данных.
    """

    def __init__(
        self,
        data_type: str,
        object_id: Any,
        items_count: int,
        total_count: Optional[int] = None,
        fetch_time: Optional[float] = None,
        source: str = "api",
    ):
        """
        Args:
            data_type: Тип данных (posts, comments, groups, users)
            object_id: ID объекта (group_id, post_id, etc.)
            items_count: Количество полученных элементов
            total_count: Общее количество доступных элементов
            fetch_time: Время получения данных
            source: Источник данных (api, cache)
        """
        super().__init__(object_id)
        self.data_type = data_type
        self.object_id = object_id
        self.items_count = items_count
        self.total_count = total_count
        self.fetch_time = fetch_time
        self.source = source

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "data_type": self.data_type,
            "object_id": self.object_id,
            "items_count": self.items_count,
            "total_count": self.total_count,
            "fetch_time": self.fetch_time,
            "source": self.source,
        }


class VKAPIBulkOperationEvent(DomainEvent):
    """
    Событие массовой операции с VK API

    Генерируется при выполнении операций над множественными объектами.
    """

    def __init__(
        self,
        operation_type: str,
        target_type: str,
        object_ids: List[Any],
        success_count: int,
        failure_count: int,
        total_time: Optional[float] = None,
        errors: Optional[List[str]] = None,
    ):
        """
        Args:
            operation_type: Тип операции (fetch, process, validate)
            target_type: Тип объектов (posts, comments, groups)
            object_ids: Список ID объектов
            success_count: Количество успешных операций
            failure_count: Количество неудачных операций
            total_time: Общее время выполнения
            errors: Список ошибок
        """
        super().__init__(object_ids[0] if object_ids else "bulk_operation")
        self.operation_type = operation_type
        self.target_type = target_type
        self.object_ids = object_ids
        self.success_count = success_count
        self.failure_count = failure_count
        self.total_time = total_time
        self.errors = errors or []
        self.total_count = len(object_ids)

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "operation_type": self.operation_type,
            "target_type": self.target_type,
            "object_ids": self.object_ids,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_time": self.total_time,
            "errors": self.errors,
            "total_count": self.total_count,
        }


class VKAPIErrorEvent(DomainEvent):
    """
    Событие ошибки VK API

    Генерируется при получении ошибки от VK API.
    """

    def __init__(
        self,
        method: str,
        error_code: int,
        error_message: str,
        request_params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        should_retry: bool = False,
    ):
        """
        Args:
            method: Метод VK API, вызвавший ошибку
            error_code: Код ошибки VK API
            error_message: Сообщение об ошибке
            request_params: Параметры запроса
            retry_count: Количество попыток
            should_retry: Нужно ли повторять запрос
        """
        super().__init__(f"vk_error_{error_code}")
        self.method = method
        self.error_code = error_code
        self.error_message = error_message
        self.request_params = request_params or {}
        self.retry_count = retry_count
        self.should_retry = should_retry

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "method": self.method,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "request_params": self.request_params,
            "retry_count": self.retry_count,
            "should_retry": self.should_retry,
        }


class VKAPICacheHitEvent(DomainEvent):
    """
    Событие попадания в кеш VK API

    Генерируется при получении данных из кеша вместо API.
    """

    def __init__(
        self,
        cache_key: str,
        data_type: str,
        cache_age: int,
        saved_requests: int = 1,
    ):
        """
        Args:
            cache_key: Ключ кеша
            data_type: Тип данных
            cache_age: Возраст кеша в секундах
            saved_requests: Количество сэкономленных запросов
        """
        super().__init__(cache_key)
        self.cache_key = cache_key
        self.data_type = data_type
        self.cache_age = cache_age
        self.saved_requests = saved_requests

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "cache_key": self.cache_key,
            "data_type": self.data_type,
            "cache_age": self.cache_age,
            "saved_requests": self.saved_requests,
        }


# Вспомогательные функции для создания событий


def create_vk_api_request_event(
    method: str,
    parameters: Dict[str, Any],
    success: bool = True,
    response_time: Optional[float] = None,
) -> VKAPIRequestEvent:
    """
    Создать событие запроса к VK API

    Args:
        method: Метод VK API
        parameters: Параметры запроса
        success: Успешность запроса
        response_time: Время ответа

    Returns:
        VKAPIRequestEvent
    """
    return VKAPIRequestEvent(
        method=method,
        parameters=parameters,
        request_id=f"vk_req_{method}",
        success=success,
        response_time=response_time,
    )


def create_vk_api_rate_limit_event(
    method: str,
    wait_time: float,
    request_count: int,
) -> VKAPIRateLimitEvent:
    """
    Создать событие rate limit

    Args:
        method: Метод VK API
        wait_time: Время ожидания
        request_count: Количество запросов

    Returns:
        VKAPIRateLimitEvent
    """
    return VKAPIRateLimitEvent(
        method=method,
        wait_time=wait_time,
        request_count=request_count,
    )


def create_vk_api_data_fetched_event(
    data_type: str,
    object_id: Any,
    items_count: int,
    fetch_time: Optional[float] = None,
) -> VKAPIDataFetchedEvent:
    """
    Создать событие получения данных

    Args:
        data_type: Тип данных
        object_id: ID объекта
        items_count: Количество элементов
        fetch_time: Время получения

    Returns:
        VKAPIDataFetchedEvent
    """
    return VKAPIDataFetchedEvent(
        data_type=data_type,
        object_id=object_id,
        items_count=items_count,
        fetch_time=fetch_time,
    )


def create_vk_api_error_event(
    method: str,
    error_code: int,
    error_message: str,
    request_params: Optional[Dict[str, Any]] = None,
) -> VKAPIErrorEvent:
    """
    Создать событие ошибки VK API

    Args:
        method: Метод VK API
        error_code: Код ошибки
        error_message: Сообщение об ошибке
        request_params: Параметры запроса

    Returns:
        VKAPIErrorEvent
    """
    return VKAPIErrorEvent(
        method=method,
        error_code=error_code,
        error_message=error_message,
        request_params=request_params,
    )
