"""
Инфраструктурный сервис работы со временем

Предоставляет утилиты для работы с датами и временем
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Union, List
from functools import lru_cache


class TimeUtilsService:
    """
    Инфраструктурный сервис для работы со временем

    Предоставляет утилиты для работы с датами и временем
    во всех слоях архитектуры
    """

    @staticmethod
    def now() -> datetime:
        """
        Получить текущее время UTC

        Returns:
            Текущее время в UTC
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def now_iso() -> str:
        """
        Получить текущее время в ISO формате

        Returns:
            Строка с текущим временем в ISO формате
        """
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def now_timestamp() -> float:
        """
        Получить текущий timestamp

        Returns:
            Текущий timestamp
        """
        return datetime.now(timezone.utc).timestamp()

    @staticmethod
    def from_iso(iso_string: str) -> datetime:
        """
        Преобразовать ISO строку в datetime

        Args:
            iso_string: ISO строка

        Returns:
            datetime объект
        """
        if not iso_string:
            return datetime.now(timezone.utc)

        # Обрабатываем разные форматы ISO
        iso_string = iso_string.replace("Z", "+00:00")
        if "+" not in iso_string and "-" not in iso_string[-6:]:
            iso_string += "+00:00"

        return datetime.fromisoformat(iso_string)

    @staticmethod
    def to_iso(dt: datetime) -> str:
        """
        Преобразовать datetime в ISO строку

        Args:
            dt: datetime объект

        Returns:
            ISO строка
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Добавить дни к дате

        Args:
            dt: Исходная дата
            days: Количество дней

        Returns:
            Новая дата
        """
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """
        Добавить часы к дате

        Args:
            dt: Исходная дата
            hours: Количество часов

        Returns:
            Новая дата
        """
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """
        Добавить минуты к дате

        Args:
            dt: Исходная дата
            minutes: Количество минут

        Returns:
            Новая дата
        """
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """
        Добавить секунды к дате

        Args:
            dt: Исходная дата
            seconds: Количество секунд

        Returns:
            Новая дата
        """
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def is_expired(dt: datetime) -> bool:
        """
        Проверить, истекло ли время

        Args:
            dt: Дата для проверки

        Returns:
            True если время истекло
        """
        now = datetime.now(timezone.utc)
        return dt < now

    @staticmethod
    def is_future(dt: datetime) -> bool:
        """
        Проверить, является ли дата будущей

        Args:
            dt: Дата для проверки

        Returns:
            True если дата в будущем
        """
        now = datetime.now(timezone.utc)
        return dt > now

    @staticmethod
    def time_until(dt: datetime) -> timedelta:
        """
        Получить время до указанной даты

        Args:
            dt: Целевая дата

        Returns:
            Время до даты
        """
        now = datetime.now(timezone.utc)
        return dt - now

    @staticmethod
    def time_since(dt: datetime) -> timedelta:
        """
        Получить время с указанной даты

        Args:
            dt: Исходная дата

        Returns:
            Время с даты
        """
        now = datetime.now(timezone.utc)
        return now - dt

    @staticmethod
    def format_duration(seconds: Union[int, float]) -> str:
        """
        Форматировать продолжительность в читаемый вид

        Args:
            seconds: Продолжительность в секундах

        Returns:
            Отформатированная строка
        """
        if seconds < 0:
            return f"-{TimeUtilsService.format_duration(-seconds)}"

        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h"

    @staticmethod
    def format_datetime(
        dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """
        Форматировать datetime в строку

        Args:
            dt: datetime объект
            format_str: Формат строки

        Returns:
            Отформатированная строка
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime(format_str)

    @staticmethod
    def parse_datetime(
        date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        """
        Парсить строку в datetime

        Args:
            date_str: Строка с датой
            format_str: Формат строки

        Returns:
            datetime объект
        """
        dt = datetime.strptime(date_str, format_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def get_date_range(
        start_date: datetime, end_date: datetime, include_end: bool = True
    ) -> List[datetime]:
        """
        Получить список дат в диапазоне

        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            include_end: Включать конечную дату

        Returns:
            Список дат
        """
        dates = []
        current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current <= end if include_end else current < end:
            dates.append(current)
            current += timedelta(days=1)

        return dates

    @staticmethod
    def get_business_days(start_date: datetime, end_date: datetime) -> int:
        """
        Получить количество рабочих дней между датами

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Количество рабочих дней
        """
        business_days = 0
        current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        while current <= end_date:
            # Проверяем, является ли день рабочим (понедельник-пятница)
            if current.weekday() < 5:  # 0-4 = понедельник-пятница
                business_days += 1
            current += timedelta(days=1)

        return business_days

    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """
        Проверить, является ли дата рабочим днем

        Args:
            dt: Дата для проверки

        Returns:
            True если рабочий день
        """
        return dt.weekday() < 5  # 0-4 = понедельник-пятница

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        Проверить, является ли дата выходным

        Args:
            dt: Дата для проверки

        Returns:
            True если выходной
        """
        return dt.weekday() >= 5  # 5-6 = суббота-воскресенье

    @staticmethod
    def get_week_start(dt: datetime) -> datetime:
        """
        Получить начало недели для даты

        Args:
            dt: Исходная дата

        Returns:
            Дата начала недели (понедельник)
        """
        days_since_monday = dt.weekday()
        return dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=days_since_monday)

    @staticmethod
    def get_month_start(dt: datetime) -> datetime:
        """
        Получить начало месяца для даты

        Args:
            dt: Исходная дата

        Returns:
            Дата начала месяца
        """
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def get_quarter_start(dt: datetime) -> datetime:
        """
        Получить начало квартала для даты

        Args:
            dt: Исходная дата

        Returns:
            Дата начала квартала
        """
        quarter = (dt.month - 1) // 3 + 1
        month = (quarter - 1) * 3 + 1
        return dt.replace(
            month=month, day=1, hour=0, minute=0, second=0, microsecond=0
        )

    @staticmethod
    def get_year_start(dt: datetime) -> datetime:
        """
        Получить начало года для даты

        Args:
            dt: Исходная дата

        Returns:
            Дата начала года
        """
        return dt.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )

    def get_time_info(self) -> Dict[str, Any]:
        """
        Получить информацию о текущем времени

        Returns:
            Информация о времени
        """
        now = self.now()
        return {
            "current_time": now.isoformat(),
            "timestamp": now.timestamp(),
            "day_of_week": now.weekday(),
            "day_of_year": now.timetuple().tm_yday,
            "week_of_year": now.isocalendar()[1],
            "month": now.month,
            "year": now.year,
            "quarter": (now.month - 1) // 3 + 1,
            "is_weekend": self.is_weekend(now),
            "is_business_day": self.is_business_day(now),
            "timezone": "UTC",
        }

    def get_time_stats(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Получить статистику по периоду времени

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Статистика по периоду
        """
        total_days = (end_date - start_date).days + 1
        business_days = self.get_business_days(start_date, end_date)
        weekend_days = total_days - business_days

        return {
            "total_days": total_days,
            "business_days": business_days,
            "weekend_days": weekend_days,
            "business_days_percentage": (
                (business_days / total_days) * 100 if total_days > 0 else 0
            ),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }


# Глобальный экземпляр сервиса времени
@lru_cache(maxsize=1)
def get_time_utils_service() -> TimeUtilsService:
    """Получить экземпляр сервиса времени (кешируется)"""
    return TimeUtilsService()


# Глобальный объект для обратной совместимости
time_utils_service = get_time_utils_service()


# Экспорт
__all__ = [
    "TimeUtilsService",
    "get_time_utils_service",
    "time_utils_service",
]
