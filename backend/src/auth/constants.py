"""
Константы для модуля аутентификации
"""

# Статусы пользователей
class UserStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


# Типы токенов
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


# Типы событий безопасности
class SecurityEvent:
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"


# Кеш ключи
class CacheKeys:
    USER_PREFIX = "user:"
    LOGIN_ATTEMPTS_PREFIX = "login_attempts:"
    TOKEN_PREFIX = "token:"


# Ограничения
class Limits:
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPTS_TTL_SECONDS = 900  # 15 минут
    PASSWORD_MIN_LENGTH = 8
    EMAIL_MAX_LENGTH = 255
    FULL_NAME_MAX_LENGTH = 100
