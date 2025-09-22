"""
Value Object для слова ключевого слова
"""

from dataclasses import dataclass

from src.keywords.shared.base_value_object import BaseValueObject
from src.keywords.shared.error_handlers import handle_validation_errors
from src.keywords.shared.validation_utils import ValidationUtils


@dataclass(frozen=True)
class KeywordWord(BaseValueObject):
    """Value Object для слова ключевого слова с валидацией"""

    value: str

    @handle_validation_errors
    def _validate_type(self) -> None:
        """
        Валидация типа и формата значения слова ключевого слова.

        Использует ValidationUtils для комплексной валидации,
        включая проверку типа, длины и формата слова.
        """
        # Валидируем через ValidationUtils, который включает все проверки
        cleaned_value = ValidationUtils.validate_word_format(self.value)

        # Обновляем значение, если оно было изменено (очищено от пробелов)
        if cleaned_value != self.value:
            object.__setattr__(self, "value", cleaned_value)

    def _validate_length(self) -> None:
        """
        Валидация длины слова ключевого слова.

        Этот метод больше не нужен, так как валидация длины
        выполняется в ValidationUtils.validate_word_format().
        Оставлен для совместимости с BaseValueObject.
        """
        pass