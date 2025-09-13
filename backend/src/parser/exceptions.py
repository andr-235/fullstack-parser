"""
Исключения модуля Parser - упрощенная версия
"""

from common.exceptions import APIException, NotFoundException


class ParserError(APIException):
    """Общая ошибка парсера"""
    pass


class TaskNotFoundException(NotFoundException):
    """Задача не найдена"""
    pass


class ParsingException(APIException):
    """Ошибка парсинга"""
    pass


class VKAPILimitExceededException(APIException):
    """Превышен лимит VK API"""

    def __init__(self, retry_after: int = None):
        super().__init__(
            message="Превышен лимит запросов к VK API",
            status_code=429,
            details={"retry_after": retry_after} if retry_after else {}
        )


class GroupNotFoundException(NotFoundException):
    """Группа VK не найдена"""
    pass


__all__ = [
    "ParserError",
    "TaskNotFoundException",
    "ParsingException",
    "VKAPILimitExceededException",
    "GroupNotFoundException",
]
