"""
Value Object для приоритета ключевого слова
"""

from dataclasses import dataclass

from src.keywords.shared.base_value_object import BaseValueObject
from src.keywords.shared.constants import DEFAULT_PRIORITY
from src.keywords.shared.error_handlers import handle_validation_errors
from src.keywords.shared.validation_utils import ValidationUtils


@dataclass(frozen=True)
class KeywordPriority(BaseValueObject):
    """Value Object для приоритета ключевого слова с валидацией"""

    value: int

    @handle_validation_errors
    def _validate_type(self) -> None:
        """
        Валидация типа и диапазона значения приоритета.

        Использует ValidationUtils для комплексной валидации,
        включая проверку типа, диапазона и формата приоритета.
        """
        # Валидируем через ValidationUtils, который включает все проверки
        cleaned_value = ValidationUtils.validate_priority(self.value)

        # Обновляем значение, если оно было изменено (очищено или нормализовано)
        if cleaned_value != self.value:
            object.__setattr__(self, "value", cleaned_value)

    def _should_strip_value(self) -> bool:
        """
        Обрезать пробелы для приоритета.

        Приоритет - числовое значение, поэтому обрезка пробелов не нужна.
        """
        return False

    def _validate_length(self) -> None:
        """
        Валидация диапазона приоритета.

        Этот метод больше не нужен, так как валидация диапазона
        выполняется в ValidationUtils.validate_priority().
        """
        pass

    def __str__(self) -> str:
        """Строковое представление"""
        return str(self.value)

    def __lt__(self, other) -> bool:
        """Сравнение меньше"""
        if not isinstance(other, KeywordPriority):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other) -> bool:
        """Сравнение меньше или равно"""
        if not isinstance(other, KeywordPriority):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other) -> bool:
        """Сравнение больше"""
        if not isinstance(other, KeywordPriority):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other) -> bool:
        """Сравнение больше или равно"""
        if not isinstance(other, KeywordPriority):
            return NotImplemented
        return self.value >= other.value

    @classmethod
    def default(cls) -> "KeywordPriority":
        """Создать приоритет по умолчанию"""
        return cls(DEFAULT_PRIORITY)