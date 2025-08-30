"""
Вспомогательные функции модуля Error Reporting

Содержит утилиты для работы с отчетами об ошибках
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from .constants import (
    REGEX_ERROR_REPORT_ID,
    REGEX_EMAIL,
    REGEX_IP_ADDRESS,
    MAX_ERROR_MESSAGE_LENGTH,
    MAX_STACK_TRACE_LENGTH,
    MAX_ADDITIONAL_CONTEXT_SIZE,
)


def validate_error_report_id(report_id: str) -> Tuple[bool, str]:
    """
    Валидировать ID отчета об ошибке

    Args:
        report_id: ID отчета для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not report_id or not report_id.strip():
        return False, "ID отчета об ошибке не может быть пустым"

    report_id = report_id.strip()

    if not re.match(REGEX_ERROR_REPORT_ID, report_id):
        return False, "Неверный формат ID отчета об ошибке"

    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Валидировать email адрес

    Args:
        email: Email для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not email:
        return True, ""  # Email опционален

    email = email.strip()

    if not re.match(REGEX_EMAIL, email):
        return False, "Неверный формат email адреса"

    return True, ""


def validate_ip_address(ip: str) -> Tuple[bool, str]:
    """
    Валидировать IP адрес

    Args:
        ip: IP адрес для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not ip:
        return True, ""  # IP опционален

    ip = ip.strip()

    if not re.match(REGEX_IP_ADDRESS, ip):
        return False, "Неверный формат IP адреса"

    return True, ""


def sanitize_error_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очистить контекст ошибки от чувствительной информации

    Args:
        context: Контекст ошибки

    Returns:
        Dict[str, Any]: Очищенный контекст
    """
    from .config import error_reporting_config

    if not error_reporting_config.should_filter_sensitive_data():
        return context.copy()

    sanitized = {}

    for key, value in context.items():
        # Проверяем, является ли ключ чувствительным
        if any(
            sensitive_key in key.lower()
            for sensitive_key in error_reporting_config.get_sensitive_keys()
        ):
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_error_context(value)
        elif isinstance(value, list):
            sanitized[key] = [
                (
                    sanitize_error_context({"item": item})["item"]
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def truncate_error_message(
    message: str, max_length: int = MAX_ERROR_MESSAGE_LENGTH
) -> str:
    """
    Обрезать сообщение об ошибке до максимальной длины

    Args:
        message: Сообщение об ошибке
        max_length: Максимальная длина

    Returns:
        str: Обрезанное сообщение
    """
    if not message:
        return ""

    if len(message) <= max_length:
        return message

    # Обрезаем и добавляем индикатор
    truncated = message[: max_length - 3] + "..."
    return truncated


def truncate_stack_trace(
    stack_trace: str, max_length: int = MAX_STACK_TRACE_LENGTH
) -> str:
    """
    Обрезать трассировку стека до максимальной длины

    Args:
        stack_trace: Трассировка стека
        max_length: Максимальная длина

    Returns:
        str: Обрезанная трассировка
    """
    if not stack_trace:
        return ""

    if len(stack_trace) <= max_length:
        return stack_trace

    # Обрезаем и добавляем индикатор
    truncated = stack_trace[: max_length - 3] + "..."
    return truncated


def calculate_error_report_metrics(
    reports: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Вычислить метрики по отчетам об ошибках

    Args:
        reports: Список отчетов

    Returns:
        Dict[str, Any]: Метрики
    """
    if not reports:
        return {
            "total_reports": 0,
            "acknowledged_reports": 0,
            "resolved_reports": 0,
            "critical_reports": 0,
            "average_time_to_acknowledge": 0,
            "average_time_to_resolve": 0,
        }

    total_reports = len(reports)
    acknowledged_reports = sum(
        1 for r in reports if r.get("status", {}).get("acknowledged")
    )
    resolved_reports = sum(
        1 for r in reports if r.get("status", {}).get("resolved")
    )
    critical_reports = sum(
        1 for r in reports if r.get("severity") == "critical"
    )

    # Вычисляем среднее время до подтверждения
    acknowledge_times = [
        r.get("timestamps", {}).get("time_to_acknowledge")
        for r in reports
        if r.get("timestamps", {}).get("time_to_acknowledge") is not None
    ]
    average_time_to_acknowledge = (
        sum(acknowledge_times) / len(acknowledge_times)
        if acknowledge_times
        else 0
    )

    # Вычисляем среднее время до разрешения
    resolve_times = [
        r.get("timestamps", {}).get("time_to_resolve")
        for r in reports
        if r.get("timestamps", {}).get("time_to_resolve") is not None
    ]
    average_time_to_resolve = (
        sum(resolve_times) / len(resolve_times) if resolve_times else 0
    )

    return {
        "total_reports": total_reports,
        "acknowledged_reports": acknowledged_reports,
        "resolved_reports": resolved_reports,
        "critical_reports": critical_reports,
        "acknowledgment_rate": (
            acknowledged_reports / total_reports if total_reports > 0 else 0
        ),
        "resolution_rate": (
            resolved_reports / total_reports if total_reports > 0 else 0
        ),
        "average_time_to_acknowledge": round(average_time_to_acknowledge, 2),
        "average_time_to_resolve": round(average_time_to_resolve, 2),
    }


def group_error_reports_by_type(
    reports: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Группировать отчеты об ошибках по типу

    Args:
        reports: Список отчетов

    Returns:
        Dict[str, List[Dict[str, Any]]]: Группированные отчеты
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for report in reports:
        error_type = report.get("error_type", "unknown")
        if error_type not in grouped:
            grouped[error_type] = []
        grouped[error_type].append(report)

    return grouped


def group_error_reports_by_severity(
    reports: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Группировать отчеты об ошибках по серьезности

    Args:
        reports: Список отчетов

    Returns:
        Dict[str, List[Dict[str, Any]]]: Группированные отчеты
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for report in reports:
        severity = report.get("severity", "medium")
        if severity not in grouped:
            grouped[severity] = []
        grouped[severity].append(report)

    return grouped


def find_similar_error_reports(
    target_report: Dict[str, Any],
    all_reports: List[Dict[str, Any]],
    similarity_threshold: float = 0.8,
) -> List[Dict[str, Any]]:
    """
    Найти похожие отчеты об ошибках

    Args:
        target_report: Целевой отчет
        all_reports: Все отчеты для поиска
        similarity_threshold: Порог похожести

    Returns:
        List[Dict[str, Any]]: Похожие отчеты
    """
    similar_reports = []
    target_message = target_report.get("message", "").lower()
    target_stack = target_report.get("stack_trace", "").lower()

    for report in all_reports:
        if report["id"] == target_report["id"]:
            continue

        message = report.get("message", "").lower()
        stack = report.get("stack_trace", "").lower()

        # Вычисляем простую похожесть
        message_similarity = calculate_string_similarity(
            target_message, message
        )
        stack_similarity = calculate_string_similarity(target_stack, stack)

        # Общая похожесть
        overall_similarity = (message_similarity + stack_similarity) / 2

        if overall_similarity >= similarity_threshold:
            report_copy = report.copy()
            report_copy["similarity_score"] = round(overall_similarity, 2)
            similar_reports.append(report_copy)

    return similar_reports


def calculate_string_similarity(str1: str, str2: str) -> float:
    """
    Вычислить похожесть строк (простая реализация)

    Args:
        str1: Первая строка
        str2: Вторая строка

    Returns:
        float: Коэффициент похожести (0-1)
    """
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0

    # Простая похожесть на основе общих слов
    words1 = set(str1.split())
    words2 = set(str2.split())

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def format_error_report_for_export(
    report: Dict[str, Any], format: str = "json"
) -> str:
    """
    Форматировать отчет об ошибке для экспорта

    Args:
        report: Отчет об ошибке
        format: Формат экспорта

    Returns:
        str: Форматированный отчет
    """
    if format == "json":
        return json.dumps(report, indent=2, default=str)
    elif format == "csv":
        return format_error_report_as_csv(report)
    else:
        return json.dumps(report, default=str)


def format_error_report_as_csv(report: Dict[str, Any]) -> str:
    """
    Форматировать отчет об ошибке как CSV

    Args:
        report: Отчет об ошибке

    Returns:
        str: CSV строка
    """
    fields = [
        report.get("id", ""),
        report.get("error_type", ""),
        report.get("severity", ""),
        report.get("message", "").replace("\n", " ").replace(",", ";"),
        report.get("context", {}).get("operation", ""),
        report.get("status", {}).get("acknowledged", False),
        report.get("status", {}).get("resolved", False),
        report.get("timestamps", {}).get("created_at", ""),
    ]

    return ",".join(f'"{field}"' for field in fields)


def generate_error_report_summary(
    reports: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Сгенерировать сводку по отчетам об ошибках

    Args:
        reports: Список отчетов

    Returns:
        Dict[str, Any]: Сводка
    """
    if not reports:
        return {
            "total_reports": 0,
            "summary": "Нет отчетов об ошибках",
            "recommendations": [],
        }

    metrics = calculate_error_report_metrics(reports)

    # Анализируем и даем рекомендации
    recommendations = []

    if metrics["acknowledgment_rate"] < 0.8:
        recommendations.append(
            "Улучшить скорость подтверждения отчетов об ошибках"
        )

    if metrics["resolution_rate"] < 0.7:
        recommendations.append("Улучшить скорость разрешения ошибок")

    if metrics["critical_reports"] > 0:
        recommendations.append(
            f"Обратить внимание на {metrics['critical_reports']} критических ошибок"
        )

    if metrics["average_time_to_resolve"] > 24:  # больше суток
        recommendations.append("Сократить среднее время разрешения ошибок")

    # Группировка по типам
    by_type = group_error_reports_by_type(reports)
    most_common_type = (
        max(by_type.keys(), key=lambda k: len(by_type[k])) if by_type else None
    )

    # Группировка по серьезности
    by_severity = group_error_reports_by_severity(reports)
    severity_distribution = {k: len(v) for k, v in by_severity.items()}

    return {
        "total_reports": metrics["total_reports"],
        "metrics": metrics,
        "severity_distribution": severity_distribution,
        "most_common_error_type": most_common_type,
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat(),
    }


def check_error_report_timeout(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Проверить таймауты отчета об ошибке

    Args:
        report: Отчет об ошибке

    Returns:
        Dict[str, Any]: Результат проверки таймаутов
    """
    from .config import error_reporting_config

    result = {
        "report_id": report["id"],
        "acknowledge_timeout": False,
        "resolve_timeout": False,
        "warnings": [],
    }

    created_at = datetime.fromisoformat(report["timestamps"]["created_at"])
    now = datetime.utcnow()

    # Проверяем таймаут подтверждения
    if not report["status"]["acknowledged"]:
        acknowledge_deadline = created_at + timedelta(
            hours=error_reporting_config.ACKNOWLEDGE_TIMEOUT_HOURS
        )
        if now > acknowledge_deadline:
            result["acknowledge_timeout"] = True
            result["warnings"].append(
                f"Просрочено подтверждение на {(now - acknowledge_deadline).total_seconds() / 3600:.1f} часов"
            )

    # Проверяем таймаут разрешения
    if report["status"]["acknowledged"] and not report["status"]["resolved"]:
        acknowledged_at = datetime.fromisoformat(
            report["status"]["acknowledged_at"]
        )
        resolve_deadline = acknowledged_at + timedelta(
            hours=error_reporting_config.RESOLVE_TIMEOUT_HOURS
        )
        if now > resolve_deadline:
            result["resolve_timeout"] = True
            result["warnings"].append(
                f"Просрочено разрешение на {(now - resolve_deadline).total_seconds() / 3600:.1f} часов"
            )

    return result


# Экспорт всех функций
__all__ = [
    "validate_error_report_id",
    "validate_email",
    "validate_ip_address",
    "sanitize_error_context",
    "truncate_error_message",
    "truncate_stack_trace",
    "calculate_error_report_metrics",
    "group_error_reports_by_type",
    "group_error_reports_by_severity",
    "find_similar_error_reports",
    "calculate_string_similarity",
    "format_error_report_for_export",
    "format_error_report_as_csv",
    "generate_error_report_summary",
    "check_error_report_timeout",
]
