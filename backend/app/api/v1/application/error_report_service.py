"""
Application Service для системы отчетов об ошибках (DDD)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..domain.error_report import (
    ErrorReport,
    ErrorType,
    ErrorSeverity,
    ErrorContext,
)
from .base import ApplicationService


class ErrorReportApplicationService(ApplicationService):
    """Application Service для работы с отчетами об ошибках"""

    def __init__(self, error_report_repository=None):
        self.error_report_repository = error_report_repository

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
        """Создать отчет об ошибке"""
        context = ErrorContext(
            operation=operation,
            user_id=user_id,
            request_id=request_id,
            additional_data=additional_context or {},
        )

        error_report = ErrorReport(
            error_type=ErrorType(error_type),
            severity=ErrorSeverity(severity),
            message=message,
            stack_trace=stack_trace,
            context=context,
        )

        await self.error_report_repository.save(error_report)
        return error_report

    async def get_error_report(self, report_id: str) -> Optional[ErrorReport]:
        """Получить отчет об ошибке по ID"""
        return await self.error_report_repository.find_by_id(report_id)

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
        """Получить список отчетов об ошибках с фильтрами"""
        # Получаем все отчеты (в реальности нужна пагинация в репозитории)
        all_reports = await self.error_report_repository.find_all()

        # Применяем фильтры
        filtered_reports = []
        for report in all_reports:
            if error_type and str(report.error_type) != error_type:
                continue
            if severity and str(report.severity) != severity:
                continue
            if operation and report.context.operation != operation:
                continue
            if (
                acknowledged is not None
                and report.acknowledged != acknowledged
            ):
                continue
            if resolved is not None and report.resolved != resolved:
                continue
            if start_date and report.created_at < start_date:
                continue
            if end_date and report.created_at > end_date:
                continue

            filtered_reports.append(report)

        # Пагинация
        total = len(filtered_reports)
        start_index = (page - 1) * size
        end_index = start_index + size
        paginated_reports = filtered_reports[start_index:end_index]

        return {
            "items": [report.to_dict() for report in paginated_reports],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "has_next": page * size < total,
            "has_prev": page > 1,
        }

    async def acknowledge_error_report(
        self, report_id: str, acknowledged_by: str
    ) -> Optional[ErrorReport]:
        """Подтвердить отчет об ошибке"""
        report = await self.error_report_repository.find_by_id(report_id)
        if not report:
            return None

        report.acknowledge(acknowledged_by)
        await self.error_report_repository.save(report)
        return report

    async def resolve_error_report(
        self, report_id: str, resolution_notes: Optional[str] = None
    ) -> Optional[ErrorReport]:
        """Разрешить отчет об ошибке"""
        report = await self.error_report_repository.find_by_id(report_id)
        if not report:
            return None

        report.resolve(resolution_notes)
        await self.error_report_repository.save(report)
        return report

    async def delete_error_report(self, report_id: str) -> bool:
        """Удалить отчет об ошибке"""
        return await self.error_report_repository.delete(report_id)

    async def get_error_statistics(
        self,
        days: int = 7,
        include_resolved: bool = True,
    ) -> Dict[str, Any]:
        """Получить статистику по ошибкам"""
        start_date = datetime.utcnow() - timedelta(days=days)
        all_reports = await self.error_report_repository.find_all()

        # Фильтруем по дате
        recent_reports = [r for r in all_reports if r.created_at >= start_date]

        total_reports = len(recent_reports)
        acknowledged_reports = len(
            [r for r in recent_reports if r.acknowledged]
        )
        resolved_reports = len([r for r in recent_reports if r.resolved])
        critical_reports = len([r for r in recent_reports if r.is_critical])

        # Статистика по типам ошибок
        error_types_stats = {}
        for report in recent_reports:
            error_type = str(report.error_type)
            if error_type not in error_types_stats:
                error_types_stats[error_type] = 0
            error_types_stats[error_type] += 1

        # Статистика по серьезности
        severity_stats = {}
        for report in recent_reports:
            severity = str(report.severity)
            if severity not in severity_stats:
                severity_stats[severity] = 0
            severity_stats[severity] += 1

        # Статистика по операциям
        operation_stats = {}
        for report in recent_reports:
            operation = report.context.operation or "unknown"
            if operation not in operation_stats:
                operation_stats[operation] = 0
            operation_stats[operation] += 1

        return {
            "period_days": days,
            "total_reports": total_reports,
            "acknowledged_reports": acknowledged_reports,
            "resolved_reports": resolved_reports,
            "critical_reports": critical_reports,
            "acknowledgment_rate": (
                acknowledged_reports / total_reports
                if total_reports > 0
                else 0
            ),
            "resolution_rate": (
                resolved_reports / total_reports if total_reports > 0 else 0
            ),
            "error_types_stats": error_types_stats,
            "severity_stats": severity_stats,
            "operation_stats": operation_stats,
        }

    async def get_pending_reports(self, limit: int = 50) -> List[ErrorReport]:
        """Получить неподтвержденные отчеты об ошибках"""
        all_reports = await self.error_report_repository.find_all()
        pending_reports = [r for r in all_reports if r.is_pending]

        # Сортируем по времени создания (новые сначала)
        pending_reports.sort(key=lambda r: r.created_at, reverse=True)

        return pending_reports[:limit]

    async def get_critical_reports(self, limit: int = 50) -> List[ErrorReport]:
        """Получить критические отчеты об ошибках"""
        all_reports = await self.error_report_repository.find_all()
        critical_reports = [r for r in all_reports if r.is_critical]

        # Сортируем по времени создания (новые сначала)
        critical_reports.sort(key=lambda r: r.created_at, reverse=True)

        return critical_reports[:limit]

    async def bulk_acknowledge_reports(
        self, report_ids: List[str], acknowledged_by: str
    ) -> Dict[str, Any]:
        """Массовое подтверждение отчетов об ошибках"""
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
