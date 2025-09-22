"""
Исключения модуля Auth

Предоставляет иерархию исключений для различных сценариев аутентификации и авторизации.
Все исключения наследуются от AuthException для удобства обработки.
"""

from typing import Optional, Dict, Any


class AuthException(Exception):
    """
    Базовое исключение модуля Auth

    Attributes:
        message: Сообщение об ошибке
        code: Код ошибки для API
        details: Дополнительные детали ошибки
        status_code: HTTP статус код
    """

    def __init__(
        self,
        message: str,
        code: str = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать исключение в словарь для API ответа"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class InvalidCredentialsError(AuthException):
    """Неверные учетные данные"""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            code="INVALID_CREDENTIALS",
            status_code=401
        )


class InvalidTokenError(AuthException):
    """Неверный токен"""

    def __init__(self, message: str = "Invalid token", token_type: Optional[str] = None):
        details = {"token_type": token_type} if token_type else {}
        super().__init__(
            message=message,
            code="INVALID_TOKEN",
            details=details,
            status_code=401
        )


class TokenExpiredError(AuthException):
    """Токен истек"""

    def __init__(self, message: str = "Token has expired", token_type: Optional[str] = None):
        details = {"token_type": token_type} if token_type else {}
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
            details=details,
            status_code=401
        )


class UserNotFoundError(AuthException):
    """Пользователь не найден"""

    def __init__(self, user_id: Optional[str] = None, email: Optional[str] = None):
        message = "User not found"
        details = {}
        if user_id:
            details["user_id"] = user_id
        if email:
            details["email"] = email

        super().__init__(
            message=message,
            code="USER_NOT_FOUND",
            details=details,
            status_code=404
        )


class UserInactiveError(AuthException):
    """Пользователь неактивен"""

    def __init__(self, user_id: str, message: str = "User account is inactive"):
        super().__init__(
            message=message,
            code="USER_INACTIVE",
            details={"user_id": user_id},
            status_code=403
        )


class UserLockedError(AuthException):
    """Пользователь заблокирован"""

    def __init__(self, user_id: str, lock_reason: Optional[str] = None):
        details = {"user_id": user_id}
        if lock_reason:
            details["lock_reason"] = lock_reason

        super().__init__(
            message="User account is locked",
            code="USER_LOCKED",
            details=details,
            status_code=403
        )


class PasswordTooWeakError(AuthException):
    """Пароль слишком слабый"""

    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(
            message=message,
            code="PASSWORD_TOO_WEAK",
            status_code=400
        )


class PasswordMismatchError(AuthException):
    """Пароли не совпадают"""

    def __init__(self, message: str = "Passwords do not match"):
        super().__init__(
            message=message,
            code="PASSWORD_MISMATCH",
            status_code=400
        )


class RateLimitExceededError(AuthException):
    """Превышен лимит запросов"""

    def __init__(self, retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message="Too many requests. Please try again later.",
            code="RATE_LIMIT_EXCEEDED",
            details=details,
            status_code=429
        )


class EmailAlreadyExistsError(AuthException):
    """Email уже зарегистрирован"""

    def __init__(self, email: str):
        super().__init__(
            message="User with this email already exists",
            code="EMAIL_ALREADY_EXISTS",
            details={"email": email},
            status_code=409
        )


class InvalidEmailFormatError(AuthException):
    """Неверный формат email"""

    def __init__(self, email: str):
        super().__init__(
            message="Invalid email format",
            code="INVALID_EMAIL_FORMAT",
            details={"email": email},
            status_code=400
        )


class TokenRevokedError(AuthException):
    """Токен отозван"""

    def __init__(self, token_id: Optional[str] = None):
        details = {"token_id": token_id} if token_id else {}
        super().__init__(
            message="Token has been revoked",
            code="TOKEN_REVOKED",
            details=details,
            status_code=401
        )


class InsufficientPermissionsError(AuthException):
    """Недостаточно прав доступа"""

    def __init__(self, required_role: Optional[str] = None, user_role: Optional[str] = None):
        details = {}
        if required_role:
            details["required_role"] = required_role
        if user_role:
            details["user_role"] = user_role

        super().__init__(
            message="Insufficient permissions",
            code="INSUFFICIENT_PERMISSIONS",
            details=details,
            status_code=403
        )


class SessionExpiredError(AuthException):
    """Сессия истекла"""

    def __init__(self, session_id: Optional[str] = None):
        details = {"session_id": session_id} if session_id else {}
        super().__init__(
            message="Session has expired",
            code="SESSION_EXPIRED",
            details=details,
            status_code=401
        )


class TwoFactorRequiredError(AuthException):
    """Требуется двухфакторная аутентификация"""

    def __init__(self, message: str = "Two-factor authentication is required"):
        super().__init__(
            message=message,
            code="TWO_FACTOR_REQUIRED",
            status_code=401
        )


class TwoFactorCodeInvalidError(AuthException):
    """Неверный код двухфакторной аутентификации"""

    def __init__(self, message: str = "Invalid two-factor authentication code"):
        super().__init__(
            message=message,
            code="TWO_FACTOR_CODE_INVALID",
            status_code=401
        )
