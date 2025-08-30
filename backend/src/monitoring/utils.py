"""
Вспомогательные функции модуля Monitoring

Содержит утилиты для работы с мониторингом групп VK
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from .constants import (
    MAX_GROUP_NAME_LENGTH,
    MAX_OWNER_ID_LENGTH,
    ALLOWED_MONITORING_STATUSES,
    ALLOWED_BULK_ACTIONS,
    ALLOWED_NOTIFICATION_CHANNELS,
)


def validate_monitoring_creation_data(
    data: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Валидировать данные создания мониторинга

    Args:
        data: Данные для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    # Проверка обязательных полей
    required_fields = ["group_id", "group_name", "owner_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Обязательное поле '{field}' не заполнено"

    # Валидация group_id
    group_id = data["group_id"]
    if not isinstance(group_id, int) or group_id <= 0:
        return False, "group_id должен быть положительным целым числом"

    # Валидация group_name
    group_name = str(data["group_name"]).strip()
    if len(group_name) > MAX_GROUP_NAME_LENGTH:
        return (
            False,
            f"Название группы слишком длинное (макс {MAX_GROUP_NAME_LENGTH} символов)",
        )

    if not validate_group_name(group_name):
        return False, "Название группы содержит недопустимые символы"

    # Валидация owner_id
    owner_id = str(data["owner_id"]).strip()
    if len(owner_id) > MAX_OWNER_ID_LENGTH:
        return (
            False,
            f"ID владельца слишком длинный (макс {MAX_OWNER_ID_LENGTH} символов)",
        )

    # Валидация статуса
    if "status" in data:
        status = data["status"]
        if status not in ALLOWED_MONITORING_STATUSES:
            return (
                False,
                f"Неверный статус. Допустимые: {', '.join(ALLOWED_MONITORING_STATUSES)}",
            )

    # Валидация конфигурации
    if "config" in data:
        config = data["config"]
        if not isinstance(config, dict):
            return False, "config должен быть объектом"
        else:
            config_errors = validate_monitoring_config(config)
            if config_errors:
                return (
                    False,
                    f"Ошибки в конфигурации: {'; '.join(config_errors)}",
                )

    return True, ""


def validate_monitoring_config(config: Dict[str, Any]) -> List[str]:
    """
    Валидировать конфигурацию мониторинга

    Args:
        config: Конфигурация для валидации

    Returns:
        List[str]: Список ошибок валидации
    """
    errors = []

    # Валидация интервала
    if "interval_minutes" in config:
        interval = config["interval_minutes"]
        if not isinstance(interval, int) or not (1 <= interval <= 1440):
            errors.append("interval_minutes должен быть от 1 до 1440")

    # Валидация максимального количества одновременных задач
    if "max_concurrent_groups" in config:
        concurrent = config["max_concurrent_groups"]
        if not isinstance(concurrent, int) or not (1 <= concurrent <= 100):
            errors.append("max_concurrent_groups должен быть от 1 до 100")

    # Валидация максимального количества повторных попыток
    if "max_retries" in config:
        retries = config["max_retries"]
        if not isinstance(retries, int) or not (0 <= retries <= 10):
            errors.append("max_retries должен быть от 0 до 10")

    # Валидация таймаута
    if "timeout_seconds" in config:
        timeout = config["timeout_seconds"]
        if not isinstance(timeout, (int, float)) or not (5 <= timeout <= 300):
            errors.append("timeout_seconds должен быть от 5 до 300")

    # Валидация каналов уведомлений
    if "notification_channels" in config:
        channels = config["notification_channels"]
        if not isinstance(channels, list):
            errors.append("notification_channels должен быть списком")
        else:
            for channel in channels:
                if channel not in ALLOWED_NOTIFICATION_CHANNELS:
                    errors.append(
                        f"Неподдерживаемый канал уведомлений: {channel}"
                    )

    # Валидация булевых полей
    bool_fields = ["enable_auto_retry", "enable_notifications"]
    for field in bool_fields:
        if field in config:
            value = config[field]
            if not isinstance(value, bool):
                errors.append(f"{field} должен быть boolean")

    return errors


def validate_group_name(name: str) -> bool:
    """
    Валидировать название группы

    Args:
        name: Название группы для валидации

    Returns:
        bool: Валидно ли название
    """
    if not name:
        return False

    # Разрешены буквы, цифры, пробелы, дефисы, подчеркивания
    pattern = r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-_]+$"
    return bool(re.match(pattern, name))


def validate_bulk_action_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Валидировать данные массового действия

    Args:
        data: Данные для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    # Проверка обязательных полей
    required_fields = ["monitoring_ids", "action"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Обязательное поле '{field}' не заполнено"

    # Валидация monitoring_ids
    monitoring_ids = data["monitoring_ids"]
    if not isinstance(monitoring_ids, list):
        return False, "monitoring_ids должен быть списком"

    if len(monitoring_ids) == 0:
        return False, "monitoring_ids не может быть пустым"

    if len(monitoring_ids) > 100:
        return False, "Максимум 100 мониторингов за один запрос"

    # Проверка, что все ID - строки
    for i, monitoring_id in enumerate(monitoring_ids):
        if not isinstance(monitoring_id, str):
            return False, f"monitoring_ids[{i}] должен быть строкой"

    # Валидация действия
    action = data["action"]
    if action not in ALLOWED_BULK_ACTIONS:
        return (
            False,
            f"Неверное действие. Допустимые: {', '.join(ALLOWED_BULK_ACTIONS)}",
        )

    return True, ""


def calculate_monitoring_schedule(
    last_run_at: Optional[datetime], interval_minutes: int, status: str
) -> Optional[datetime]:
    """
    Вычислить следующее время запуска мониторинга

    Args:
        last_run_at: Время последнего запуска
        interval_minutes: Интервал в минутах
        status: Статус мониторинга

    Returns:
        Optional[datetime]: Время следующего запуска или None
    """
    if status != "active":
        return None

    if last_run_at is None:
        # Первый запуск - через интервал от текущего времени
        return datetime.utcnow() + timedelta(minutes=interval_minutes)

    # Следующий запуск - через интервал от последнего
    return last_run_at + timedelta(minutes=interval_minutes)


def calculate_monitoring_progress(
    total_runs: int, successful_runs: int, failed_runs: int
) -> Dict[str, float]:
    """
    Вычислить прогресс мониторинга

    Args:
        total_runs: Общее количество запусков
        successful_runs: Успешных запусков
        failed_runs: Неудачных запусков

    Returns:
        Dict[str, float]: Показатели прогресса
    """
    if total_runs == 0:
        return {
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "completion_rate": 0.0,
        }

    success_rate = (successful_runs / total_runs) * 100
    failure_rate = (failed_runs / total_runs) * 100
    completion_rate = ((successful_runs + failed_runs) / total_runs) * 100

    return {
        "success_rate": round(success_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "completion_rate": round(completion_rate, 2),
    }


def format_monitoring_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Форматировать результат мониторинга для API

    Args:
        result: Результат мониторинга

    Returns:
        Dict[str, Any]: Форматированный результат
    """
    formatted = result.copy()

    # Форматирование времени
    time_fields = ["started_at", "completed_at"]
    for field in time_fields:
        if field in formatted and isinstance(formatted[field], datetime):
            formatted[field] = formatted[field].isoformat()

    # Форматирование числовых полей
    float_fields = ["processing_time", "average_processing_time"]
    for field in float_fields:
        if field in formatted and formatted[field] is not None:
            formatted[field] = round(formatted[field], 2)

    # Форматирование списков
    if "keywords_found" in formatted and formatted["keywords_found"]:
        formatted["keywords_found"] = sorted(
            list(set(formatted["keywords_found"]))
        )

    if "errors" in formatted and formatted["errors"]:
        formatted["errors"] = [str(error) for error in formatted["errors"]]

    return formatted


def generate_monitoring_report(
    monitoring: Dict[str, Any],
    results: List[Dict[str, Any]],
    period_start: datetime,
    period_end: datetime,
) -> Dict[str, Any]:
    """
    Сгенерировать отчет по мониторингу

    Args:
        monitoring: Данные мониторинга
        results: Результаты мониторинга
        period_start: Начало периода
        period_end: Конец периода

    Returns:
        Dict[str, Any]: Отчет
    """
    # Фильтрация результатов по периоду
    period_results = [
        result
        for result in results
        if result.get("started_at")
        and period_start <= result["started_at"] <= period_end
    ]

    if not period_results:
        return {
            "monitoring_id": monitoring["id"],
            "group_id": monitoring["group_id"],
            "group_name": monitoring["group_name"],
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "summary": {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_posts": 0,
                "total_comments": 0,
                "avg_processing_time": 0.0,
            },
        }

    # Расчет статистики
    total_runs = len(period_results)
    successful_runs = sum(1 for r in period_results if not r.get("errors"))
    failed_runs = total_runs - successful_runs
    total_posts = sum(r.get("posts_found", 0) for r in period_results)
    total_comments = sum(r.get("comments_found", 0) for r in period_results)

    processing_times = [
        r.get("processing_time", 0)
        for r in period_results
        if r.get("processing_time") is not None
    ]
    avg_processing_time = (
        sum(processing_times) / len(processing_times)
        if processing_times
        else 0
    )

    return {
        "monitoring_id": monitoring["id"],
        "group_id": monitoring["group_id"],
        "group_name": monitoring["group_name"],
        "period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat(),
        },
        "summary": {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "avg_processing_time": round(avg_processing_time, 2),
        },
        "results": period_results,
    }


def create_monitoring_notification(
    monitoring: Dict[str, Any],
    notification_type: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Создать уведомление о мониторинге

    Args:
        monitoring: Данные мониторинга
        notification_type: Тип уведомления
        message: Текст уведомления
        metadata: Дополнительные данные

    Returns:
        Dict[str, Any]: Уведомление
    """
    return {
        "monitoring_id": monitoring["id"],
        "group_id": monitoring["group_id"],
        "group_name": monitoring["group_name"],
        "type": notification_type,
        "message": message,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
    }


def calculate_monitoring_uptime(
    monitoring: Dict[str, Any], results: List[Dict[str, Any]]
) -> float:
    """
    Вычислить uptime мониторинга

    Args:
        monitoring: Данные мониторинга
        results: Результаты мониторинга

    Returns:
        float: Процент uptime
    """
    if not results:
        return 0.0

    # Группировка результатов по дням
    daily_results = {}
    for result in results:
        if not result.get("started_at"):
            continue

        day = result["started_at"].date()
        if day not in daily_results:
            daily_results[day] = []

        daily_results[day].append(result)

    if not daily_results:
        return 0.0

    # Расчет uptime по дням
    total_days = len(daily_results)
    successful_days = 0

    for day_results in daily_results.values():
        successful_runs = sum(1 for r in day_results if not r.get("errors"))
        if successful_runs > 0:  # Хотя бы один успешный запуск в день
            successful_days += 1

    return (successful_days / total_days) * 100


def validate_monitoring_schedule_conflict(
    monitoring: Dict[str, Any], existing_monitorings: List[Dict[str, Any]]
) -> List[str]:
    """
    Проверить конфликты расписания мониторинга

    Args:
        monitoring: Мониторинг для проверки
        existing_monitorings: Существующие мониторинги

    Returns:
        List[str]: Список конфликтов
    """
    conflicts = []

    # Проверка на одинаковые группы
    for existing in existing_monitorings:
        if existing["group_id"] == monitoring["group_id"] and existing[
            "id"
        ] != monitoring.get("id"):
            conflicts.append(
                f"Группа {monitoring['group_id']} уже мониторится"
            )

    # Проверка на перегрузку (слишком много мониторингов на одного владельца)
    owner_monitorings = [
        m
        for m in existing_monitorings
        if m["owner_id"] == monitoring["owner_id"]
        and m["id"] != monitoring.get("id")
    ]

    if len(owner_monitorings) >= 50:  # Лимит на пользователя
        conflicts.append(
            "Превышен лимит количества мониторингов на пользователя"
        )

    return conflicts


# Экспорт всех функций
__all__ = [
    "validate_monitoring_creation_data",
    "validate_monitoring_config",
    "validate_group_name",
    "validate_bulk_action_data",
    "calculate_monitoring_schedule",
    "calculate_monitoring_progress",
    "format_monitoring_result",
    "generate_monitoring_report",
    "create_monitoring_notification",
    "calculate_monitoring_uptime",
    "validate_monitoring_schedule_conflict",
]
