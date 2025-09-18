"""
Исключения модуля Groups
"""

from common.exceptions import (
    APIException,
    NotFoundError,
    ValidationError,
)


class GroupError(APIException):
    """Общая ошибка модуля Groups"""

    def __init__(self, message: str, status_code: int = 500):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            status_code: HTTP код статуса.
        """
        super().__init__(message, status_code)


class GroupNotFoundError(NotFoundError):
    """Группа не найдена"""

    def __init__(self, message: str = "Группа не найдена"):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
        """
        super().__init__(message)


class GroupValidationError(ValidationError):
    """Ошибка валидации данных группы"""

    def __init__(self, message: str):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
        """
        super().__init__(message)


class GroupAlreadyExistsError(GroupValidationError):
    """Группа с такими данными уже существует"""

    def __init__(self, message: str = "Группа с такими данными уже существует"):
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
        """
        super().__init__(message)


__all__ = [
    "GroupError",
    "GroupNotFoundError",
    "GroupValidationError",
    "GroupAlreadyExistsError",
]