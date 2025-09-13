"""
Исключения модуля Auth
"""


class AuthException(Exception):
    """Базовое исключение модуля Auth"""
    pass


class InvalidCredentialsError(AuthException):
    """Неверные учетные данные"""
    pass


class InvalidTokenError(AuthException):
    """Неверный токен"""
    pass


class TokenExpiredError(AuthException):
    """Токен истек"""
    pass
