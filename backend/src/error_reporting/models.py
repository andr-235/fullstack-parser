"""
Модели для модуля Error Reporting

Определяет модели данных для отчетов об ошибках
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..database import get_db_session
from .config import error_reporting_config


class ErrorSeverity:
    """Уровень серьезности ошибки"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __init__(self, level: str = MEDIUM):
        if level not in [self.LOW, self.MEDIUM, self.HIGH, self.CRITICAL]:
            raise ValueError(f"Invalid severity level: {level}")
        self.level = level

    def is_critical(self) -> bool:
        return self.level == self.CRITICAL

    def is_high(self) -> bool:
        return self.level in [self.HIGH, self.CRITICAL]

    def __str__(self) -> str:
        return self.level

    def __eq__(self, other) -> bool:
        if isinstance(other, ErrorSeverity):
            return self.level == other.level
        return self.level == other


class ErrorType:
    """Тип ошибки"""

    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    UNKNOWN = "unknown"

    def __init__(self, error_type: str = UNKNOWN):
        valid_types = [
            self.NETWORK,
            self.DATABASE,
            self.API,
            self.VALIDATION,
            self.AUTHENTICATION,
            self.AUTHORIZATION,
            self.BUSINESS_LOGIC,
            self.EXTERNAL_SERVICE,
            self.SYSTEM,
            self.UNKNOWN,
        ]
        if error_type not in valid_types:
            raise ValueError(f"Invalid error type: {error_type}")
        self.error_type = error_type

    def __str__(self) -> str:
        return self.error_type

    def __eq__(self, other) -> bool:
        if isinstance(other, ErrorType):
            return self.error_type == other.error_type
        return self.error_type == other


class ErrorContext:
    """Контекст ошибки"""

    def __init__(
        self,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        self.operation = operation
        self.user_id = user_id
        self.session_id = session_id
        self.request_id = request_id
        self.endpoint = endpoint
        self.method = method
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.additional_data = additional_data or {}


class ErrorReport:
    """
    Доменная сущность отчета об ошибке

    Представляет отчет об ошибке с полной информацией о контексте
    """

    def __init__(
        self,
        id: Optional[str] = None,
        error_type: ErrorType = None,
        severity: ErrorSeverity = None,
        message: str = None,
        stack_trace: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ):
        self.id = id or self._generate_id()
        self.error_type = error_type or ErrorType()
        self.severity = severity or ErrorSeverity()
        self.message = message or ""
        self.stack_trace = stack_trace
        self.context = context or ErrorContext()

        # Метаданные
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1

        # Статус
        self.acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None
        self.resolved = False
        self.resolved_at = None
        self.resolution_notes = None

    def acknowledge(self, acknowledged_by: str) -> None:
        """Подтвердить обработку ошибки"""
        if self.acknowledged:
            raise ValueError("Error report is already acknowledged")

        self.acknowledged = True
        self.acknowledged_by = acknowledged_by
        self.acknowledged_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version += 1

    def resolve(self, resolution_notes: Optional[str] = None) -> None:
        """Разрешить ошибку"""
        if not self.acknowledged:
            raise ValueError("Error must be acknowledged before resolution")

        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolution_notes = resolution_notes
        self.updated_at = datetime.utcnow()
        self.version += 1

    def reopen(self) -> None:
        """Переоткрыть ошибку"""
        self.resolved = False
        self.resolved_at = None
        self.resolution_notes = None
        self.updated_at = datetime.utcnow()
        self.version += 1

    @property
    def is_critical(self) -> bool:
        return self.severity.is_critical()

    @property
    def is_pending(self) -> bool:
        return not self.acknowledged

    @property
    def is_resolved(self) -> bool:
        return self.resolved

    @property
    def time_to_acknowledge(self) -> Optional[float]:
        """Время до подтверждения в часах"""
        if not self.acknowledged_at:
            return None
        return (self.acknowledged_at - self.created_at).total_seconds() / 3600

    @property
    def time_to_resolve(self) -> Optional[float]:
        """Время до разрешения в часах"""
        if not self.resolved_at:
            return None
        return (self.resolved_at - self.created_at).total_seconds() / 3600

    @property
    def status(self) -> str:
        """Получить текстовый статус отчета"""
        if self.resolved:
            return "resolved"
        elif self.acknowledged:
            return "acknowledged"
        else:
            return "pending"

    def _generate_id(self) -> str:
        """Сгенерировать уникальный ID для отчета"""
        import uuid

        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "error_type": str(self.error_type),
            "severity": str(self.severity),
            "message": self.message,
            "stack_trace": self.stack_trace,
            "context": {
                "operation": self.context.operation,
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "endpoint": self.context.endpoint,
                "method": self.context.method,
                "ip_address": self.context.ip_address,
                "user_agent": self.context.user_agent,
                "additional_data": self.context.additional_data,
            },
            "status": {
                "current": self.status,
                "acknowledged": self.acknowledged,
                "acknowledged_by": self.acknowledged_by,
                "acknowledged_at": (
                    self.acknowledged_at.isoformat()
                    if self.acknowledged_at
                    else None
                ),
                "resolved": self.resolved,
                "resolved_at": (
                    self.resolved_at.isoformat() if self.resolved_at else None
                ),
                "resolution_notes": self.resolution_notes,
            },
            "timestamps": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "time_to_acknowledge": self.time_to_acknowledge,
                "time_to_resolve": self.time_to_resolve,
            },
            "metadata": {
                "version": self.version,
                "is_critical": self.is_critical,
                "is_pending": self.is_pending,
                "is_resolved": self.is_resolved,
            },
        }


class ErrorReportRepository:
    """
    Репозиторий для работы с отчетами об ошибках

    Предоставляет интерфейс для хранения и получения отчетов об ошибках
    """

    def __init__(self, db=None):
        self.db = db
        # In-memory хранилище для простоты (в продакшене использовать БД)
        self._reports = {}
        self._total_count = 0

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def save(self, report: ErrorReport) -> None:
        """
        Сохранить отчет об ошибке

        Args:
            report: Отчет для сохранения
        """
        self._reports[report.id] = report
        self._total_count = len(self._reports)

    async def find_by_id(self, report_id: str) -> Optional[ErrorReport]:
        """
        Найти отчет по ID

        Args:
            report_id: ID отчета

        Returns:
            Optional[ErrorReport]: Отчет или None
        """
        return self._reports.get(report_id)

    async def find_all(self) -> list:
        """
        Получить все отчеты

        Returns:
            list: Список всех отчетов
        """
        return list(self._reports.values())

    async def delete(self, report_id: str) -> bool:
        """
        Удалить отчет

        Args:
            report_id: ID отчета

        Returns:
            bool: True если отчет был удален
        """
        if report_id in self._reports:
            del self._reports[report_id]
            self._total_count = len(self._reports)
            return True
        return False

    async def find_by_filters(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        operation: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list:
        """
        Найти отчеты по фильтрам

        Args:
            error_type: Фильтр по типу ошибки
            severity: Фильтр по серьезности
            operation: Фильтр по операции
            acknowledged: Фильтр по подтверждению
            resolved: Фильтр по разрешению
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Максимальное количество результатов

        Returns:
            list: Список найденных отчетов
        """
        results = []

        for report in self._reports.values():
            # Применяем фильтры
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

            results.append(report)

            # Ограничиваем количество результатов
            if len(results) >= limit:
                break

        return results

    async def count_by_filters(
        self,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        operation: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        resolved: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Посчитать количество отчетов по фильтрам

        Args:
            error_type: Фильтр по типу ошибки
            severity: Фильтр по серьезности
            operation: Фильтр по операции
            acknowledged: Фильтр по подтверждению
            resolved: Фильтр по разрешению
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            int: Количество найденных отчетов
        """
        filtered_reports = await self.find_by_filters(
            error_type,
            severity,
            operation,
            acknowledged,
            resolved,
            start_date,
            end_date,
            limit=float("inf"),
        )
        return len(filtered_reports)

    async def get_statistics(
        self,
        days: int = 7,
        include_resolved: bool = True,
    ) -> Dict[str, Any]:
        """
        Получить статистику по отчетам

        Args:
            days: Количество дней для статистики
            include_resolved: Включать ли разрешенные отчеты

        Returns:
            Dict[str, Any]: Статистика
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        all_reports = await self.find_all()

        # Фильтруем по дате
        recent_reports = [r for r in all_reports if r.created_at >= start_date]

        if not include_resolved:
            recent_reports = [r for r in recent_reports if not r.resolved]

        total_reports = len(recent_reports)
        acknowledged_reports = len(
            [r for r in recent_reports if r.acknowledged]
        )
        resolved_reports = len([r for r in recent_reports if r.resolved])
        critical_reports = len([r for r in recent_reports if r.is_critical])

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
        }

    async def cleanup_old_reports(self, max_age_days: int) -> int:
        """
        Очистить старые отчеты

        Args:
            max_age_days: Максимальный возраст отчетов в днях

        Returns:
            int: Количество удаленных отчетов
        """
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        old_reports = [
            report_id
            for report_id, report in self._reports.items()
            if report.created_at < cutoff_date
        ]

        for report_id in old_reports:
            del self._reports[report_id]

        deleted_count = len(old_reports)
        self._total_count = len(self._reports)

        return deleted_count

    async def get_pending_reports(self, limit: int = 50) -> list:
        """
        Получить неподтвержденные отчеты

        Args:
            limit: Максимальное количество отчетов

        Returns:
            list: Список неподтвержденных отчетов
        """
        pending_reports = [r for r in self._reports.values() if r.is_pending]

        # Сортируем по времени создания (новые сначала)
        pending_reports.sort(key=lambda r: r.created_at, reverse=True)

        return pending_reports[:limit]

    async def get_critical_reports(self, limit: int = 50) -> list:
        """
        Получить критические отчеты

        Args:
            limit: Максимальное количество отчетов

        Returns:
            list: Список критических отчетов
        """
        critical_reports = [r for r in self._reports.values() if r.is_critical]

        # Сортируем по времени создания (новые сначала)
        critical_reports.sort(key=lambda r: r.created_at, reverse=True)

        return critical_reports[:limit]

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье репозитория

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            total_reports = len(self._reports)
            pending_reports = len(
                await self.get_pending_reports(limit=float("inf"))
            )
            critical_reports = len(
                await self.get_critical_reports(limit=float("inf"))
            )

            return {
                "status": "healthy",
                "total_reports": total_reports,
                "pending_reports": pending_reports,
                "critical_reports": critical_reports,
                "storage_usage_percent": (
                    total_reports / error_reporting_config.MAX_REPORTS_TOTAL
                )
                * 100,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Функции для создания репозитория
async def get_error_report_repository(db=None) -> ErrorReportRepository:
    """Создать репозиторий отчетов об ошибках"""
    return ErrorReportRepository(db)


# Экспорт
__all__ = [
    "ErrorSeverity",
    "ErrorType",
    "ErrorContext",
    "ErrorReport",
    "ErrorReportRepository",
    "get_error_report_repository",
]
