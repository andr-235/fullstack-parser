"""
ErrorReportingService - DDD Application Service для обработки ошибок и отчетов

Мигрирован из app/services/error_reporting_service.py
"""

import traceback
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import structlog


class ErrorReportingService:
    """
    DDD Application Service для создания и управления отчетами об ошибках.

    Предоставляет высокоуровневый интерфейс для:
    - Создания отчетов об ошибках
    - Анализа ошибок
    - Рекомендаций по исправлению
    - Сохранения отчетов в БД
    """

    def __init__(self, db=None, error_repository=None):
        """
        Инициализация ErrorReportingService.

        Args:
            db: Асинхронная сессия базы данных
            error_repository: Репозиторий ошибок
        """
        self.db = db
        self.error_repository = error_repository
        self.logger = structlog.get_logger(__name__)

    # =============== МИГРАЦИЯ ErrorReportingService В DDD ===============

    async def create_error_entry_ddd(
        self,
        error_type: str,
        severity: str,
        message: str,
        details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
    ) -> Dict[str, Any]:
        """
        Создает запись об ошибке (мигрировано из ErrorReportingService)

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
        try:
            stack_trace = None
            if exception:
                stack_trace = "".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                )

            error_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": error_type,
                "severity": severity,
                "message": message,
                "details": details,
                "context": context or {},
                "stack_trace": stack_trace,
                "created_at": datetime.utcnow().isoformat(),
            }

            return error_entry

        except Exception as e:
            self.logger.error(f"Error creating error entry: {e}")
            raise

    async def create_error_report_ddd(
        self,
        operation: str,
        errors: List[Dict[str, Any]],
        recommendations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Создает отчет об ошибках (мигрировано из ErrorReportingService)

        Args:
            operation: Операция, при которой произошли ошибки
            errors: Список ошибок
            recommendations: Рекомендации по исправлению

        Returns:
            Отчет об ошибках
        """
        try:
            # Генерируем рекомендации, если не предоставлены
            if not recommendations:
                recommendations = await self._generate_recommendations_ddd(
                    errors
                )

            # Подсчитываем статистику ошибок
            error_stats = self._calculate_error_statistics(errors)

            error_report = {
                "id": str(uuid.uuid4()),
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat(),
                "errors": errors,
                "error_count": len(errors),
                "recommendations": recommendations,
                "statistics": error_stats,
                "severity_summary": self._summarize_severity(errors),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Сохраняем отчет в БД, если есть репозиторий
            if self.error_repository:
                await self.error_repository.save(error_report)

            # Логируем отчет
            await self._log_error_report_ddd(error_report)

            return error_report

        except Exception as e:
            self.logger.error(f"Error creating error report: {e}")
            raise

    async def create_group_load_error_report_ddd(
        self,
        group_id: int,
        operation: str,
        errors: List[Dict[str, Any]],
        load_duration: Optional[float] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Создает отчет об ошибках загрузки группы (мигрировано из ErrorReportingService)

        Args:
            group_id: ID группы
            operation: Операция загрузки
            errors: Список ошибок
            load_duration: Время загрузки
            retry_count: Количество попыток

        Returns:
            Отчет об ошибках загрузки группы
        """
        try:
            # Создаем базовый отчет об ошибках
            base_report = await self.create_error_report_ddd(
                operation=f"group_load_{operation}", errors=errors
            )

            # Добавляем специфичную для группы информацию
            group_report = {
                **base_report,
                "group_id": group_id,
                "load_duration": load_duration,
                "retry_count": retry_count,
                "success_rate": (1 - len(errors) / max(1, len(errors) + 1))
                * 100,
                "group_context": {
                    "group_id": group_id,
                    "operation": operation,
                    "has_retries": retry_count > 0,
                    "load_time_seconds": load_duration,
                },
            }

            # Сохраняем специфичный отчет
            if self.error_repository:
                await self.error_repository.save_group_load_report(
                    group_report
                )

            return group_report

        except Exception as e:
            self.logger.error(f"Error creating group load error report: {e}")
            raise

    async def analyze_error_patterns_ddd(
        self, time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Анализирует паттерны ошибок за период времени

        Args:
            time_range_hours: Период анализа в часах

        Returns:
            Анализ паттернов ошибок
        """
        try:
            # Получаем все ошибки за период
            if self.error_repository:
                errors = await self.error_repository.find_by_time_range(
                    time_range_hours
                )
            else:
                # Имитация данных для демонстрации
                errors = []

            # Анализируем паттерны
            patterns = {
                "total_errors": len(errors),
                "error_types": {},
                "error_severities": {},
                "common_messages": {},
                "temporal_distribution": {},
                "most_affected_operations": {},
            }

            for error in errors:
                # Подсчитываем типы ошибок
                error_type = error.get("error_type", "unknown")
                patterns["error_types"][error_type] = (
                    patterns["error_types"].get(error_type, 0) + 1
                )

                # Подсчитываем уровни серьезности
                severity = error.get("severity", "unknown")
                patterns["error_severities"][severity] = (
                    patterns["error_severities"].get(severity, 0) + 1
                )

                # Подсчитываем частые сообщения
                message = error.get("message", "")[:100]  # Первые 100 символов
                patterns["common_messages"][message] = (
                    patterns["common_messages"].get(message, 0) + 1
                )

            return {
                "analysis_period_hours": time_range_hours,
                "patterns": patterns,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing error patterns: {e}")
            raise

    async def get_error_reports_ddd(
        self,
        limit: int = 50,
        offset: int = 0,
        severity_filter: Optional[str] = None,
        time_range_hours: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Получает отчеты об ошибках с фильтрацией

        Args:
            limit: Максимальное количество отчетов
            offset: Смещение
            severity_filter: Фильтр по уровню серьезности
            time_range_hours: Ограничение по времени в часах

        Returns:
            Отчеты об ошибках
        """
        try:
            if self.error_repository:
                reports = await self.error_repository.find_with_filters(
                    limit=limit,
                    offset=offset,
                    severity_filter=severity_filter,
                    time_range_hours=time_range_hours,
                )
            else:
                # Имитация данных
                reports = []

            return {
                "reports": reports,
                "total": len(reports),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "severity": severity_filter,
                    "time_range_hours": time_range_hours,
                },
                "has_next": len(reports) == limit,
                "has_prev": offset > 0,
                "retrieved_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting error reports: {e}")
            raise

    async def cleanup_old_reports_ddd(
        self, older_than_days: int = 30
    ) -> Dict[str, Any]:
        """
        Очищает старые отчеты об ошибках

        Args:
            older_than_days: Удалить отчеты старше N дней

        Returns:
            Результат очистки
        """
        try:
            if self.error_repository:
                deleted_count = await self.error_repository.delete_older_than(
                    older_than_days
                )
            else:
                deleted_count = 0

            return {
                "cleanup_completed": True,
                "deleted_reports": deleted_count,
                "older_than_days": older_than_days,
                "cleanup_at": datetime.utcnow().isoformat(),
                "message": f"Deleted {deleted_count} error reports older than {older_than_days} days",
            }

        except Exception as e:
            self.logger.error(f"Error cleaning up old reports: {e}")
            raise

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===============

    async def _generate_recommendations_ddd(
        self, errors: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Генерирует рекомендации по исправлению ошибок
        """
        recommendations = []

        # Анализируем типы ошибок и генерируем рекомендации
        error_types = {}
        severities = {}

        for error in errors:
            error_type = error.get("error_type", "unknown")
            severity = error.get("severity", "low")

            error_types[error_type] = error_types.get(error_type, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1

        # Рекомендации на основе типов ошибок
        if "network" in error_types:
            recommendations.append(
                "Проверьте подключение к интернету и VK API"
            )
            recommendations.append("Увеличьте таймауты для сетевых запросов")

        if "database" in error_types:
            recommendations.append("Проверьте подключение к базе данных")
            recommendations.append("Проверьте достаточность ресурсов БД")

        if "authentication" in error_types:
            recommendations.append("Проверьте токен доступа VK API")
            recommendations.append("Обновите токен, если он истек")

        if severities.get("critical", 0) > 0:
            recommendations.append(
                "Критические ошибки требуют немедленного внимания"
            )
            recommendations.append(
                "Рассмотрите временное отключение проблемных компонентов"
            )

        if len(errors) > 10:
            recommendations.append(
                "Большое количество ошибок - проверьте системные ресурсы"
            )
            recommendations.append(
                "Рассмотрите увеличение лимитов и оптимизацию"
            )

        return recommendations

    def _calculate_error_statistics(
        self, errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Подсчитывает статистику ошибок
        """
        stats = {
            "total": len(errors),
            "by_type": {},
            "by_severity": {},
            "by_hour": {},
            "avg_errors_per_hour": 0,
        }

        for error in errors:
            # По типам
            error_type = error.get("error_type", "unknown")
            stats["by_type"][error_type] = (
                stats["by_type"].get(error_type, 0) + 1
            )

            # По уровням серьезности
            severity = error.get("severity", "unknown")
            stats["by_severity"][severity] = (
                stats["by_severity"].get(severity, 0) + 1
            )

        return stats

    def _summarize_severity(
        self, errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Создает сводку по уровням серьезности
        """
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for error in errors:
            severity = error.get("severity", "low")
            summary[severity] = summary.get(severity, 0) + 1

        return summary

    async def _log_error_report_ddd(self, report: Dict[str, Any]) -> None:
        """
        Логирует отчет об ошибках
        """
        try:
            self.logger.error(
                "Error report generated",
                report_id=report.get("id"),
                operation=report.get("operation"),
                error_count=report.get("error_count"),
                severity_summary=report.get("severity_summary"),
                recommendations_count=len(report.get("recommendations", [])),
            )

            # Логируем каждую ошибку
            for i, error in enumerate(report.get("errors", [])):
                self.logger.error(
                    f"Error {i+1}: {error.get('message', 'Unknown error')}",
                    error_type=error.get("error_type"),
                    severity=error.get("severity"),
                    operation=report.get("operation"),
                )

        except Exception as e:
            self.logger.error(f"Error logging error report: {e}")

    async def get_health_status_ddd(self) -> Dict[str, Any]:
        """
        Получает статус здоровья системы отчетов об ошибках

        Returns:
            Статус здоровья
        """
        try:
            health = {
                "service": "ErrorReportingService",
                "status": "healthy",
                "database_connected": self.db is not None,
                "repository_available": self.error_repository is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Проверяем подключение к БД
            if self.db:
                try:
                    # Простая проверка подключения
                    await self.db.execute("SELECT 1")
                    health["database_status"] = "connected"
                except Exception as e:
                    health["database_status"] = "error"
                    health["database_error"] = str(e)
                    health["status"] = "degraded"

            return health

        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                "service": "ErrorReportingService",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
