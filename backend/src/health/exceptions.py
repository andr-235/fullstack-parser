"""
Исключения модуля Health
"""

from shared.presentation.exceptions import APIException


class HealthError(APIException):
    """Общая ошибка модуля Health"""
    
    def __init__(self, message: str, error_code: str = "HEALTH_ERROR"):
        super().__init__(
            status_code=500,
            detail=message,
            error_code=error_code,
        )


class HealthCheckFailedError(APIException):
    """Ошибка выполнения проверки здоровья"""
    
    def __init__(self, component: str, message: str = "Health check failed"):
        super().__init__(
            status_code=503,
            detail=f"{message}: {component}",
            error_code="HEALTH_CHECK_FAILED",
            extra_data={"component": component},
        )


class HealthComponentNotFoundError(APIException):
    """Компонент здоровья не найден"""
    
    def __init__(self, component: str):
        super().__init__(
            status_code=404,
            detail=f"Health component not found: {component}",
            error_code="HEALTH_COMPONENT_NOT_FOUND",
            extra_data={"component": component},
        )


class HealthCheckTimeoutError(APIException):
    """Превышено время ожидания проверки здоровья"""
    
    def __init__(self, component: str, timeout: float):
        super().__init__(
            status_code=504,
            detail=f"Health check timeout for {component}: {timeout}s",
            error_code="HEALTH_CHECK_TIMEOUT",
            extra_data={"component": component, "timeout": timeout},
        )


__all__ = [
    "HealthError",
    "HealthCheckFailedError", 
    "HealthComponentNotFoundError",
    "HealthCheckTimeoutError",
]
