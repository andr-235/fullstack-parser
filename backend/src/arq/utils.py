"""
Вспомогательные функции для ARQ модуля

Содержит утилиты для работы с задачами и cron выражениями.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from croniter import croniter  # type: ignore[import-untyped]


def validate_cron_expression(cron_expr: str) -> bool:
    """
    Валидация cron выражения

    Args:
        cron_expr: Cron выражение для проверки

    Returns:
        True если выражение валидно, False в противном случае
    """
    try:
        croniter(cron_expr)
        return True
    except Exception:
        return False


def get_next_cron_run(cron_expr: str, base_time: Optional[datetime] = None) -> Optional[datetime]:
    """
    Получение времени следующего выполнения cron задачи

    Args:
        cron_expr: Cron выражение
        base_time: Базовое время для расчета (по умолчанию текушее время)

    Returns:
        Время следующего выполнения или None если выражение невалидно
    """
    try:
        if base_time is None:
            base_time = datetime.now()

        cron = croniter(cron_expr, base_time)
        return cron.get_next(datetime)
    except Exception:
        return None


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Парсинг строки продолжительности в timedelta

    Поддерживает форматы:
    - "1h 30m 45s" или "1h30m45s"
    - "90s", "30m", "2h"
    - "01:30:45" (HH:MM:SS)

    Args:
        duration_str: Строка с продолжительностью

    Returns:
        timedelta объект или None если парсинг не удался
    """
    try:
        # Попытка парсинга формата HH:MM:SS
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # Парсинг формата с единицами измерения
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, duration_str.replace(' ', ''))

        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)

            return timedelta(hours=hours, minutes=minutes, seconds=seconds)

        return None
    except (ValueError, AttributeError):
        return None


def format_task_result(result: Any, max_length: int = 500) -> str:
    """
    Форматирование результата задачи для логирования

    Args:
        result: Результат задачи
        max_length: Максимальная длина строки

    Returns:
        Отформатированная строка результата
    """
    try:
        if result is None:
            return "None"

        result_str = str(result)

        if len(result_str) > max_length:
            return result_str[:max_length] + "..."

        return result_str
    except Exception as e:
        return f"<ошибка форматирования: {e}>"


def calculate_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, backoff: float = 2.0) -> float:
    """
    Расчет задержки для повторной попытки

    Args:
        attempt: Номер попытки (начиная с 1)
        base_delay: Базовая задержка в секундах
        max_delay: Максимальная задержка в секундах
        backoff: Коэффициент увеличения задержки

    Returns:
        Задержка в секундах
    """
    delay = base_delay * (backoff ** (attempt - 1))
    return min(delay, max_delay)


def generate_task_summary(status_info: Dict[str, Any]) -> Dict[str, str]:
    """
    Генерация краткого summary для задачи

    Args:
        status_info: Информация о статусе задачи

    Returns:
        Dict с краткой информацией
    """
    summary = {
        "job_id": status_info.get("job_id", "unknown"),
        "function": status_info.get("function", "unknown"),
        "status": status_info.get("status", "unknown"),
    }

    # Добавляем время выполнения если доступно
    started_at = status_info.get("started_at")
    finished_at = status_info.get("finished_at")

    if started_at and finished_at:
        try:
            duration = (finished_at - started_at).total_seconds()
            summary["duration"] = f"{duration:.2f}"
        except:
            summary["duration"] = "unknown"

    # Добавляем информацию об ошибке если есть
    if status_info.get("error"):
        summary["has_error"] = True
        summary["error_preview"] = status_info["error"][:100] + "..." if len(status_info["error"]) > 100 else status_info["error"]
    else:
        summary["has_error"] = False

    return summary


def sanitize_function_name(function_name: str) -> str:
    """
    Очистка имени функции от потенциально опасных символов

    Args:
        function_name: Имя функции

    Returns:
        Очищенное имя функции
    """
    # Удаляем все символы кроме букв, цифр и подчеркиваний
    return re.sub(r'[^\w]', '', function_name)
