"""
Исключения модуля Groups

Содержит специфические исключения для модуля групп
"""

from ..exceptions import APIException


class GroupNotFoundException(APIException):
    """Группа не найдена"""

    def __init__(self, group_id: int):
        super().__init__(
            status_code=404,
            detail=f"Группа с ID {group_id} не найдена",
            error_code="GROUP_NOT_FOUND",
            extra_data={"group_id": group_id}
        )


class GroupAlreadyExistsException(APIException):
    """Группа уже существует"""

    def __init__(self, vk_id: int = None, screen_name: str = None):
        if vk_id:
            detail = f"Группа с VK ID {vk_id} уже существует"
            extra_data = {"vk_id": vk_id}
        elif screen_name:
            detail = f"Группа с screen_name @{screen_name} уже существует"
            extra_data = {"screen_name": screen_name}
        else:
            detail = "Группа уже существует"
            extra_data = {}

        super().__init__(
            status_code=409,
            detail=detail,
            error_code="GROUP_ALREADY_EXISTS",
            extra_data=extra_data
        )


class InvalidGroupDataException(APIException):
    """Неверные данные группы"""

    def __init__(self, field: str, value: str = None):
        detail = f"Неверное значение поля '{field}'"
        if value:
            detail += f": {value}"

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_GROUP_DATA",
            extra_data={"field": field, "value": value}
        )


class GroupSearchException(APIException):
    """Ошибка поиска групп"""

    def __init__(self, query: str):
        super().__init__(
            status_code=400,
            detail=f"Ошибка поиска по запросу: {query}",
            error_code="GROUP_SEARCH_ERROR",
            extra_data={"query": query}
        )


class GroupBulkOperationException(APIException):
    """Ошибка массовой операции с группами"""

    def __init__(self, operation: str, failed_count: int = 0):
        super().__init__(
            status_code=400,
            detail=f"Ошибка массовой операции '{operation}'",
            error_code="GROUP_BULK_OPERATION_ERROR",
            extra_data={
                "operation": operation,
                "failed_count": failed_count
            }
        )


class GroupValidationException(APIException):
    """Ошибка валидации группы"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации поля '{field}': {reason}",
            error_code="GROUP_VALIDATION_ERROR",
            extra_data={"field": field, "reason": reason}
        )


class GroupPermissionException(APIException):
    """Ошибка доступа к группе"""

    def __init__(self, group_id: int, reason: str = "Недостаточно прав"):
        super().__init__(
            status_code=403,
            detail=f"Доступ к группе {group_id} запрещен: {reason}",
            error_code="GROUP_PERMISSION_ERROR",
            extra_data={"group_id": group_id, "reason": reason}
        )


class GroupServiceUnavailableException(APIException):
    """Сервис групп недоступен"""

    def __init__(self, service_name: str = "groups"):
        super().__init__(
            status_code=503,
            detail=f"Сервис {service_name} временно недоступен",
            error_code="GROUP_SERVICE_UNAVAILABLE",
            extra_data={"service": service_name}
        )


class VKAPIError(APIException):
    """Ошибка VK API"""

    def __init__(
        self,
        detail: str = "Ошибка VK API",
        error_code: str = "VK_API_ERROR",
    ):
        super().__init__(
            status_code=502,
            detail=detail,
            error_code=error_code,
        )


class GroupMonitoringException(APIException):
    """Ошибка мониторинга группы"""

    def __init__(self, group_id: int, reason: str):
        super().__init__(
            status_code=400,
            detail=f"Ошибка мониторинга группы {group_id}: {reason}",
            error_code="GROUP_MONITORING_ERROR",
            extra_data={"group_id": group_id, "reason": reason}
        )


# Экспорт всех исключений
__all__ = [
    "GroupNotFoundException",
    "GroupAlreadyExistsException",
    "InvalidGroupDataException",
    "GroupSearchException",
    "GroupBulkOperationException",
    "GroupValidationException",
    "GroupPermissionException",
    "GroupServiceUnavailableException",
    "VKAPIError",
    "GroupMonitoringException",
]
