"""
Утилиты для работы с временем и часовыми поясами
"""

from datetime import datetime, timezone

import pytz


def get_vladivostok_timezone() -> pytz.timezone:
    """Получить часовой пояс Владивостока"""
    return pytz.timezone("Asia/Vladivostok")


def utc_to_vladivostok(utc_time: datetime) -> datetime:
    """
    Конвертировать UTC время в время Владивостока

    Args:
        utc_time: Время в UTC

    Returns:
        Время в часовом поясе Владивостока
    """
    if utc_time.tzinfo is None:
        # Если время без часового пояса, считаем что это UTC
        utc_time = utc_time.replace(tzinfo=timezone.utc)

    vladivostok_tz = get_vladivostok_timezone()
    return utc_time.astimezone(vladivostok_tz)


def vladivostok_to_utc(local_time: datetime) -> datetime:
    """
    Конвертировать время Владивостока в UTC

    Args:
        local_time: Время в часовом поясе Владивостока

    Returns:
        Время в UTC
    """
    if local_time.tzinfo is None:
        # Если время без часового пояса, считаем что это локальное время
        vladivostok_tz = get_vladivostok_timezone()
        local_time = vladivostok_tz.localize(local_time)

    return local_time.astimezone(timezone.utc)


def now_vladivostok() -> datetime:
    """
    Получить текущее время в часовом поясе Владивостока

    Returns:
        Текущее время в Владивостоке
    """
    return datetime.now(get_vladivostok_timezone())


def format_datetime_for_display(
    dt: datetime, include_timezone: bool = False
) -> str:
    """
    Форматировать дату и время для отображения пользователю

    Args:
        dt: Дата и время
        include_timezone: Включить информацию о часовом поясе

    Returns:
        Отформатированная строка
    """
    if dt.tzinfo is None:
        # Если время без часового пояса, считаем что это UTC
        dt = dt.replace(tzinfo=timezone.utc)

    # Конвертируем в локальное время
    local_dt = utc_to_vladivostok(dt)

    if include_timezone:
        return local_dt.strftime("%d.%m.%Y %H:%M:%S %Z")
    else:
        return local_dt.strftime("%d.%m.%Y %H:%M:%S")


def format_date_for_display(dt: datetime) -> str:
    """
    Форматировать только дату для отображения пользователю

    Args:
        dt: Дата и время

    Returns:
        Отформатированная дата
    """
    if dt.tzinfo is None:
        # Если время без часового пояса, считаем что это UTC
        dt = dt.replace(tzinfo=timezone.utc)

    # Конвертируем в локальное время
    local_dt = utc_to_vladivostok(dt)
    return local_dt.strftime("%d.%m.%Y")


def format_time_for_display(dt: datetime) -> str:
    """
    Форматировать только время для отображения пользователю

    Args:
        dt: Дата и время

    Returns:
        Отформатированное время
    """
    if dt.tzinfo is None:
        # Если время без часового пояса, считаем что это UTC
        dt = dt.replace(tzinfo=timezone.utc)

    # Конвертируем в локальное время
    local_dt = utc_to_vladivostok(dt)
    return local_dt.strftime("%H:%M:%S")
