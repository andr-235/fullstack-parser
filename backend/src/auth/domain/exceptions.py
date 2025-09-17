"""
Доменные исключения аутентификации
"""

from typing import Optional


class AuthDomainException(Exception):
    """Базовое исключение домена аутентификации"""
    pass


class InvalidCredentialsError(AuthDomainException):
    """Неверные учетные данные"""
    pass


class InvalidTokenError(AuthDomainException):
    """Неверный токен"""
    pass


class TokenExpiredError(AuthDomainException):
    """Токен истек"""
    pass


class UserAlreadyExistsError(AuthDomainException):
    """Пользователь уже существует"""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists")


class UserNotFoundError(AuthDomainException):
    """Пользователь не найден"""
    
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        if user_id:
            super().__init__(f"User with ID {user_id} not found")
        elif email:
            super().__init__(f"User with email {email} not found")
        else:
            super().__init__("User not found")


class UserInactiveError(AuthDomainException):
    """Пользователь неактивен"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} is inactive")


class UserLockedError(AuthDomainException):
    """Пользователь заблокирован"""
    
    def __init__(self, user_id: int, locked_until: Optional[str] = None):
        self.user_id = user_id
        self.locked_until = locked_until
        super().__init__(f"User {user_id} is locked until {locked_until}")


class TooManyLoginAttemptsError(AuthDomainException):
    """Слишком много попыток входа"""
    
    def __init__(self, email: str, attempts: int):
        self.email = email
        self.attempts = attempts
        super().__init__(f"Too many login attempts for {email}: {attempts}")


class PasswordTooWeakError(AuthDomainException):
    """Пароль слишком слабый"""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Password is too weak: {reason}")


class InvalidPasswordResetTokenError(AuthDomainException):
    """Неверный токен сброса пароля"""
    pass
