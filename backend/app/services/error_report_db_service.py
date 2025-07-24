"""
Сервис для работы с отчетами об ошибках в базе данных
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.error_report import ErrorReport
from app.models.error_entry import ErrorEntry
from app.schemas.error_report import (
    ErrorReport as ErrorReportSchema,
    ErrorEntry as ErrorEntrySchema,
    ErrorType,
    ErrorSeverity,
    GroupLoadErrorReport,
)
from app.schemas.base import PaginatedResponse


class ErrorReportDBService:
    """Сервис для работы с отчетами об ошибках в базе данных"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_error_report(
        self,
        report_id: str,
        operation: str,
        total_errors: int,
        summary: Optional[Dict[str, int]] = None,
        recommendations: Optional[List[str]] = None,
        groups_processed: Optional[int] = None,
        groups_successful: Optional[int] = None,
        groups_failed: Optional[int] = None,
        groups_skipped: Optional[int] = None,
        processing_time_seconds: Optional[float] = None,
    ) -> ErrorReport:
        """Создает новый отчет об ошибках в базе данных"""
        error_report = ErrorReport(
            report_id=report_id,
            operation=operation,
            total_errors=total_errors,
            summary=summary,
            recommendations=recommendations,
            groups_processed=groups_processed,
            groups_successful=groups_successful,
            groups_failed=groups_failed,
            groups_skipped=groups_skipped,
            processing_time_seconds=processing_time_seconds,
        )

        self.db.add(error_report)
        await self.db.commit()
        await self.db.refresh(error_report)

        return error_report

    async def create_error_entry(
        self,
        error_report_id: int,
        error_type: ErrorType,
        severity: ErrorSeverity,
        message: str,
        details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> ErrorEntry:
        """Создает новую запись об ошибке в базе данных"""
        error_entry = ErrorEntry(
            error_report_id=error_report_id,
            error_type=error_type,
            severity=severity,
            message=message,
            details=details,
            context=context,
            stack_trace=stack_trace,
        )

        self.db.add(error_entry)
        await self.db.commit()
        await self.db.refresh(error_entry)

        return error_entry

    async def get_error_reports(
        self,
        page: int = 1,
        size: int = 20,
        error_type: Optional[ErrorType] = None,
        severity: Optional[ErrorSeverity] = None,
        operation: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_acknowledged: Optional[bool] = None,
    ) -> PaginatedResponse[ErrorReportSchema]:
        """Получает список отчетов об ошибках с фильтрацией и пагинацией"""
        # Базовый запрос
        query = select(ErrorReport).options(
            selectinload(ErrorReport.error_entries)
        )

        # Применяем фильтры
        conditions = []

        if error_type:
            conditions.append(
                ErrorReport.error_entries.any(
                    ErrorEntry.error_type == error_type
                )
            )

        if severity:
            conditions.append(
                ErrorReport.error_entries.any(ErrorEntry.severity == severity)
            )

        if operation:
            conditions.append(ErrorReport.operation == operation)

        if start_date:
            conditions.append(ErrorReport.created_at >= start_date)

        if end_date:
            conditions.append(ErrorReport.created_at <= end_date)

        if is_acknowledged is not None:
            conditions.append(ErrorReport.is_acknowledged == is_acknowledged)

        if conditions:
            query = query.where(and_(*conditions))

        # Подсчитываем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        # Применяем сортировку и пагинацию
        query = query.order_by(desc(ErrorReport.created_at))
        query = query.offset((page - 1) * size).limit(size)

        # Выполняем запрос
        result = await self.db.execute(query)
        error_reports = result.scalars().all()

        # Преобразуем в схемы
        items = []
        for report in error_reports:
            report_schema = ErrorReportSchema(
                report_id=report.report_id,
                created_at=report.created_at,
                operation=report.operation,
                total_errors=report.total_errors,
                errors=[
                    ErrorEntrySchema(
                        timestamp=entry.created_at,
                        error_type=entry.error_type,
                        severity=entry.severity,
                        message=entry.message,
                        details=entry.details,
                        context=entry.context,
                        stack_trace=entry.stack_trace,
                    )
                    for entry in report.error_entries
                ],
                summary=report.summary or {},
                recommendations=report.recommendations or [],
            )

            # Если это отчет о группах, добавляем специфичные поля
            if report.groups_processed is not None:
                report_schema = GroupLoadErrorReport(
                    **report_schema.model_dump(),
                    groups_processed=report.groups_processed,
                    groups_successful=report.groups_successful or 0,
                    groups_failed=report.groups_failed or 0,
                    groups_skipped=report.groups_skipped or 0,
                    processing_time_seconds=report.processing_time_seconds
                    or 0.0,
                )

            items.append(report_schema)

        return PaginatedResponse(
            total=total or 0,
            page=page,
            size=size,
            items=items,
        )

    async def get_error_report(
        self, report_id: str
    ) -> Optional[ErrorReportSchema]:
        """Получает конкретный отчет об ошибках по ID"""
        query = (
            select(ErrorReport)
            .options(selectinload(ErrorReport.error_entries))
            .where(ErrorReport.report_id == report_id)
        )

        result = await self.db.execute(query)
        report = result.scalar_one_or_none()

        if not report:
            return None

        # Преобразуем в схему
        report_schema = ErrorReportSchema(
            report_id=report.report_id,
            created_at=report.created_at,
            operation=report.operation,
            total_errors=report.total_errors,
            errors=[
                ErrorEntrySchema(
                    timestamp=entry.created_at,
                    error_type=entry.error_type,
                    severity=entry.severity,
                    message=entry.message,
                    details=entry.details,
                    context=entry.context,
                    stack_trace=entry.stack_trace,
                )
                for entry in report.error_entries
            ],
            summary=report.summary or {},
            recommendations=report.recommendations or [],
        )

        # Если это отчет о группах, добавляем специфичные поля
        if report.groups_processed is not None:
            report_schema = GroupLoadErrorReport(
                **report_schema.model_dump(),
                groups_processed=report.groups_processed,
                groups_successful=report.groups_successful or 0,
                groups_failed=report.groups_failed or 0,
                groups_skipped=report.groups_skipped or 0,
                processing_time_seconds=report.processing_time_seconds or 0.0,
            )

        return report_schema

    async def acknowledge_error_report(
        self, report_id: str, acknowledged_by: str
    ) -> Optional[ErrorReport]:
        """Подтверждает обработку отчета об ошибках"""
        query = select(ErrorReport).where(ErrorReport.report_id == report_id)
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()

        if not report:
            return None

        report.is_acknowledged = True
        report.acknowledged_at = datetime.utcnow()
        report.acknowledged_by = acknowledged_by

        await self.db.commit()
        await self.db.refresh(report)

        return report

    async def delete_error_report(self, report_id: str) -> bool:
        """Удаляет отчет об ошибках"""
        query = select(ErrorReport).where(ErrorReport.report_id == report_id)
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()

        if not report:
            return False

        await self.db.delete(report)
        await self.db.commit()

        return True

    async def get_error_stats(self, days: int = 7) -> Dict[str, Any]:
        """Получает статистику ошибок за указанный период"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Общее количество ошибок
        total_errors_query = select(func.count(ErrorEntry.id)).where(
            ErrorEntry.created_at >= start_date
        )
        total_errors = await self.db.scalar(total_errors_query) or 0

        # Ошибки по типам
        errors_by_type_query = (
            select(ErrorEntry.error_type, func.count(ErrorEntry.id))
            .where(ErrorEntry.created_at >= start_date)
            .group_by(ErrorEntry.error_type)
        )
        result = await self.db.execute(errors_by_type_query)
        errors_by_type = {row[0].value: row[1] for row in result.all()}

        # Ошибки по серьезности
        errors_by_severity_query = (
            select(ErrorEntry.severity, func.count(ErrorEntry.id))
            .where(ErrorEntry.created_at >= start_date)
            .group_by(ErrorEntry.severity)
        )
        result = await self.db.execute(errors_by_severity_query)
        errors_by_severity = {row[0].value: row[1] for row in result.all()}

        # Ошибки по операциям
        errors_by_operation_query = (
            select(ErrorReport.operation, func.count(ErrorEntry.id))
            .join(ErrorEntry, ErrorReport.id == ErrorEntry.error_report_id)
            .where(ErrorEntry.created_at >= start_date)
            .group_by(ErrorReport.operation)
        )
        result = await self.db.execute(errors_by_operation_query)
        errors_by_operation = {row[0]: row[1] for row in result.all()}

        # Ежедневная статистика
        daily_stats_query = (
            select(
                func.date(ErrorEntry.created_at).label("date"),
                func.count(ErrorEntry.id).label("count"),
            )
            .where(ErrorEntry.created_at >= start_date)
            .group_by(func.date(ErrorEntry.created_at))
            .order_by(func.date(ErrorEntry.created_at))
        )
        result = await self.db.execute(daily_stats_query)
        daily_trends = [
            {"date": row[0].isoformat(), "count": row[1]}
            for row in result.all()
        ]

        # Почасовая статистика (за последние 24 часа)
        hourly_start_date = end_date - timedelta(hours=24)
        hourly_stats_query = (
            select(
                func.date_trunc("hour", ErrorEntry.created_at).label("hour"),
                func.count(ErrorEntry.id).label("count"),
            )
            .where(ErrorEntry.created_at >= hourly_start_date)
            .group_by(func.date_trunc("hour", ErrorEntry.created_at))
            .order_by(func.date_trunc("hour", ErrorEntry.created_at))
        )
        result = await self.db.execute(hourly_stats_query)
        hourly_trends = [
            {"hour": row[0].isoformat(), "count": row[1]}
            for row in result.all()
        ]

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "total_errors": total_errors,
            "errors_by_type": errors_by_type,
            "errors_by_severity": errors_by_severity,
            "errors_by_operation": errors_by_operation,
            "trends": {
                "daily": daily_trends,
                "hourly": hourly_trends,
            },
        }
