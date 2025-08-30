"""
Исключения модуля Parser

Содержит специфические исключения для модуля парсера
"""

from ..exceptions import APIException


class TaskNotFoundException(APIException):
    """Задача не найдена"""

    def __init__(self, task_id: str):
        super().__init__(
            status_code=404,
            detail=f"Задача с ID {task_id} не найдена",
            error_code="TASK_NOT_FOUND",
            extra_data={"task_id": task_id},
        )


class InvalidTaskDataException(APIException):
    """Неверные данные задачи"""

    def __init__(self, field: str, value: str = None):
        detail = f"Неверное значение поля '{field}'"
        if value:
            detail += f": {value}"

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_TASK_DATA",
            extra_data={"field": field, "value": value},
        )


class ParsingException(APIException):
    """Ошибка парсинга"""

    def __init__(self, message: str, group_id: int = None):
        detail = f"Ошибка парсинга: {message}"
        extra_data = {"message": message}
        if group_id:
            extra_data["group_id"] = group_id

        super().__init__(
            status_code=500,
            detail=detail,
            error_code="PARSING_ERROR",
            extra_data=extra_data,
        )


class VKAPILimitExceededException(APIException):
    """Превышен лимит VK API"""

    def __init__(self, retry_after: int = None):
        extra_data = {}
        if retry_after:
            extra_data["retry_after"] = retry_after

        super().__init__(
            status_code=429,
            detail="Превышен лимит запросов к VK API",
            error_code="VK_API_LIMIT_EXCEEDED",
            extra_data=extra_data,
        )


class VKAPITimeoutException(APIException):
    """Таймаут VK API"""

    def __init__(self, timeout: int = None):
        extra_data = {}
        if timeout:
            extra_data["timeout"] = timeout

        super().__init__(
            status_code=504,
            detail="Превышено время ожидания ответа от VK API",
            error_code="VK_API_TIMEOUT",
            extra_data=extra_data,
        )


class ParserServiceUnavailableException(APIException):
    """Сервис парсера недоступен"""

    def __init__(self, service_name: str = "parser"):
        super().__init__(
            status_code=503,
            detail=f"Сервис {service_name} временно недоступен",
            error_code="PARSER_SERVICE_UNAVAILABLE",
            extra_data={"service": service_name},
        )


class TaskAlreadyRunningException(APIException):
    """Задача уже выполняется"""

    def __init__(self, task_id: str):
        super().__init__(
            status_code=409,
            detail=f"Задача {task_id} уже выполняется",
            error_code="TASK_ALREADY_RUNNING",
            extra_data={"task_id": task_id},
        )


class TaskQueueFullException(APIException):
    """Очередь задач переполнена"""

    def __init__(self, queue_size: int):
        super().__init__(
            status_code=503,
            detail="Очередь задач переполнена",
            error_code="TASK_QUEUE_FULL",
            extra_data={"queue_size": queue_size},
        )


class InvalidGroupIdException(APIException):
    """Неверный ID группы VK"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=422,
            detail=f"Неверный ID группы VK: {group_id}",
            error_code="INVALID_GROUP_ID",
            extra_data={"group_id": group_id},
        )


class GroupNotFoundException(APIException):
    """Группа VK не найдена"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=404,
            detail=f"Группа VK с ID {group_id} не найдена",
            error_code="GROUP_NOT_FOUND",
            extra_data={"group_id": group_id},
        )


class PostNotFoundException(APIException):
    """Пост VK не найден"""

    def __init__(self, post_id: str):
        super().__init__(
            status_code=404,
            detail=f"Пост VK с ID {post_id} не найден",
            error_code="POST_NOT_FOUND",
            extra_data={"post_id": post_id},
        )


class ParserConfigurationException(APIException):
    """Ошибка конфигурации парсера"""

    def __init__(self, config_key: str, message: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка конфигурации парсера: {message}",
            error_code="PARSER_CONFIGURATION_ERROR",
            extra_data={"config_key": config_key, "message": message},
        )


class ParserTimeoutException(APIException):
    """Превышено время выполнения парсера"""

    def __init__(self, timeout: int, task_id: str = None):
        extra_data = {"timeout": timeout}
        if task_id:
            extra_data["task_id"] = task_id

        super().__init__(
            status_code=504,
            detail="Превышено время выполнения задачи парсинга",
            error_code="PARSER_TIMEOUT",
            extra_data=extra_data,
        )


class ParserResourceLimitException(APIException):
    """Превышен лимит ресурсов парсера"""

    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            status_code=507,
            detail=f"Превышен лимит ресурса '{resource}': {current}/{limit}",
            error_code="PARSER_RESOURCE_LIMIT",
            extra_data={
                "resource": resource,
                "limit": limit,
                "current": current,
            },
        )


class ParserDataValidationException(APIException):
    """Ошибка валидации данных парсера"""

    def __init__(self, data_type: str, errors: list):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации данных типа '{data_type}'",
            error_code="PARSER_DATA_VALIDATION_ERROR",
            extra_data={"data_type": data_type, "validation_errors": errors},
        )


class ParserExternalServiceException(APIException):
    """Ошибка внешнего сервиса"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            status_code=502,
            detail=f"Ошибка внешнего сервиса '{service_name}': {error_message}",
            error_code="PARSER_EXTERNAL_SERVICE_ERROR",
            extra_data={
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
