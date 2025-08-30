"""
Сервис для модуля Error Reporting

Содержит бизнес-логику для работы с отчетами об ошибках
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..exceptions import ServiceUnavailableError
from .models import (
    ErrorReportRepository,
    ErrorReport,
    ErrorType,
    ErrorSeverity,
    ErrorContext,
)
from .config import error_reporting_config
from .constants import (
    ERROR_SEVERITY_MEDIUM,
    ERROR_TYPE_UNKNOWN,
    ERROR_REPORT_STATUS_PENDING,
    ERROR_REPORT_STATUS_ACKNOWLEDGED,
    ERROR_REPORT_STATUS_RESOLVED,
    MAX_ERROR_MESSAGE_LENGTH,
    MAX_STACK_TRACE_LENGTH,
    MAX_ADDITIONAL_CONTEXT_SIZE,
    MAX_RESOLUTION_NOTES_LENGTH,
    ERROR_REPORT_TIMEOUT_ACKNOWLEDGE_HOURS,
    ERROR_REPORT_TIMEOUT_RESOLVE_HOURS,
)


class ErrorReportingService:
    """
    Сервис для работы с отчетами об ошибках

    Реализует бизнес-логику для создания, обработки и анализа отчетов об ошибках
    """

    def __init__(self, repository: ErrorReportRepository = None):
        self.repository = repository or ErrorReportRepository()
        self.logger = logging.getLogger(__name__)

    async def create_error_report(
        self,
        error_type: str,
        severity: str,
        message: str,
        stack_trace: Optional[str] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> ErrorReport:
        """
        Создать отчет об ошибке

        Args:
            error_type: Тип ошибки
            severity: Уровень серьезности
            message: Сообщение об ошибке
            stack_trace: Трассировка стека
            operation: Операция, во время которой произошла ошибка
            user_id: ID пользователя
            request_id: ID запроса
            additional_context: Дополнительный контекст

        Returns:
            ErrorReport: Созданный отчет об ошибке
        """
        try:
            # Валидируем входные данные
            await self._validate_error_data(
                error_type, severity, message, stack_trace, additional_context
            )

            # Создаем контекст ошибки
            context = ErrorContext(
                operation=operation,
                user_id=user_id,
                request_id=request_id,
                additional_data=additional_context or {},
            )

            # Создаем отчет об ошибке
            error_report = ErrorReport(
                error_type=ErrorType(error_type),
                severity=ErrorSeverity(severity),
                message=message,
                stack_trace=stack_trace,
                context=context,
            )

            # Сохраняем отчет
            await self.repository.save(error_report)

            # Логируем создание отчета
            self.logger.warning(
                f"Error report created: {error_report.id}, type: {error_type}, severity: {severity}"
            )

            # Проверяем лимиты
            await self._check_limits()

            return error_report

        except Exception as e:
            self.logger.error(f"Failed to create error report: {e}")
            raise ServiceUnavailableError(
                f"Failed to create error report: {str(e)}"
            )

    async def get_error_report(self, report_id: str) -> Optional[ErrorReport]:
        """
        Получить отчет об ошибке по ID

        Args:
            report_id: ID отчета

        Returns:
            Optional[ErrorReport]: Отчет об ошибке или None
        """
        try:
            return await self.repository.find_by_id(report_id)
        except Exception as e:
            self.logger.error(f"Failed to get error report {report_id}: {e}")
            raise ServiceUnavailableError(
                f"Failed to get error report: {str(e)}"
            )

    async def get_error_reports(
        self,
        page: int = 1,
        size: int = 20,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        operation: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Получить список отчетов об ошибках с фильтрацией и пагинацией

        Args:
            page: Номер страницы
            size: Размер страницы
            error_type: Фильтр по типу ошибки
            severity: Фильтр по серьезности
            operation: Фильтр по операции
            acknowledged: Фильтр по подтверждению
            resolved: Фильтр по разрешению
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Dict[str, Any]: Результаты поиска с пагинацией
        """
        try:
            # Валидируем параметры пагинации
            await self._validate_pagination_params(page, size)

            # Получаем общее количество
            total = await self.repository.count_by_filters(
                error_type,
                severity,
                operation,
                acknowledged,
                resolved,
                start_date,
                end_date,
            )

            # Получаем отчеты для текущей страницы
            reports = await self.repository.find_by_filters(
                error_type,
                severity,
                operation,
                acknowledged,
                resolved,
                start_date,
                end_date,
                limit=size,
            )

            # Вычисляем пагинацию
            pages = (total + size - 1) // size
            has_next = page * size < total
            has_prev = page > 1

            return {
                "items": reports,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
                "has_next": has_next,
                "has_prev": has_prev,
            }

        except Exception as e:
            self.logger.error(f"Failed to get error reports: {e}")
            raise ServiceUnavailableError(
                f"Failed to get error reports: {str(e)}"
            )

    async def acknowledge_error_report(
        self, report_id: str, acknowledged_by: str
    ) -> Optional[ErrorReport]:
        """
        Подтвердить отчет об ошибке

        Args:
            report_id: ID отчета
            acknowledged_by: Кто подтверждает отчет

        Returns:
            Optional[ErrorReport]: Подтвержденный отчет или None
        """
        try:
            report = await self.repository.find_by_id(report_id)
            if not report:
                return None

            report.acknowledge(acknowledged_by)
            await self.repository.save(report)

            self.logger.info(
                f"Error report {report_id} acknowledged by {acknowledged_by}"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Failed to acknowledge error report {report_id}: {e}"
            )
            raise ServiceUnavailableError(
                f"Failed to acknowledge error report: {str(e)}"
            )

    async def resolve_error_report(
        self, report_id: str, resolution_notes: Optional[str] = None
    ) -> Optional[ErrorReport]:
        """
        Разрешить отчет об ошибке

        Args:
            report_id: ID отчета
            resolution_notes: Заметки о разрешении

        Returns:
            Optional[ErrorReport]: Разрешенный отчет или None
        """
        try:
            report = await self.repository.find_by_id(report_id)
            if not report:
                return None

            # Валидируем заметки о разрешении
            if (
                resolution_notes
                and len(resolution_notes) > MAX_RESOLUTION_NOTES_LENGTH
            ):
                resolution_notes = resolution_notes[
                    :MAX_RESOLUTION_NOTES_LENGTH
                ]

            report.resolve(resolution_notes)
            await self.repository.save(report)

            self.logger.info(f"Error report {report_id} resolved")

            return report

        except Exception as e:
            self.logger.error(
                f"Failed to resolve error report {report_id}: {e}"
            )
            raise ServiceUnavailableError(
                f"Failed to resolve error report: {str(e)}"
            )

    async def delete_error_report(self, report_id: str) -> bool:
        """
        Удалить отчет об ошибке

        Args:
            report_id: ID отчета

        Returns:
            bool: True если отчет был удален
        """
        try:
            deleted = await self.repository.delete(report_id)

            if deleted:
                self.logger.info(f"Error report {report_id} deleted")

            return deleted

        except Exception as e:
            self.logger.error(
                f"Failed to delete error report {report_id}: {e}"
            )
            raise ServiceUnavailableError(
                f"Failed to delete error report: {str(e)}"
            )

    async def get_error_statistics(
        self,
        days: int = 7,
        include_resolved: bool = True,
    ) -> Dict[str, Any]:
        """
        Получить статистику по ошибкам

        Args:
            days: Количество дней для статистики
            include_resolved: Включать ли разрешенные отчеты

        Returns:
            Dict[str, Any]: Статистика по ошибкам
        """
        try:
            # Валидируем параметры
            if days < 1 or days > 365:
                days = 7

            stats = await self.repository.get_statistics(
                days, include_resolved
            )

            # Добавляем дополнительные метрики
            stats["error_types_stats"] = await self._get_error_types_stats(
                days, include_resolved
            )
            stats["severity_stats"] = await self._get_severity_stats(
                days, include_resolved
            )
            stats["operation_stats"] = await self._get_operation_stats(
                days, include_resolved
            )

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get error statistics: {e}")
            raise ServiceUnavailableError(
                f"Failed to get error statistics: {str(e)}"
            )

    async def get_pending_reports(self, limit: int = 50) -> List[ErrorReport]:
        """
        Получить неподтвержденные отчеты об ошибках

        Args:
            limit: Максимальное количество отчетов

        Returns:
            List[ErrorReport]: Список неподтвержденных отчетов
        """
        try:
            return await self.repository.get_pending_reports(limit)
        except Exception as e:
            self.logger.error(f"Failed to get pending reports: {e}")
            raise ServiceUnavailableError(
                f"Failed to get pending reports: {str(e)}"
            )

    async def get_critical_reports(self, limit: int = 50) -> List[ErrorReport]:
        """
        Получить критические отчеты об ошибках

        Args:
            limit: Максимальное количество отчетов

        Returns:
            List[ErrorReport]: Список критических отчетов
        """
        try:
            return await self.repository.get_critical_reports(limit)
        except Exception as e:
            self.logger.error(f"Failed to get critical reports: {e}")
            raise ServiceUnavailableError(
                f"Failed to get critical reports: {str(e)}"
            )

    async def bulk_acknowledge_reports(
        self, report_ids: List[str], acknowledged_by: str
    ) -> Dict[str, Any]:
        """
        Массовое подтверждение отчетов об ошибках

        Args:
            report_ids: Список ID отчетов
            acknowledged_by: Кто подтверждает отчеты

        Returns:
            Dict[str, Any]: Результаты массовой операции
        """
        try:
            successful = []
            failed = []

            for report_id in report_ids:
                try:
                    report = await self.acknowledge_error_report(
                        report_id, acknowledged_by
                    )
                    if report:
                        successful.append(report_id)
                    else:
                        failed.append(
                            {"id": report_id, "error": "Report not found"}
                        )
                except Exception as e:
                    failed.append({"id": report_id, "error": str(e)})

            return {
                "successful": successful,
                "failed": failed,
                "total_processed": len(report_ids),
                "success_count": len(successful),
                "failure_count": len(failed),
            }

        except Exception as e:
            self.logger.error(f"Failed to bulk acknowledge reports: {e}")
            raise ServiceUnavailableError(
                f"Failed to bulk acknowledge reports: {str(e)}"
            )

    async def cleanup_old_reports(self, max_age_days: int = 365) -> int:
        """
        Очистить старые отчеты

        Args:
            max_age_days: Максимальный возраст отчетов в днях

        Returns:
            int: Количество удаленных отчетов
        """
        try:
            deleted_count = await self.repository.cleanup_old_reports(
                max_age_days
            )

            if deleted_count > 0:
                self.logger.info(
                    f"Cleaned up {deleted_count} old error reports"
                )

            return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old reports: {e}")
            raise ServiceUnavailableError(
                f"Failed to cleanup old reports: {str(e)}"
            )

    async def _validate_error_data(
        self,
        error_type: str,
        severity: str,
        message: str,
        stack_trace: Optional[str],
        additional_context: Optional[Dict[str, Any]],
    ) -> None:
        """Валидировать данные ошибки"""
        from .exceptions import (
            ErrorReportValidationError,
            ErrorReportSizeLimitError,
            ErrorReportInvalidTypeError,
            ErrorReportInvalidSeverityError,
        )

        # Валидируем тип ошибки
        try:
            ErrorType(error_type)
        except ValueError:
            raise ErrorReportInvalidTypeError(
                error_type,
                [
                    "network",
                    "database",
                    "api",
                    "validation",
                    "authentication",
                    "authorization",
                    "business_logic",
                    "external_service",
                    "system",
                    "unknown",
                ],
            )

        # Валидируем серьезность
        try:
            ErrorSeverity(severity)
        except ValueError:
            raise ErrorReportInvalidSeverityError(
                severity, ["low", "medium", "high", "critical"]
            )

        # Валидируем размер сообщения
        if len(message) > MAX_ERROR_MESSAGE_LENGTH:
            raise ErrorReportSizeLimitError(
                "message", len(message), MAX_ERROR_MESSAGE_LENGTH
            )

        # Валидируем размер stack trace
        if stack_trace and len(stack_trace) > MAX_STACK_TRACE_LENGTH:
            raise ErrorReportSizeLimitError(
                "stack_trace", len(stack_trace), MAX_STACK_TRACE_LENGTH
            )

        # Валидируем размер дополнительного контекста
        if additional_context:
            context_size = len(str(additional_context).encode("utf-8"))
            if context_size > MAX_ADDITIONAL_CONTEXT_SIZE:
                raise ErrorReportSizeLimitError(
                    "additional_context",
                    context_size,
                    MAX_ADDITIONAL_CONTEXT_SIZE,
                )

    async def _validate_pagination_params(self, page: int, size: int) -> None:
        """Валидировать параметры пагинации"""
        if page < 1:
            page = 1
        if size < 1 or size > error_reporting_config.MAX_PAGE_SIZE:
            size = error_reporting_config.DEFAULT_PAGE_SIZE

    async def _check_limits(self) -> None:
        """Проверить лимиты хранения отчетов"""
        from .exceptions import ErrorReportLimitExceededError

        total_reports = len(await self.repository.find_all())
        if total_reports >= error_reporting_config.MAX_REPORTS_TOTAL:
            # Автоматическая очистка старых отчетов
            await self.cleanup_old_reports(
                error_reporting_config.RETENTION_DAYS
            )

            # Проверяем снова после очистки
            total_reports = len(await self.repository.find_all())
            if total_reports >= error_reporting_config.MAX_REPORTS_TOTAL:
                raise ErrorReportLimitExceededError(
                    total_reports, error_reporting_config.MAX_REPORTS_TOTAL
                )

    async def _get_error_types_stats(
        self, days: int, include_resolved: bool
    ) -> Dict[str, int]:
        """Получить статистику по типам ошибок"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            all_reports = await self.repository.find_all()

            reports = [r for r in all_reports if r.created_at >= start_date]
            if not include_resolved:
                reports = [r for r in reports if not r.resolved]

            # Ключ: тип ошибки, Значение: количество
            stats: Dict[str, int] = {}
            for report in reports:
                error_type = str(report.error_type)
                stats[error_type] = stats.get(error_type, 0) + 1

            return stats

        except Exception:
            return {}

    async def _get_severity_stats(
        self, days: int, include_resolved: bool
    ) -> Dict[str, int]:
        """Получить статистику по серьезности ошибок"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            all_reports = await self.repository.find_all()

            reports = [r for r in all_reports if r.created_at >= start_date]
            if not include_resolved:
                reports = [r for r in reports if not r.resolved]

            # Ключ: уровень серьезности, Значение: количество
            stats: Dict[str, int] = {}
            for report in reports:
                severity = str(report.severity)
                stats[severity] = stats.get(severity, 0) + 1

            return stats

        except Exception:
            return {}

    async def _get_operation_stats(
        self, days: int, include_resolved: bool
    ) -> Dict[str, int]:
        """Получить статистику по операциям"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            all_reports = await self.repository.find_all()

            reports = [r for r in all_reports if r.created_at >= start_date]
            if not include_resolved:
                reports = [r for r in reports if not r.resolved]

            stats: Dict[str, int] = {}
            for report in reports:
                operation = report.context.operation or "unknown"
                stats[operation] = stats.get(operation, 0) + 1

            return stats

        except Exception:
            return {}


# Экспорт
__all__ = [
    "ErrorReportingService",
]
