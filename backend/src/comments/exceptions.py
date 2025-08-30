"""
Исключения модуля Comments

Содержит специфические исключения для модуля комментариев
"""

from ..exceptions import APIException


class CommentNotFoundException(APIException):
    """Комментарий не найден"""

    def __init__(self, comment_id: int):
        super().__init__(
            status_code=404,
            detail=f"Комментарий с ID {comment_id} не найден",
            error_code="COMMENT_NOT_FOUND",
            extra_data={"comment_id": comment_id},
        )


class CommentAlreadyExistsException(APIException):
    """Комментарий уже существует"""

    def __init__(self, vk_comment_id: str):
        super().__init__(
            status_code=409,
            detail=f"Комментарий с VK ID {vk_comment_id} уже существует",
            error_code="COMMENT_ALREADY_EXISTS",
            extra_data={"vk_comment_id": vk_comment_id},
        )


class InvalidCommentDataException(APIException):
    """Неверные данные комментария"""

    def __init__(self, field: str, value: str = None):
        detail = f"Неверное значение поля '{field}'"
        if value:
            detail += f": {value}"

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_COMMENT_DATA",
            extra_data={"field": field, "value": value},
        )


class CommentSearchException(APIException):
    """Ошибка поиска комментариев"""

    def __init__(self, query: str):
        super().__init__(
            status_code=400,
            detail=f"Ошибка поиска по запросу: {query}",
            error_code="COMMENT_SEARCH_ERROR",
            extra_data={"query": query},
        )


class CommentBulkOperationException(APIException):
    """Ошибка массовой операции с комментариями"""

    def __init__(self, operation: str, failed_count: int = 0):
        super().__init__(
            status_code=400,
            detail=f"Ошибка массовой операции '{operation}'",
            error_code="COMMENT_BULK_OPERATION_ERROR",
            extra_data={"operation": operation, "failed_count": failed_count},
        )


class CommentValidationException(APIException):
    """Ошибка валидации комментария"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации поля '{field}': {reason}",
            error_code="COMMENT_VALIDATION_ERROR",
            extra_data={"field": field, "reason": reason},
        )


class CommentPermissionException(APIException):
    """Ошибка доступа к комментарию"""

    def __init__(self, comment_id: int, reason: str = "Недостаточно прав"):
        super().__init__(
            status_code=403,
            detail=f"Доступ к комментарию {comment_id} запрещен: {reason}",
            error_code="COMMENT_PERMISSION_ERROR",
            extra_data={"comment_id": comment_id, "reason": reason},
        )


class CommentServiceUnavailableException(APIException):
    """Сервис комментариев недоступен"""

    def __init__(self, service_name: str = "comments"):
        super().__init__(
            status_code=503,
            detail=f"Сервис {service_name} временно недоступен",
            error_code="COMMENT_SERVICE_UNAVAILABLE",
            extra_data={"service": service_name},
        )


# Экспорт всех исключений
__all__ = [
    "CommentNotFoundException",
    "CommentAlreadyExistsException",
    "InvalidCommentDataException",
    "CommentSearchException",
    "CommentBulkOperationException",
    "CommentValidationException",
    "CommentPermissionException",
    "CommentServiceUnavailableException",
]
