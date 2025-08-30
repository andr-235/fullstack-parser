"""
Зависимости для модуля Error Reporting

Определяет FastAPI зависимости для работы с отчетами об ошибках
"""

from fastapi import Depends

from .service import ErrorReportingService
from .models import get_error_report_repository


async def get_error_reporting_service() -> ErrorReportingService:
    """
    Получить сервис отчетов об ошибках

    Returns:
        ErrorReportingService: Сервис отчетов об ошибках
    """
    repository = await get_error_report_repository()
    return ErrorReportingService(repository)


# Экспорт зависимостей
__all__ = [
    "get_error_reporting_service",
]
