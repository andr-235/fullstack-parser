"""
Декораторы для унифицированной обработки ошибок в сервисах и репозиториях
"""

import logging
from functools import wraps
from typing import Callable, Any

from .exceptions import (
    KeywordsException,
    KeywordValidationError,
    DatabaseError,
    RepositoryError,
)

# Настройка логгера для модуля
logger = logging.getLogger(__name__)


def handle_service_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок в сервисах.

    Ловит общие исключения KeywordsException (кроме валидационных и репозиторных)
    и логирует их перед перевыбросом.

    Args:
        func: Функция сервиса для декорирования

    Returns:
        Callable: Декорированная функция

    Raises:
        KeywordsException: Перевыбрасывает пойманное исключение после логирования
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except (DatabaseError, RepositoryError, KeywordValidationError):
            # Пропускаем эти исключения, они обрабатываются другими декораторами
            raise
        except KeywordsException as e:
            logger.error(
                f"Service error in {func.__name__}: {e.message}",
                exc_info=True
            )
            raise
        except Exception as e:
            # Ловим неожиданные исключения и оборачиваем в KeywordsException
            logger.error(
                f"Unexpected error in service {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise KeywordsException(f"Неожиданная ошибка сервиса: {str(e)}") from e

    return wrapper


def handle_repository_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок в репозиториях.

    Ловит исключения DatabaseError и RepositoryError, логирует их
    и перевыбрасывает.

    Args:
        func: Функция репозитория для декорирования

    Returns:
        Callable: Декорированная функция

    Raises:
        DatabaseError: Перевыбрасывает ошибки базы данных
        RepositoryError: Перевыбрасывает ошибки репозитория
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except (DatabaseError, RepositoryError) as e:
            logger.error(
                f"Repository error in {func.__name__}: {e.message}",
                exc_info=True
            )
            raise
        except Exception as e:
            # Оборачиваем неожиданные исключения в RepositoryError
            logger.error(
                f"Unexpected error in repository {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise RepositoryError(f"Неожиданная ошибка репозитория: {str(e)}") from e

    return wrapper


def handle_validation_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок валидации.

    Ловит исключения KeywordValidationError и его подклассы,
    логирует их и перевыбрасывает.

    Args:
        func: Функция валидации для декорирования

    Returns:
        Callable: Декорированная функция

    Raises:
        KeywordValidationError: Перевыбрасывает ошибки валидации
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except KeywordValidationError as e:
            logger.error(
                f"Validation error in {func.__name__}: {e.message}",
                exc_info=True
            )
            raise
        except Exception as e:
            # Оборачиваем неожиданные исключения в KeywordValidationError
            logger.error(
                f"Unexpected error in validation {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise KeywordValidationError(f"Неожиданная ошибка валидации: {str(e)}") from e

    return wrapper