"""
Сервис для создания отчетов об ошибках
"""

import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.error_report import (
    ErrorContext,
    ErrorEntry,
    ErrorReport,
    ErrorSeverity,
    ErrorType,
    GroupLoadErrorReport,
)

logger = structlog.get_logger(__name__)


class ErrorReportingService:
    """Сервис для создания и управления отчетами об ошибках"""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)

    def create_error_entry(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        message: str,
        details: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        exception: Optional[Exception] = None,
    ) -> ErrorEntry:
        """
        Создает запись об ошибке

        Args:
            error_type: Тип ошибки
            severity: Уровень серьезности
            message: Сообщение об ошибке
            details: Детали ошибки
            context: Контекст ошибки
            exception: Исключение (если есть)

        Returns:
            Запись об ошибке
        """
        stack_trace = None
        if exception:
            stack_trace = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )

        return ErrorEntry(
            timestamp=datetime.utcnow(),
            error_type=error_type,
            severity=severity,
            message=message,
            details=details,
            context=context,
            stack_trace=stack_trace,
        )

    def create_error_report(
        self,
        operation: str,
        errors: List[ErrorEntry],
        recommendations: Optional[List[str]] = None,
    ) -> ErrorReport:
        """
        Создает отчет об ошибках

        Args:
            operation: Операция, при которой произошли ошибки
            errors: Список ошибок
            recommendations: Рекомендации по исправлению

        Returns:
            Отчет об ошибках
        """
        # Подсчитываем статистику по типам ошибок
        summary = {}
        for error in errors:
            error_type = error.error_type.value
            summary[error_type] = summary.get(error_type, 0) + 1

        # Генерируем рекомендации на основе ошибок
        auto_recommendations = self._generate_recommendations(errors)
        all_recommendations = (recommendations or []) + auto_recommendations

        return ErrorReport(
            report_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            operation=operation,
            total_errors=len(errors),
            errors=errors,
            summary=summary,
            recommendations=all_recommendations,
        )

    def create_group_load_error_report(
        self,
        errors: List[ErrorEntry],
        groups_processed: int,
        groups_successful: int,
        groups_failed: int,
        groups_skipped: int,
        processing_time_seconds: float,
        recommendations: Optional[List[str]] = None,
    ) -> GroupLoadErrorReport:
        """
        Создает специализированный отчет для ошибок загрузки групп

        Args:
            errors: Список ошибок
            groups_processed: Количество обработанных групп
            groups_successful: Количество успешно загруженных групп
            groups_failed: Количество групп с ошибками
            groups_skipped: Количество пропущенных групп
            processing_time_seconds: Время обработки в секундах
            recommendations: Рекомендации по исправлению

        Returns:
            Отчет об ошибках загрузки групп
        """
        base_report = self.create_error_report(
            operation="group_loading",
            errors=errors,
            recommendations=recommendations,
        )

        return GroupLoadErrorReport(
            **base_report.model_dump(),
            groups_processed=groups_processed,
            groups_successful=groups_successful,
            groups_failed=groups_failed,
            groups_skipped=groups_skipped,
            processing_time_seconds=processing_time_seconds,
        )

    def _generate_recommendations(self, errors: List[ErrorEntry]) -> List[str]:
        """
        Генерирует автоматические рекомендации на основе ошибок

        Args:
            errors: Список ошибок

        Returns:
            Список рекомендаций
        """
        recommendations = []
        error_types = {error.error_type for error in errors}

        if ErrorType.DATABASE in error_types:
            recommendations.append(
                "Проверьте подключение к базе данных и целостность данных"
            )

        if ErrorType.API in error_types:
            recommendations.append(
                "Проверьте доступность VK API и корректность токена"
            )

        if ErrorType.RATE_LIMIT in error_types:
            recommendations.append(
                "Снизьте частоту запросов к VK API или увеличьте интервалы между запросами"
            )

        if ErrorType.VALIDATION in error_types:
            recommendations.append(
                "Проверьте корректность входных данных и их формат"
            )

        if ErrorType.NETWORK in error_types:
            recommendations.append(
                "Проверьте сетевое подключение и доступность внешних сервисов"
            )

        if ErrorType.AUTHENTICATION in error_types:
            recommendations.append(
                "Проверьте корректность токена VK API и его права доступа"
            )

        # Добавляем общие рекомендации
        if len(errors) > 5:
            recommendations.append(
                "Большое количество ошибок может указывать на системные проблемы. "
                "Рекомендуется проверить логи сервера."
            )

        return recommendations

    def log_error_report(self, report: ErrorReport) -> None:
        """
        Логирует отчет об ошибках

        Args:
            report: Отчет об ошибках
        """
        self.logger.error(
            "Error report generated",
            report_id=report.report_id,
            operation=report.operation,
            total_errors=report.total_errors,
            summary=report.summary,
            recommendations=report.recommendations,
        )

        # Логируем каждую ошибку отдельно
        for error in report.errors:
            self.logger.error(
                "Error in report",
                report_id=report.report_id,
                error_type=error.error_type.value,
                severity=error.severity.value,
                message=error.message,
                details=error.details,
                context=error.context.model_dump() if error.context else None,
            )


# Глобальный экземпляр сервиса
error_reporting_service = ErrorReportingService()
