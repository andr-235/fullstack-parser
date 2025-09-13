"""
Вспомогательные функции модуля Health
"""

from datetime import datetime
from typing import Any, Dict, Optional


def calculate_health_score(health_status: Dict[str, Any]) -> float:
    """Вычислить оценку здоровья системы (0-100)"""
    if not health_status or "components" not in health_status:
        return 0.0

    components = health_status["components"]
    if not components:
        return 100.0

    healthy_count = sum(1 for status in components.values() if status == "healthy")
    return (healthy_count / len(components)) * 100.0


def format_health_for_prometheus(health_data: Dict[str, Any]) -> str:
    """Форматировать данные здоровья для Prometheus"""
    lines = []

    # Общий статус
    status_value = 1 if health_data.get("status") == "healthy" else 0
    lines.append(f'health_status{{service="{health_data.get("service", "unknown")}"}} {status_value}')

    # Компоненты
    components = health_data.get("components", {})
    for component, status in components.items():
        status_value = 1 if status == "healthy" else 0
        lines.append(f'health_component_status{{component="{component}"}} {status_value}')

    # Uptime
    uptime = health_data.get("uptime_seconds", 0)
    lines.append(f'health_uptime_seconds{{service="{health_data.get("service", "unknown")}"}} {uptime}')

    return "\n".join(lines)


def create_health_alert(
    component: str,
    old_status: str,
    new_status: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Создать алерт о изменении здоровья"""
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


def sanitize_health_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Очистить детали здоровья от чувствительной информации"""
    sanitized = {}

    for key, value in details.items():
        if key.lower() in ["password", "token", "secret", "key"]:
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_health_details(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_health_details({"item": item})["item"] if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


__all__ = [
    "calculate_health_score",
    "format_health_for_prometheus",
    "create_health_alert",
    "sanitize_health_details",
]
