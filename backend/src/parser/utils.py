"""
Общие утилиты для модуля Parser

Содержит основные вспомогательные функции для парсинга VK данных
"""

from __future__ import annotations
import time
import asyncio
import re
import logging
from typing import Dict, Any, List, Optional, Union, Tuple, Callable, TypeVar
from datetime import datetime
from functools import wraps

from parser.config import parser_settings

# Настройка логирования
logger = logging.getLogger(__name__)

# Type variables для generic функций
T = TypeVar("T")


def retry_with_backoff(
    max_attempts: Optional[int] = None,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[type[BaseException], ...] = (Exception,),
):
    """Декоратор для повторных попыток с экспоненциальной задержкой"""
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

                    delay = min(base_delay * (backoff_factor**attempt), max_delay)
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

                    delay = min(base_delay * (backoff_factor**attempt), max_delay)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)

            raise last_exception or RuntimeError("Max attempts exceeded")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def measure_execution_time(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения функции"""

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

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def create_batch_chunks(items: List[T], chunk_size: int):
    """Разделить список на батчи"""
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть положительным числом")

    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Безопасно получить значение из словаря по ключу"""
    keys = key.split(".")
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default

    return current


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


def validate_vk_group_id(group_id: Union[int, str]) -> bool:
    """Валидация VK Group ID"""
    try:
        gid = int(group_id)
        return gid > 0
    except (ValueError, TypeError):
        return False


def validate_vk_post_id(post_id: Union[int, str]) -> bool:
    """Валидация VK Post ID"""
    try:
        pid = int(post_id)
        return pid > 0
    except (ValueError, TypeError):
        return False


# Экспорт
__all__ = [
    "retry_with_backoff",
    "measure_execution_time",
    "create_batch_chunks",
    "safe_get",
    "clean_text",
    "extract_hashtags",
    "extract_mentions",
    "validate_vk_group_id",
    "validate_vk_post_id",
]