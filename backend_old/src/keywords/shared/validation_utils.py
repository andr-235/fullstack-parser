"""
Утилиты валидации для модуля Keywords

Содержит статические методы для валидации различных типов данных,
используемых в ключевых словах. Предназначен для устранения дублирования
логики валидации между Value Objects.
"""

import re
from typing import Optional

from src.keywords.shared.constants import (
    ERROR_INVALID_KEYWORD_FORMAT,
    KEYWORD_WORD_PATTERN,
    MAX_CATEGORY_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_KEYWORD_LENGTH,
    MIN_KEYWORD_LENGTH,
    MIN_PRIORITY,
    MAX_PRIORITY,
)
from src.keywords.shared.exceptions import (
    InvalidCategoryLengthError,
    InvalidDescriptionLengthError,
    InvalidPriorityError,
    KeywordTooLongError,
    KeywordTooShortError,
    KeywordValidationError,
)


class ValidationUtils:
    """
    Статический класс с методами валидации для ключевых слов.

    Предоставляет переиспользуемые методы валидации, которые используются
    в Value Objects для проверки корректности данных.
    """

    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = MIN_KEYWORD_LENGTH,
        max_length: int = MAX_KEYWORD_LENGTH,
        field_name: str = "строка"
    ) -> str:
        """
        Валидирует длину строки и возвращает очищенное значение.

        Args:
            value: Строка для валидации
            min_length: Минимальная допустимая длина
            max_length: Максимальная допустимая длина
            field_name: Название поля для сообщений об ошибках

        Returns:
            str: Очищенная от пробелов строка

        Raises:
            KeywordValidationError: Если значение не является строкой
            KeywordTooShortError: Если длина меньше минимальной
            KeywordTooLongError: Если длина больше максимальной
        """
        if not isinstance(value, str):
            raise KeywordValidationError(f"{field_name} должна быть строкой")

        # Очищаем от пробелов
        cleaned_value = value.strip()

        # Проверяем минимальную длину
        if len(cleaned_value) < min_length:
            raise KeywordTooShortError(min_length)

        # Проверяем максимальную длину
        if len(cleaned_value) > max_length:
            raise KeywordTooLongError(max_length)

        return cleaned_value

    @staticmethod
    def validate_priority(value: int) -> int:
        """
        Валидирует значение приоритета.

        Args:
            value: Значение приоритета для проверки

        Returns:
            int: Проверенное значение приоритета

        Raises:
            KeywordValidationError: Если значение не является целым числом
            InvalidPriorityError: Если значение вне допустимого диапазона
        """
        if not isinstance(value, int):
            raise KeywordValidationError("Приоритет должен быть целым числом")

        if not (MIN_PRIORITY <= value <= MAX_PRIORITY):
            raise InvalidPriorityError(MIN_PRIORITY, MAX_PRIORITY)

        return value

    @staticmethod
    def validate_word_format(value: str) -> str:
        """
        Валидирует формат слова ключевого слова.

        Проверяет, что слово содержит только допустимые символы
        (буквы, цифры, пробелы, дефисы, подчеркивания).

        Args:
            value: Слово для валидации формата

        Returns:
            str: Очищенное слово

        Raises:
            KeywordValidationError: Если формат слова некорректный
        """
        # Сначала валидируем длину
        cleaned_value = ValidationUtils.validate_string_length(
            value, field_name="Слово ключевого слова"
        )

        # Проверяем формат: только буквы, цифры, пробелы, дефисы, подчеркивания
        if not re.match(KEYWORD_WORD_PATTERN, cleaned_value):
            raise KeywordValidationError(ERROR_INVALID_KEYWORD_FORMAT)

        return cleaned_value

    @staticmethod
    def validate_category(value: Optional[str]) -> Optional[str]:
        """
        Валидирует значение категории.

        Args:
            value: Значение категории (может быть None)

        Returns:
            Optional[str]: Очищенное значение категории или None

        Raises:
            KeywordValidationError: Если значение не является строкой или None
            InvalidCategoryLengthError: Если длина превышает максимальную
        """
        if value is None:
            return None

        if not isinstance(value, str):
            raise KeywordValidationError("Категория должна быть строкой или None")

        # Очищаем от пробелов
        cleaned_value = value.strip()

        # Если после очистки пустое, возвращаем None
        if not cleaned_value:
            return None

        # Проверяем максимальную длину
        if len(cleaned_value) > MAX_CATEGORY_LENGTH:
            raise InvalidCategoryLengthError(MAX_CATEGORY_LENGTH)

        return cleaned_value

    @staticmethod
    def validate_description(value: Optional[str]) -> Optional[str]:
        """
        Валидирует значение описания.

        Args:
            value: Значение описания (может быть None)

        Returns:
            Optional[str]: Очищенное значение описания или None

        Raises:
            KeywordValidationError: Если значение не является строкой или None
            InvalidDescriptionLengthError: Если длина превышает максимальную
        """
        if value is None:
            return None

        if not isinstance(value, str):
            raise KeywordValidationError("Описание должно быть строкой или None")

        # Очищаем от пробелов
        cleaned_value = value.strip()

        # Если после очистки пустое, возвращаем None
        if not cleaned_value:
            return None

        # Проверяем максимальную длину
        if len(cleaned_value) > MAX_DESCRIPTION_LENGTH:
            raise InvalidDescriptionLengthError(MAX_DESCRIPTION_LENGTH)

        return cleaned_value