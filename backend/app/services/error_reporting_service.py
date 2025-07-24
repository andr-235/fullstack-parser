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
from app.services.error_report_db_service import ErrorReportDBService

logger = structlog.get_logger(__name__)


class ErrorReportingService:
    """Сервис для создания и управления отчетами об ошибках"""

    def __init__(self, db: Optional[AsyncSession] = None):
        self.logger = structlog.get_logger(__name__)
        self.db = db
        self._error_db_service = None

    @property
    def error_db_service(self) -> Optional[ErrorReportDBService]:
        """Получает сервис для работы с базой данных"""
        if self.db and not self._error_db_service:
            self._error_db_service = ErrorReportDBService(self.db)
        return self._error_db_service

    def set_db(self, db: AsyncSession) -> None:
        """Устанавливает сессию базы данных"""
        self.db = db
        self._error_db_service = None

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

        report = ErrorReport(
            report_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            operation=operation,
            total_errors=len(errors),
            errors=errors,
            summary=summary,
            recommendations=all_recommendations,
        )

        # Сохраняем в базу данных, если доступна
        if self.error_db_service:
            self._save_report_to_db(report)

        return report

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

        report = GroupLoadErrorReport(
            **base_report.model_dump(),
            groups_processed=groups_processed,
            groups_successful=groups_successful,
            groups_failed=groups_failed,
            groups_skipped=groups_skipped,
            processing_time_seconds=processing_time_seconds,
        )

        # Сохраняем в базу данных, если доступна
        if self.error_db_service:
            self._save_group_report_to_db(report)

        return report

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

    async def _save_report_to_db(self, report: ErrorReport) -> None:
        """Сохраняет отчет в базу данных"""
        if not self.error_db_service:
            return

        try:
            # Создаем отчет в базе данных
            db_report = await self.error_db_service.create_error_report(
                report_id=report.report_id,
                operation=report.operation,
                total_errors=report.total_errors,
                summary=report.summary,
                recommendations=report.recommendations,
            )

            # Создаем записи об ошибках
            for error in report.errors:
                await self.error_db_service.create_error_entry(
                    error_report_id=db_report.id,
                    error_type=error.error_type,
                    severity=error.severity,
                    message=error.message,
                    details=error.details,
                    context=(
                        error.context.model_dump() if error.context else None
                    ),
                    stack_trace=error.stack_trace,
                )

            self.logger.info(
                "Error report saved to database",
                report_id=report.report_id,
                total_errors=report.total_errors,
            )
        except Exception as e:
            self.logger.error(
                "Failed to save error report to database",
                report_id=report.report_id,
                error=str(e),
            )

    async def _save_group_report_to_db(
        self, report: GroupLoadErrorReport
    ) -> None:
        """Сохраняет отчет о группах в базу данных"""
        if not self.error_db_service:
            return

        try:
            # Создаем отчет в базе данных
            db_report = await self.error_db_service.create_error_report(
                report_id=report.report_id,
                operation=report.operation,
                total_errors=report.total_errors,
                summary=report.summary,
                recommendations=report.recommendations,
                groups_processed=report.groups_processed,
                groups_successful=report.groups_successful,
                groups_failed=report.groups_failed,
                groups_skipped=report.groups_skipped,
                processing_time_seconds=report.processing_time_seconds,
            )

            # Создаем записи об ошибках
            for error in report.errors:
                await self.error_db_service.create_error_entry(
                    error_report_id=db_report.id,
                    error_type=error.error_type,
                    severity=error.severity,
                    message=error.message,
                    details=error.details,
                    context=(
                        error.context.model_dump() if error.context else None
                    ),
                    stack_trace=error.stack_trace,
                )

            self.logger.info(
                "Group error report saved to database",
                report_id=report.report_id,
                groups_processed=report.groups_processed,
                groups_successful=report.groups_successful,
                groups_failed=report.groups_failed,
            )
        except Exception as e:
            self.logger.error(
                "Failed to save group error report to database",
                report_id=report.report_id,
                error=str(e),
            )

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
