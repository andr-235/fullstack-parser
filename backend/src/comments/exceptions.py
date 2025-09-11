"""
Исключения для модуля Comments

Определяет специфичные исключения для работы с комментариями
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class CommentError(Exception):
    """Базовое исключение для модуля комментариев"""

    def __init__(
        self, message: str, code: str = None, details: Dict[str, Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class CommentNotFoundError(CommentError):
    """Исключение когда комментарий не найден"""

    def __init__(self, comment_id: int, message: str = None):
        self.comment_id = comment_id
        super().__init__(
            message or f"Комментарий с ID {comment_id} не найден",
            code="COMMENT_NOT_FOUND",
            details={"comment_id": comment_id},
        )


class CommentValidationError(CommentError):
    """Исключение при ошибке валидации комментария"""

    def __init__(
        self, message: str, field: str = None, details: Dict[str, Any] = None
    ):
        self.field = field
        super().__init__(
            message,
            code="COMMENT_VALIDATION_ERROR",
            details={**(details or {}), "field": field},
        )


class CommentDuplicateError(CommentError):
    """Исключение при попытке создать дубликат комментария"""

    def __init__(self, vk_id: str, message: str = None):
        self.vk_id = vk_id
        super().__init__(
            message or f"Комментарий с VK ID {vk_id} уже существует",
            code="COMMENT_DUPLICATE",
            details={"vk_id": vk_id},
        )


class CommentPermissionError(CommentError):
    """Исключение при недостатке прав для операции с комментарием"""

    def __init__(self, operation: str, message: str = None):
        self.operation = operation
        super().__init__(
            message or f"Недостаточно прав для операции: {operation}",
            code="COMMENT_PERMISSION_ERROR",
            details={"operation": operation},
        )


class CommentServiceError(CommentError):
    """Исключение при ошибке сервиса комментариев"""

    def __init__(
        self, service: str, message: str, details: Dict[str, Any] = None
    ):
        self.service = service
        super().__init__(
            message,
            code="COMMENT_SERVICE_ERROR",
            details={**(details or {}), "service": service},
        )


def handle_comment_error(error: CommentError) -> HTTPException:
    """Преобразовать CommentError в HTTPException"""

    status_code_map = {
        "COMMENT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "COMMENT_VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "COMMENT_DUPLICATE": status.HTTP_409_CONFLICT,
        "COMMENT_PERMISSION_ERROR": status.HTTP_403_FORBIDDEN,
        "COMMENT_SERVICE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(
        error.code, status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    return HTTPException(
        status_code=status_code,
        detail={
            "message": error.message,
            "code": error.code,
            "details": error.details,
        },
    )


def handle_validation_error(
    error: Exception, field: str = None
) -> HTTPException:
    """Обработать ошибку валидации"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": str(error),
            "code": "VALIDATION_ERROR",
            "details": {"field": field} if field else {},
        },
    )


def handle_not_found_error(resource: str, resource_id: Any) -> HTTPException:
    """Обработать ошибку "не найдено" """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": f"{resource} с ID {resource_id} не найден",
            "code": "NOT_FOUND",
            "details": {"resource": resource, "resource_id": resource_id},
        },
    )


def handle_internal_error(
    error: Exception, operation: str = None
) -> HTTPException:
    """Обработать внутреннюю ошибку"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": f"Внутренняя ошибка сервера{f' при {operation}' if operation else ''}",
            "code": "INTERNAL_ERROR",
            "details": {"operation": operation} if operation else {},
        },
    )


# Экспорт исключений
__all__ = [
    "CommentError",
    "CommentNotFoundError",
    "CommentValidationError",
    "CommentDuplicateError",
    "CommentPermissionError",
    "CommentServiceError",
    "handle_comment_error",
    "handle_validation_error",
    "handle_not_found_error",
    "handle_internal_error",
]
