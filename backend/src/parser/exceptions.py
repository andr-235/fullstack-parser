"""
Исключения модуля Parser

Содержит специфические исключения для модуля парсера
"""

from shared.presentation.exceptions import APIException as APIError


class TaskNotFoundException(APIError):
    """Задача не найдена"""

    def __init__(self, task_id: str):
        super().__init__(
            status_code=404,
            error_code="TASK_NOT_FOUND",
            message=f"Задача с ID {task_id} не найдена",
            details={"task_id": task_id},
        )


class InvalidTaskDataException(APIError):
    """Неверные данные задачи"""

    def __init__(self, field: str, value: str = None):
        detail = f"Неверное значение поля '{field}'"
        if value:
            detail += f": {value}"

        super().__init__(
            status_code=422,
            error_code="INVALID_TASK_DATA",
            message=detail,
            details={"field": field, "value": value},
            field=field,
        )


class ParsingException(APIError):
    """Ошибка парсинга"""

    def __init__(self, message: str, group_id: int = None):
        detail = f"Ошибка парсинга: {message}"
        extra_data = {"message": message}
        if group_id:
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=500,
            error_code="PARSING_ERROR",
            message=detail,
            details=extra_data,
        )


class VKAPILimitExceededException(APIError):
    """Превышен лимит VK API"""

    def __init__(self, retry_after: int = None):
        extra_data = {}
        if retry_after:
            extra_data["retry_after"] = retry_after

        super().__init__(
            status_code=429,
            error_code="VK_API_LIMIT_EXCEEDED",
            message="Превышен лимит запросов к VK API",
            details=extra_data,
        )


class VKAPITimeoutException(APIError):
    """Таймаут VK API"""

    def __init__(self, timeout: int = None):
        extra_data = {}
        if timeout:
            extra_data["timeout"] = timeout

        super().__init__(
            status_code=504,
            error_code="VK_API_TIMEOUT",
            message="Превышено время ожидания ответа от VK API",
            details=extra_data,
        )


class ParserServiceUnavailableException(APIError):
    """Сервис парсера недоступен"""

    def __init__(self, service_name: str = "parser"):
        super().__init__(
            status_code=503,
            error_code="PARSER_SERVICE_UNAVAILABLE",
            message=f"Сервис {service_name} временно недоступен",
            details={"service": service_name},
        )


class TaskAlreadyRunningException(APIError):
    """Задача уже выполняется"""

    def __init__(self, task_id: str):
        super().__init__(
            status_code=409,
            error_code="TASK_ALREADY_RUNNING",
            message=f"Задача {task_id} уже выполняется",
            details={"task_id": task_id},
        )


class TaskQueueFullException(APIError):
    """Очередь задач переполнена"""

    def __init__(self, queue_size: int):
        super().__init__(
            status_code=503,
            error_code="TASK_QUEUE_FULL",
            message="Очередь задач переполнена",
            details={"queue_size": queue_size},
        )


class InvalidGroupIdException(APIError):
    """Неверный ID группы VK"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=422,
            error_code="INVALID_GROUP_ID",
            message=f"Неверный ID группы VK: {group_id}",
            details={"group_id": group_id},
        )


class GroupNotFoundException(APIError):
    """Группа VK не найдена"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=404,
            error_code="GROUP_NOT_FOUND",
            message=f"Группа VK с ID {group_id} не найдена",
            details={"group_id": group_id},
        )


class PostNotFoundException(APIError):
    """Пост VK не найден"""

    def __init__(self, post_id: str):
        super().__init__(
            status_code=404,
            error_code="POST_NOT_FOUND",
            message=f"Пост VK с ID {post_id} не найден",
            details={"post_id": post_id},
        )


class ParserConfigurationException(APIError):
    """Ошибка конфигурации парсера"""

    def __init__(self, config_key: str, message: str):
        super().__init__(
            status_code=500,
            error_code="PARSER_CONFIGURATION_ERROR",
            message=f"Ошибка конфигурации парсера: {message}",
            details={"config_key": config_key, "message": message},
        )


class ParserTimeoutException(APIError):
    """Превышено время выполнения парсера"""

    def __init__(self, timeout: int, task_id: str = None):
        extra_data = {"timeout": timeout}
        if task_id:
            extra_data["task_id"] = task_id

        super().__init__(
            status_code=504,
            error_code="PARSER_TIMEOUT",
            message="Превышено время выполнения задачи парсинга",
            details=extra_data,
        )


class ParserResourceLimitException(APIError):
    """Превышен лимит ресурсов парсера"""

    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            status_code=507,
            error_code="PARSER_RESOURCE_LIMIT",
            message=f"Превышен лимит ресурса '{resource}': {current}/{limit}",
            details={
                "resource": resource,
                "limit": limit,
                "current": current,
            },
        )


class ParserDataValidationException(APIError):
    """Ошибка валидации данных парсера"""

    def __init__(self, data_type: str, errors: list):
        super().__init__(
            status_code=422,
            error_code="PARSER_DATA_VALIDATION_ERROR",
            message=f"Ошибка валидации данных типа '{data_type}'",
            details={"data_type": data_type, "validation_errors": errors},
        )


class ParserExternalServiceException(APIError):
    """Ошибка внешнего сервиса"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            status_code=502,
            error_code="PARSER_EXTERNAL_SERVICE_ERROR",
            message=f"Ошибка внешнего сервиса '{service_name}': {error_message}",
            details={
                "service": service_name,
                "error_message": error_message,
            },
        )


# Экспорт всех исключений
__all__ = [
    "TaskNotFoundException",
    "InvalidTaskDataException",
    "ParsingException",
    "VKAPILimitExceededException",
    "VKAPITimeoutException",
    "ParserServiceUnavailableException",
    "TaskAlreadyRunningException",
    "TaskQueueFullException",
    "InvalidGroupIdException",
    "GroupNotFoundException",
    "PostNotFoundException",
    "ParserConfigurationException",
    "ParserTimeoutException",
    "ParserResourceLimitException",
    "ParserDataValidationException",
    "ParserExternalServiceException",
]
