"""
Исключения модуля Health - упрощенная версия
"""

from common.exceptions import APIException, NotFoundError


class HealthError(APIException):
    """Общая ошибка модуля Health"""
    pass


class HealthCheckFailedError(APIException):
    """Ошибка выполнения проверки здоровья"""

    def __init__(self, component: str, message: str = "Health check failed"):
        super().__init__(
            message=f"{message}: {component}",
            status_code=503,
            details={"component": component},
        )


class HealthComponentNotFoundError(NotFoundError):
    """Компонент здоровья не найден"""
    pass


__all__ = [
    "HealthError",
    "HealthCheckFailedError",
    "HealthComponentNotFoundError",
]
