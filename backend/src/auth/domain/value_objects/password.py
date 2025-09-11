"""
Value Object для Password

Инкапсулирует логику работы с паролями
"""

import re
from dataclasses import dataclass
from typing import Optional

from auth.shared.exceptions import PasswordTooWeakError, PasswordTooShortError


@dataclass(frozen=True)
class Password:
    """
    Value Object для пароля
    
    Обеспечивает валидацию и хеширование паролей
    """
    
    hashed_value: str
    _plain_value: Optional[str] = None
    
    def __post_init__(self):
        """Валидация пароля после инициализации"""
        if self._plain_value:
            self._validate_password(self._plain_value)
    
    @classmethod
    def create_from_plain(cls, plain_password: str) -> 'Password':
        """Создать Password из открытого пароля"""
        cls._validate_password(plain_password)
        # Хеширование будет выполнено в сервисе
        return cls(hashed_value="", _plain_value=plain_password)
    
    @classmethod
    def create_from_hash(cls, hashed_password: str) -> 'Password':
        """Создать Password из хеша"""
        return cls(hashed_value=hashed_password)
    
    @staticmethod
    def _validate_password(password: str) -> None:
        """Валидировать пароль"""
        if len(password) < 8:
            raise PasswordTooShortError()
        
        if len(password) > 128:
            raise PasswordTooWeakError("Пароль слишком длинный")
        
        # Проверка наличия разных типов символов
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        
        if not (has_upper and has_lower and has_digit):
            raise PasswordTooWeakError(
                "Пароль должен содержать заглавные и строчные буквы, а также цифры"
            )
        
        # Проверка на распространенные слабые пароли
        weak_passwords = [
            "password", "123456", "qwerty", "admin", "user",
            "password123", "123456789", "qwerty123"
        ]
        
        if password.lower() in weak_passwords:
            raise PasswordTooWeakError("Пароль слишком простой")
    
    def __str__(self) -> str:
        return self.hashed_value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Password):
            return False
        return self.hashed_value == other.hashed_value
