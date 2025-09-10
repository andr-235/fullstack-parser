"""
Общие утилиты для модуля Parser

Содержит общие вспомогательные функции для парсинга VK данных
"""

from __future__ import annotations
import time
import asyncio
import re
import logging
from typing import (
    Dict,
    Any,
    List,
    Optional,
    Union,
    Tuple,
    Callable,
    TypeVar,
    Generic,
    Iterator,
    AsyncGenerator,
)
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps

from .config import parser_settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Type variables для generic функций
T = TypeVar("T")
R = TypeVar("R")


def retry_with_backoff(
    max_attempts: Optional[int] = None,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[type[BaseException], ...] = (Exception,),
):
    """
    Декоратор для повторных попыток с экспоненциальной задержкой.

    Args:
        max_attempts: Максимум попыток
        base_delay: Базовая задержка в секундах
        max_delay: Максимальная задержка в секундах
        backoff_factor: Коэффициент увеличения задержки
        exceptions: Типы исключений для повторных попыток

    Returns:
        Callable: Декоратор функции
    """
    if max_attempts is None:
        max_attempts = parser_settings.max_retry_attempts

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any):
            last_exception: Optional[BaseException] = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt == max_attempts - 1:
                        raise e

                    # Рассчитываем задержку
                    delay = min(
                        base_delay * (backoff_factor**attempt), max_delay
                    )
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)

            raise last_exception or RuntimeError("Max attempts exceeded")

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any):
            last_exception: Optional[BaseException] = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt == max_attempts - 1:
                        raise e

                    # Рассчитываем задержку
                    delay = min(
                        base_delay * (backoff_factor**attempt), max_delay
                    )
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)

            raise last_exception or RuntimeError("Max attempts exceeded")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def measure_execution_time(func):
    """
    Декоратор для измерения времени выполнения функции.

    Args:
        func: Функция для измерения

    Returns:
        Callable: Обернутая функция
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f} seconds"
            )

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f} seconds"
            )

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def create_batch_chunks(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Разделить список на батчи.

    Args:
        items: Список элементов
        chunk_size: Размер батча

    Returns:
        List[List[T]]: Список батчей
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть положительным числом")

    return [
        items[i : i + chunk_size] for i in range(0, len(items), chunk_size)
    ]


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Безопасно получить значение из словаря.

    Args:
        data: Словарь
        key: Ключ (может быть вложенным через точку)
        default: Значение по умолчанию

    Returns:
        Union[T, Any]: Значение или default
    """
    if not data or not key:
        return default

    keys = key.split(".")
    current: Any = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default

    return current


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Объединить несколько словарей.

    Args:
        *dicts: Словари для объединения

    Returns:
        Dict[str, Any]: Объединенный словарь
    """
    result: Dict[str, Any] = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Удалить None значения из словаря.

    Args:
        data: Исходный словарь

    Returns:
        Dict[str, Any]: Словарь без None значений
    """
    return {k: v for k, v in data.items() if v is not None}


def convert_to_utc(dt: datetime) -> datetime:
    """
    Конвертировать datetime в UTC.

    Args:
        dt: Объект datetime

    Returns:
        datetime: UTC datetime
    """
    if dt.tzinfo is None:
        # Предполагаем что это уже UTC
        return dt
    return dt.astimezone()


def format_timestamp(timestamp: Union[int, float, datetime]) -> str:
    """
    Форматировать timestamp в читаемый вид.

    Args:
        timestamp: Timestamp или datetime

    Returns:
        str: Отформатированная дата
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_percentage(
    part: Union[int, float], total: Union[int, float]
) -> float:
    """
    Рассчитать процент.

    Args:
        part: Часть
        total: Общее количество

    Returns:
        float: Процент
    """
    if total == 0:
        return 0.0
    return (part / total) * 100


def clamp(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
) -> Union[int, float]:
    """
    Ограничить значение диапазоном.

    Args:
        value: Значение
        min_val: Минимальное значение
        max_val: Максимальное значение

    Returns:
        Union[int, float]: Ограниченное значение
    """
    return max(min_val, min(value, max_val))


def is_valid_email(email: str) -> bool:
    """
    Проверить валидность email.

    Args:
        email: Email адрес

    Returns:
        bool: True если email валиден
    """
    if not isinstance(email, str) or not email.strip():
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def is_valid_url(url: str) -> bool:
    """
    Проверить валидность URL.

    Args:
        url: URL

    Returns:
        bool: True если URL валиден
    """
    if not isinstance(url, str) or not url.strip():
        return False

    pattern = r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
    return bool(re.match(pattern, url.strip()))


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Обрезать строку до максимальной длины.

    Args:
        text: Исходная строка
        max_length: Максимальная длина
        suffix: Суффикс для обрезанных строк

    Returns:
        str: Обрезанная строка
    """
    if not isinstance(text, str):
        return str(text)

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def deduplicate_list(items: List[T]) -> List[T]:
    """
    Удалить дубликаты из списка с сохранением порядка.

    Args:
        items: Список элементов

    Returns:
        List[T]: Список без дубликатов
    """
    seen: set = set()
    result: List[T] = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


async def chunked_async_generator(
    items: List[T], chunk_size: int
) -> AsyncGenerator[List[T], None]:
    """
    Асинхронный генератор для обработки элементов батчами.

    Args:
        items: Список элементов
        chunk_size: Размер батча

    Yields:
        List[T]: Батч элементов
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть положительным числом")

    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]
        # Небольшая пауза между батчами
        await asyncio.sleep(0.01)


# Дополнительные утилиты
def safe_int(value: Any, default: int = 0) -> int:
    """
    Безопасно преобразовать значение в int.

    Args:
        value: Значение для преобразования
        default: Значение по умолчанию

    Returns:
        int: Преобразованное значение или default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Безопасно преобразовать значение в float.

    Args:
        value: Значение для преобразования
        default: Значение по умолчанию

    Returns:
        float: Преобразованное значение или default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Безопасно преобразовать значение в str.

    Args:
        value: Значение для преобразования
        default: Значение по умолчанию

    Returns:
        str: Преобразованное значение или default
    """
    try:
        return str(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def is_empty(value: Any) -> bool:
    """
    Проверить является ли значение пустым.

    Args:
        value: Значение для проверки

    Returns:
        bool: True если значение пустое
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple)):
        return len(value) == 0
    return False


def get_nested_value(
    data: Dict[str, Any], keys: List[str], default: Optional[T] = None
) -> Union[T, Any]:
    """
    Получить значение по вложенным ключам.

    Args:
        data: Словарь данных
        keys: Список ключей для поиска
        default: Значение по умолчанию

    Returns:
        Union[T, Any]: Найденное значение или default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


# Импорт функций из data_utils
import hashlib
import json
from datetime import timedelta


# Функции из data_utils.py
def generate_task_id(group_ids: List[int], config: Dict[str, Any]) -> str:
    """Генерировать уникальный ID задачи"""
    data = {
        "group_ids": sorted(group_ids),
        "config": config,
        "timestamp": datetime.utcnow().isoformat(),
    }
    data_str = json.dumps(data, sort_keys=True)
    hash_obj = hashlib.md5(data_str.encode())
    return hash_obj.hexdigest()


def calculate_estimated_time(
    group_count: int,
    max_posts: int,
    max_comments: int,
    requests_per_second: int = 3,
) -> int:
    """Рассчитать ожидаемое время выполнения задачи"""
    posts_requests = group_count * 1
    comments_requests = group_count * max_posts
    total_requests = posts_requests + comments_requests
    base_time = total_requests / requests_per_second
    estimated_time = int(base_time * 1.2)
    return max(estimated_time, 1)


def format_duration(seconds: float) -> str:
    """Форматировать длительность в читаемый вид"""
    if seconds < 60:
        return f"{seconds:.1f}с"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}м"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}ч"


def format_file_size(bytes_size: int) -> str:
    """Форматировать размер файла в читаемый вид"""
    size = float(bytes_size)
    for unit in ["Б", "КБ", "МБ", "ГБ"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} ТБ"


def clean_text(text: str) -> str:
    """Очистить текст от лишних символов"""
    if not text:
        return ""
    text = " ".join(text.split())
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def extract_hashtags(text: str) -> List[str]:
    """Извлечь хештеги из текста"""
    if not text:
        return []
    hashtag_pattern = r"#[\w\u0400-\u04FF]+"
    hashtags = re.findall(hashtag_pattern, text, re.IGNORECASE)
    return [tag.lower() for tag in hashtags]


def extract_mentions(text: str) -> List[str]:
    """Извлечь упоминания из текста"""
    if not text:
        return []
    mention_pattern = r"@[\w\u0400-\u04FF]+"
    mentions = re.findall(mention_pattern, text, re.IGNORECASE)
    return [mention.lower() for mention in mentions]


def calculate_sentiment_score(text: str) -> float:
    """Рассчитать простой sentiment score для текста"""
    if not text:
        return 0.0

    positive_words = [
        "хорошо",
        "отлично",
        "прекрасно",
        "замечательно",
        "супер",
        "классно",
        "круто",
        "здорово",
        "великолепно",
        "восхитительно",
    ]
    negative_words = [
        "плохо",
        "ужасно",
        "отвратительно",
        "кошмар",
        "ужас",
        "гадость",
        "мерзость",
        "отвращение",
        "ненависть",
        "зло",
    ]

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    total_words = len(text.split())
    if total_words == 0:
        return 0.0

    positive_score = positive_count / total_words
    negative_score = negative_count / total_words
    return positive_score - negative_score


def group_data_by_field(
    data: List[Dict[str, Any]], field: str
) -> Dict[Any, List[Dict[str, Any]]]:
    """Группировать данные по полю"""
    grouped: Dict[Any, List[Dict[str, Any]]] = {}
    for item in data:
        key = item.get(field)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped


def filter_data_by_condition(
    data: List[Dict[str, Any]], condition: Callable[[Dict[str, Any]], bool]
) -> List[Dict[str, Any]]:
    """Фильтровать данные по условию"""
    return [item for item in data if condition(item)]


def sort_data_by_field(
    data: List[Dict[str, Any]], field: str, reverse: bool = False
) -> List[Dict[str, Any]]:
    """Сортировать данные по полю"""
    return sorted(data, key=lambda x: x.get(field, 0), reverse=reverse)


def calculate_statistics(
    data: List[Dict[str, Any]], field: str
) -> Dict[str, float]:
    """Рассчитать статистику по полю"""
    if not data:
        return {"min": 0, "max": 0, "avg": 0, "count": 0}

    values = [
        item.get(field, 0)
        for item in data
        if isinstance(item.get(field), (int, float))
    ]

    if not values:
        return {"min": 0, "max": 0, "avg": 0, "count": 0}

    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "count": len(values),
    }


# Экспорт
__all__ = [
    # Основные утилиты
    "retry_with_backoff",
    "measure_execution_time",
    "create_batch_chunks",
    "safe_get",
    "merge_dicts",
    "filter_none_values",
    "convert_to_utc",
    "format_timestamp",
    "calculate_percentage",
    "clamp",
    "is_valid_email",
    "is_valid_url",
    "truncate_string",
    "deduplicate_list",
    "chunked_async_generator",
    "safe_int",
    "safe_float",
    "safe_str",
    "is_empty",
    "get_nested_value",
    # Функции из data_utils
    "generate_task_id",
    "calculate_estimated_time",
    "format_duration",
    "format_file_size",
    "clean_text",
    "extract_hashtags",
    "extract_mentions",
    "calculate_sentiment_score",
    "group_data_by_field",
    "filter_data_by_condition",
    "sort_data_by_field",
    "calculate_statistics",
]
