"""
Вспомогательные функции модуля Health

Содержит утилиты для работы с проверками здоровья системы
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta


def validate_component_name(component_name: str) -> Tuple[bool, str]:
    """
    Валидировать название компонента

    Args:
        component_name: Название компонента

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not component_name or not component_name.strip():
        return False, "Название компонента не может быть пустым"

    component_name = component_name.strip()

    # Проверяем длину
    if len(component_name) > 50:
        return False, "Название компонента слишком длинное (макс 50 символов)"

    # Проверяем допустимые символы
    from .constants import REGEX_COMPONENT_NAME
    import re

    if not re.match(REGEX_COMPONENT_NAME, component_name):
        return (
            False,
            "Название компонента может содержать только буквы, цифры, _ и -",
        )

    return True, ""


def validate_health_status(status: str) -> Tuple[bool, str]:
    """
    Валидировать статус здоровья

    Args:
        status: Статус здоровья

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    from .constants import REGEX_HEALTH_STATUS
    import re

    if not status or not status.strip():
        return False, "Статус здоровья не может быть пустым"

    status = status.strip()

    if not re.match(REGEX_HEALTH_STATUS, status):
        return False, "Неверный статус здоровья"

    return True, ""


def calculate_health_score(health_status: Dict[str, Any]) -> float:
    """
    Вычислить оценку здоровья системы

    Args:
        health_status: Статус здоровья системы

    Returns:
        float: Оценка здоровья (0-100)
    """
    if not health_status or "components" not in health_status:
        return 0.0

    components = health_status["components"]
    if not components:
        return 100.0

    total_components = len(components)
    healthy_components = sum(
        1 for status in components.values() if status == "healthy"
    )

    # Вес компонентов (критические компоненты имеют больший вес)
    from .config import health_config

    critical_components = set(health_config.CRITICAL_COMPONENTS)

    weighted_score = 0.0
    total_weight = 0.0

    for component, status in components.items():
        weight = 2.0 if component in critical_components else 1.0
        total_weight += weight

        if status == "healthy":
            weighted_score += weight * 1.0
        elif status == "degraded":
            weighted_score += weight * 0.5
        elif status == "warning":
            weighted_score += weight * 0.75
        # unhealthy, critical, unknown = 0

    if total_weight == 0:
        return 100.0

    return (weighted_score / total_weight) * 100.0


def aggregate_health_statuses(
    statuses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Агрегировать несколько статусов здоровья

    Args:
        statuses: Список статусов здоровья

    Returns:
        Dict[str, Any]: Агрегированный статус
    """
    if not statuses:
        return {
            "status": "unknown",
            "total_checks": 0,
            "healthy_checks": 0,
            "unhealthy_checks": 0,
            "average_score": 0.0,
        }

    total_checks = len(statuses)
    healthy_checks = sum(
        1 for status in statuses if status.get("status") == "healthy"
    )
    unhealthy_checks = total_checks - healthy_checks

    scores = [calculate_health_score(status) for status in statuses]
    average_score = sum(scores) / len(scores) if scores else 0.0

    # Определяем общий статус
    if average_score >= 90:
        overall_status = "healthy"
    elif average_score >= 70:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return {
        "status": overall_status,
        "total_checks": total_checks,
        "healthy_checks": healthy_checks,
        "unhealthy_checks": unhealthy_checks,
        "average_score": round(average_score, 2),
        "min_score": min(scores) if scores else 0.0,
        "max_score": max(scores) if scores else 0.0,
    }


def format_health_response(
    health_data: Dict[str, Any], format: str = "json"
) -> str:
    """
    Форматировать ответ о здоровье

    Args:
        health_data: Данные здоровья
        format: Формат ответа

    Returns:
        str: Форматированный ответ
    """
    if format == "json":
        return json.dumps(health_data, indent=2, default=str)
    elif format == "prometheus":
        return format_health_for_prometheus(health_data)
    else:
        return json.dumps(health_data, default=str)


def format_health_for_prometheus(health_data: Dict[str, Any]) -> str:
    """
    Форматировать данные здоровья для Prometheus

    Args:
        health_data: Данные здоровья

    Returns:
        str: Формат Prometheus
    """
    lines = []

    # Общий статус
    status_value = get_prometheus_status_value(
        health_data.get("status", "unknown")
    )
    lines.append(
        f'health_status{{service="{health_data.get("service", "unknown")}"}} {status_value}'
    )

    # Компоненты
    components = health_data.get("components", {})
    for component, status in components.items():
        status_value = get_prometheus_status_value(status)
        lines.append(
            f'health_component_status{{component="{component}"}} {status_value}'
        )

    # Uptime
    uptime = health_data.get("uptime_seconds", 0)
    lines.append(
        f'health_uptime_seconds{{service="{health_data.get("service", "unknown")}"}} {uptime}'
    )

    return "\n".join(lines)


def get_prometheus_status_value(status: str) -> int:
    """
    Получить числовое значение статуса для Prometheus

    Args:
        status: Статус здоровья

    Returns:
        int: Числовое значение
    """
    status_map = {
        "healthy": 1,
        "ready": 1,
        "alive": 1,
        "degraded": 0,
        "warning": 0,
        "unhealthy": 0,
        "critical": 0,
        "not_ready": 0,
        "dead": 0,
        "unknown": -1,
    }

    return status_map.get(status, -1)


def create_health_alert(
    component: str,
    old_status: str,
    new_status: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Создать алерт о изменении здоровья

    Args:
        component: Название компонента
        old_status: Старый статус
        new_status: Новый статус
        details: Дополнительные детали

    Returns:
        Dict[str, Any]: Алерт
    """
    severity = "info"
    if new_status in ["unhealthy", "critical"]:
        severity = "error"
    elif new_status in ["degraded", "warning"]:
        severity = "warning"

    return {
        "alert_type": "health_status_change",
        "component": component,
        "old_status": old_status,
        "new_status": new_status,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {},
    }


def check_health_trends(
    history: List[Dict[str, Any]], time_window_minutes: int = 60
) -> Dict[str, Any]:
    """
    Проверить тенденции здоровья

    Args:
        history: История проверок
        time_window_minutes: Временное окно в минутах

    Returns:
        Dict[str, Any]: Тенденции здоровья
    """
    if not history:
        return {"trend": "stable", "description": "Недостаточно данных"}

    # Фильтруем по временному окну
    cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
    recent_history = [
        item
        for item in history
        if datetime.fromisoformat(item["checked_at"]) > cutoff_time
    ]

    if len(recent_history) < 2:
        return {"trend": "stable", "description": "Недостаточно данных"}

    # Анализируем тенденции
    statuses = [item["status"] for item in recent_history]
    healthy_count = sum(
        1 for status in statuses if status in ["healthy", "ready", "alive"]
    )
    unhealthy_count = len(statuses) - healthy_count

    # Простая логика определения тенденций
    if unhealthy_count == 0:
        trend = "improving"
        description = "Все проверки успешны"
    elif unhealthy_count == len(statuses):
        trend = "degrading"
        description = "Все проверки неуспешны"
    elif statuses[0] in ["healthy", "ready", "alive"] and statuses[-1] not in [
        "healthy",
        "ready",
        "alive",
    ]:
        trend = "degrading"
        description = "Статус ухудшается"
    elif statuses[0] not in ["healthy", "ready", "alive"] and statuses[-1] in [
        "healthy",
        "ready",
        "alive",
    ]:
        trend = "improving"
        description = "Статус улучшается"
    else:
        trend = "stable"
        description = "Статус стабильный"

    return {
        "trend": trend,
        "description": description,
        "total_checks": len(recent_history),
        "healthy_ratio": healthy_count / len(recent_history),
        "time_window_minutes": time_window_minutes,
    }


def generate_health_report(
    health_status: Dict[str, Any],
    history: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Сгенерировать отчет о здоровье системы

    Args:
        health_status: Текущий статус здоровья
        history: История проверок
        metrics: Метрики

    Returns:
        Dict[str, Any]: Отчет о здоровье
    """
    score = calculate_health_score(health_status)
    trends = check_health_trends(history)

    # Рекомендации
    recommendations = []
    if score < 50:
        recommendations.append(
            "Критическое состояние системы - требуется немедленное вмешательство"
        )
    elif score < 80:
        recommendations.append(
            "Система в degraded состоянии - проверьте компоненты"
        )
    elif score < 90:
        recommendations.append(
            "Система работает нормально, но есть предупреждения"
        )

    unhealthy_components = []
    if "components" in health_status:
        for component, status in health_status["components"].items():
            if status not in ["healthy", "ready", "alive"]:
                unhealthy_components.append(f"{component}: {status}")

    if unhealthy_components:
        recommendations.append(
            f"Проверьте компоненты: {', '.join(unhealthy_components)}"
        )

    return {
        "report_generated_at": datetime.utcnow().isoformat(),
        "overall_score": round(score, 2),
        "status": health_status.get("status", "unknown"),
        "trends": trends,
        "recommendations": recommendations,
        "unhealthy_components": unhealthy_components,
        "metrics_summary": {
            "total_checks": metrics.get("total_checks", 0),
            "success_rate": round(metrics.get("success_rate", 0) * 100, 2),
            "average_response_time_ms": metrics.get(
                "average_response_time_ms", 0
            ),
        },
        "uptime_seconds": health_status.get("uptime_seconds"),
    }


def sanitize_health_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Очистить детали здоровья от чувствительной информации

    Args:
        details: Детали здоровья

    Returns:
        Dict[str, Any]: Очищенные детали
    """
    sanitized = {}

    for key, value in details.items():
        # Не включаем чувствительную информацию
        if key.lower() in ["password", "token", "secret", "key"]:
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_health_details(value)
        elif isinstance(value, list):
            sanitized[key] = [
                (
                    sanitize_health_details({"item": item})["item"]
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


# Экспорт всех функций
__all__ = [
    "validate_component_name",
    "validate_health_status",
    "calculate_health_score",
    "aggregate_health_statuses",
    "format_health_response",
    "format_health_for_prometheus",
    "get_prometheus_status_value",
    "create_health_alert",
    "check_health_trends",
    "generate_health_report",
    "sanitize_health_details",
]
