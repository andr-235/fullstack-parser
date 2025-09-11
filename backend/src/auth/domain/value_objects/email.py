"""
Value Object для Email

Инкапсулирует логику работы с email адресами
"""

import re
from dataclasses import dataclass
from typing import Optional

from auth.shared.exceptions import InvalidEmailFormatError


@dataclass(frozen=True)
class Email:
    """
    Value Object для email адреса
    
    Обеспечивает валидацию и нормализацию email
    """
    
    value: str
    
    def __post_init__(self):
        """Валидация email после инициализации"""
        if not self._is_valid_email(self.value):
            raise InvalidEmailFormatError(self.value)
        
        # Нормализация email
        object.__setattr__(self, 'value', self.value.strip().lower())
    
    def _is_valid_email(self, email: str) -> bool:
        """Проверить валидность email"""
        if not email or len(email) > 255:
            return False
        
        # Простая регулярка для базовой валидации
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Email):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
