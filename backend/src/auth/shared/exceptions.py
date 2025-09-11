"""
Исключения модуля Auth

Содержит специфические исключения для модуля аутентификации
"""

class APIException(Exception):
    """Базовый класс для API исключений"""
    
    def __init__(self, status_code: int, detail: str, error_code: str = None, extra_data: dict = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.extra_data = extra_data or {}
        super().__init__(detail)


class ValidationError(APIException):
    """Ошибка валидации"""

    def __init__(self, message: str = "Ошибка валидации", field: str = None):
        extra_data = {"field": field} if field else {}
        super().__init__(
            status_code=422,
            detail=message,
            error_code="VALIDATION_ERROR",
            extra_data=extra_data,
        )


class AuthenticationError(APIException):
    """Ошибка аутентификации"""

    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(
            status_code=401,
            detail=message,
            error_code="AUTHENTICATION_ERROR",
        )


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    def __init__(self):
        super().__init__("Неверный email или пароль")


class UserNotFoundError(APIException):
    """Пользователь не найден"""

    def __init__(self, identifier: str):
        super().__init__(
            status_code=404,
            detail=f"Пользователь не найден: {identifier}",
            error_code="USER_NOT_FOUND",
            extra_data={"identifier": identifier},
        )


class UserInactiveError(APIException):
    """Пользователь не активен"""

    def __init__(self, user_id: int):
        super().__init__(
            status_code=403,
            detail="Аккаунт пользователя не активен",
            error_code="USER_INACTIVE",
            extra_data={"user_id": user_id},
        )


class UserSuspendedError(APIException):
    """Пользователь заблокирован"""

    def __init__(self, user_id: int, reason: str = None):
        extra_data = {"user_id": user_id}
        if reason:
            extra_data["reason"] = reason

        super().__init__(
            status_code=403,
            detail="Аккаунт пользователя заблокирован",
            error_code="USER_SUSPENDED",
            extra_data=extra_data,
        )


class InvalidTokenError(APIException):
    """Неверный токен"""

    def __init__(self, token_type: str = "токен"):
        super().__init__(
            status_code=401,
            detail=f"Неверный {token_type}",
            error_code="INVALID_TOKEN",
            extra_data={"token_type": token_type},
        )


class TokenExpiredError(APIException):
    """Токен истек"""

    def __init__(self, token_type: str = "токен"):
        super().__init__(
            status_code=401,
            detail=f"{token_type.title()} истек",
            error_code="TOKEN_EXPIRED",
            extra_data={"token_type": token_type},
        )


class InsufficientPermissionsError(APIException):
    """Недостаточно прав доступа"""

    def __init__(self, required_role: str = None, user_role: str = None):
        extra_data = {}
        if required_role:
            extra_data["required_role"] = required_role
        if user_role:
            extra_data["user_role"] = user_role

        super().__init__(
            status_code=403,
            detail="Недостаточно прав доступа",
            error_code="INSUFFICIENT_PERMISSIONS",
            extra_data=extra_data,
        )


class EmailAlreadyExistsError(APIException):
    """Email уже используется"""

    def __init__(self, email: str):
        super().__init__(
            status_code=409,
            detail="Пользователь с таким email уже существует",
            error_code="EMAIL_ALREADY_EXISTS",
            extra_data={"email": email},
        )


class InvalidEmailFormatError(APIException):
    """Неверный формат email"""

    def __init__(self, email: str):
        super().__init__(
            status_code=422,
            detail="Неверный формат email",
            error_code="INVALID_EMAIL_FORMAT",
            extra_data={"email": email},
        )


class PasswordTooWeakError(APIException):
    """Пароль слишком слабый"""

    def __init__(self, reason: str = None):
        detail = "Пароль слишком слабый"
        if reason:
            detail += f": {reason}"

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="PASSWORD_TOO_WEAK",
            extra_data={"reason": reason},
        )


class PasswordTooShortError(APIException):
    """Пароль слишком короткий"""

    def __init__(self):
        super().__init__(
            status_code=422,
            detail="Пароль должен содержать минимум 8 символов",
            error_code="PASSWORD_TOO_SHORT",
        )


class CurrentPasswordIncorrectError(APIException):
    """Неверный текущий пароль"""

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Неверный текущий пароль",
            error_code="CURRENT_PASSWORD_INCORRECT",
        )


class PasswordResetTokenInvalidError(APIException):
    """Неверный токен сброса пароля"""

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Неверный токен сброса пароля",
            error_code="PASSWORD_RESET_TOKEN_INVALID",
        )


class PasswordResetTokenExpiredError(APIException):
    """Токен сброса пароля истек"""

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Токен сброса пароля истек",
            error_code="PASSWORD_RESET_TOKEN_EXPIRED",
        )


class EmailVerificationTokenInvalidError(APIException):
    """Неверный токен верификации email"""

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Неверный токен верификации email",
            error_code="EMAIL_VERIFICATION_TOKEN_INVALID",
        )


class TooManyAttemptsError(APIException):
    """Слишком много попыток"""

    def __init__(self, action: str, retry_after: int = None):
        extra_data = {"action": action}
        if retry_after:
            extra_data["retry_after"] = retry_after

        super().__init__(
            status_code=429,
            detail=f"Слишком много попыток {action}",
            error_code="TOO_MANY_ATTEMPTS",
            extra_data=extra_data,
        )


class RegistrationDisabledError(APIException):
    """Регистрация отключена"""

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Регистрация новых пользователей временно отключена",
            error_code="REGISTRATION_DISABLED",
        )


class EmailVerificationRequiredError(APIException):
    """Требуется верификация email"""

    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Необходимо подтвердить email перед входом в систему",
            error_code="EMAIL_VERIFICATION_REQUIRED",
        )


class AccountLockedError(APIException):
    """Аккаунт заблокирован"""

    def __init__(self, unlock_time: str = None):
        extra_data = {}
        if unlock_time:
            extra_data["unlock_time"] = unlock_time

        super().__init__(
            status_code=423,
            detail="Аккаунт временно заблокирован из-за слишком большого количества неудачных попыток входа",
            error_code="ACCOUNT_LOCKED",
            extra_data=extra_data,
        )


# Экспорт всех исключений
__all__ = [
    "APIException",
    "ValidationError",
    "AuthenticationError",
    "InvalidCredentialsError",
    "UserNotFoundError",
    "UserInactiveError",
    "UserSuspendedError",
    "InvalidTokenError",
    "TokenExpiredError",
    "InsufficientPermissionsError",
    "EmailAlreadyExistsError",
    "InvalidEmailFormatError",
    "PasswordTooWeakError",
    "PasswordTooShortError",
    "CurrentPasswordIncorrectError",
    "PasswordResetTokenInvalidError",
    "PasswordResetTokenExpiredError",
    "EmailVerificationTokenInvalidError",
    "TooManyAttemptsError",
    "RegistrationDisabledError",
    "EmailVerificationRequiredError",
    "AccountLockedError",
]
