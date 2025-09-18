"""
Value Object для категории ключевого слова
"""

from dataclasses import dataclass
from typing import Optional

from src.keywords.shared.base_value_object import BaseValueObject
from src.keywords.shared.constants import (
    DEFAULT_CATEGORY,
    SYSTEM_CATEGORIES,
)
from src.keywords.shared.error_handlers import handle_validation_errors
from src.keywords.shared.validation_utils import ValidationUtils


@dataclass(frozen=True)
class KeywordCategory(BaseValueObject):
    """Value Object для категории ключевого слова с валидацией"""

    value: Optional[str]

    @handle_validation_errors
    def _validate_type(self) -> None:
        """
        Валидация типа и формата значения категории.

        Использует ValidationUtils для комплексной валидации,
        включая проверку типа, длины и формата категории.
        """
        # Валидируем через ValidationUtils, который включает все проверки
        cleaned_value = ValidationUtils.validate_category(self.value)

        # Обновляем значение, если оно было изменено (очищено от пробелов или установлено None)
        if cleaned_value != self.value:
            object.__setattr__(self, "value", cleaned_value)

    def _should_strip_value(self) -> bool:
        """
        Обрезать пробелы только для непустых значений.

        Этот метод больше не нужен, так как обрезка пробелов
        выполняется в ValidationUtils.validate_category().
        """
        return False

    def _validate_length(self) -> None:
        """
        Валидация длины категории.

        Этот метод больше не нужен, так как валидация длины
        выполняется в ValidationUtils.validate_category().
        """
        pass

    def __str__(self) -> str:
        """Строковое представление"""
        return self.value or ""

    def __bool__(self) -> bool:
        """Проверка на пустоту"""
        return self.value is not None and bool(self.value.strip())

    @classmethod
    def empty(cls) -> "KeywordCategory":
        """Создать пустую категорию"""
        return cls(None)

    @classmethod
    def default(cls) -> "KeywordCategory":
        """Создать категорию по умолчанию"""
        return cls(DEFAULT_CATEGORY)

    @classmethod
    def from_system_category(cls, category_name: str) -> "KeywordCategory":
        """Создать категорию из системных категорий"""
        if category_name not in SYSTEM_CATEGORIES:
            raise ValueError(f"Категория '{category_name}' не является системной")
        return cls(category_name)

    def is_system_category(self) -> bool:
        """Проверка, является ли категория системной"""
        return self.value in SYSTEM_CATEGORIES