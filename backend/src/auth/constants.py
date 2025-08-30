"""
Константы модуля Auth

Содержит все константы используемые в модуле аутентификации
"""

# Роли пользователей
ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_SUPERUSER = "superuser"

# Допустимые роли
ALLOWED_ROLES = [
    ROLE_USER,
    ROLE_ADMIN,
    ROLE_SUPERUSER,
]

# Статусы пользователей
USER_STATUS_ACTIVE = "active"
USER_STATUS_INACTIVE = "inactive"
USER_STATUS_PENDING = "pending"
USER_STATUS_SUSPENDED = "suspended"

# Допустимые статусы пользователей
ALLOWED_USER_STATUSES = [
    USER_STATUS_ACTIVE,
    USER_STATUS_INACTIVE,
    USER_STATUS_PENDING,
    USER_STATUS_SUSPENDED,
]

# Типы токенов
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_RESET = "reset"
TOKEN_TYPE_VERIFICATION = "verification"

# Допустимые типы токенов
ALLOWED_TOKEN_TYPES = [
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TOKEN_TYPE_RESET,
    TOKEN_TYPE_VERIFICATION,
]

# Методы аутентификации
AUTH_METHOD_PASSWORD = "password"
AUTH_METHOD_OAUTH = "oauth"
AUTH_METHOD_TOKEN = "token"

# Допустимые методы аутентификации
ALLOWED_AUTH_METHODS = [
    AUTH_METHOD_PASSWORD,
    AUTH_METHOD_OAUTH,
    AUTH_METHOD_TOKEN,
]

# Сообщения об ошибках
ERROR_INVALID_CREDENTIALS = "Неверные учетные данные"
ERROR_USER_NOT_FOUND = "Пользователь не найден"
ERROR_USER_INACTIVE = "Аккаунт не активен"
ERROR_USER_SUSPENDED = "Аккаунт заблокирован"
ERROR_INVALID_TOKEN = "Неверный токен"
ERROR_TOKEN_EXPIRED = "Токен истек"
ERROR_INSUFFICIENT_PERMISSIONS = "Недостаточно прав доступа"
ERROR_EMAIL_ALREADY_EXISTS = "Email уже используется"
ERROR_INVALID_EMAIL_FORMAT = "Неверный формат email"
ERROR_PASSWORD_TOO_WEAK = "Пароль слишком слабый"
ERROR_PASSWORD_TOO_SHORT = "Пароль слишком короткий"
ERROR_CURRENT_PASSWORD_INCORRECT = "Неверный текущий пароль"
ERROR_RESET_TOKEN_INVALID = "Неверный токен сброса пароля"
ERROR_RESET_TOKEN_EXPIRED = "Токен сброса пароля истек"
ERROR_VERIFICATION_TOKEN_INVALID = "Неверный токен верификации"
ERROR_TOO_MANY_ATTEMPTS = "Слишком много попыток"

# Сообщения об успехе
SUCCESS_USER_CREATED = "Пользователь успешно создан"
SUCCESS_USER_UPDATED = "Пользователь успешно обновлен"
SUCCESS_USER_DELETED = "Пользователь успешно удален"
SUCCESS_LOGIN_SUCCESSFUL = "Вход выполнен успешно"
SUCCESS_LOGOUT_SUCCESSFUL = "Выход выполнен успешно"
SUCCESS_PASSWORD_CHANGED = "Пароль успешно изменен"
SUCCESS_PASSWORD_RESET_REQUESTED = "Запрос на сброс пароля отправлен"
SUCCESS_PASSWORD_RESET = "Пароль успешно сброшен"
SUCCESS_EMAIL_VERIFIED = "Email успешно подтвержден"
SUCCESS_TOKEN_REFRESHED = "Токен успешно обновлен"

# Названия полей для API
API_FIELD_ID = "id"
API_FIELD_EMAIL = "email"
API_FIELD_FULL_NAME = "full_name"
API_FIELD_PASSWORD = "password"
API_FIELD_CURRENT_PASSWORD = "current_password"
API_FIELD_NEW_PASSWORD = "new_password"
API_FIELD_IS_ACTIVE = "is_active"
API_FIELD_IS_SUPERUSER = "is_superuser"
API_FIELD_ROLE = "role"
API_FIELD_STATUS = "status"
API_FIELD_CREATED_AT = "created_at"
API_FIELD_UPDATED_AT = "updated_at"
API_FIELD_LAST_LOGIN = "last_login"
API_FIELD_ACCESS_TOKEN = "access_token"
API_FIELD_REFRESH_TOKEN = "refresh_token"
API_FIELD_TOKEN_TYPE = "token_type"
API_FIELD_EXPIRES_IN = "expires_in"
API_FIELD_TOKEN = "token"

# Максимальные значения
MAX_EMAIL_LENGTH = 255
MAX_FULL_NAME_LENGTH = 255
MAX_PASSWORD_LENGTH = 128
MAX_TOKEN_LENGTH = 512

# Настройки кеширования
CACHE_KEY_USER = "auth:user:{user_id}"
CACHE_KEY_USER_EMAIL = "auth:user:email:{email}"
CACHE_KEY_TOKEN = "auth:token:{token_hash}"
CACHE_KEY_RESET_TOKEN = "auth:reset:{token_hash}"
CACHE_KEY_VERIFICATION_TOKEN = "auth:verification:{token_hash}"

# Таймауты кеша
CACHE_USER_TTL = 300  # 5 минут
CACHE_TOKEN_TTL = 3600  # 1 час
CACHE_RESET_TOKEN_TTL = 86400  # 24 часа
CACHE_VERIFICATION_TOKEN_TTL = 604800  # 7 дней

# Настройки rate limiting
RATE_LIMIT_LOGIN = "login"
RATE_LIMIT_REGISTER = "register"
RATE_LIMIT_PASSWORD_RESET = "password_reset"

# Правила rate limiting
RATE_LIMIT_RULES = {
    RATE_LIMIT_LOGIN: {"requests": 5, "window": 60},  # 5 попыток в минуту
    RATE_LIMIT_REGISTER: {"requests": 3, "window": 3600},  # 3 попытки в час
    RATE_LIMIT_PASSWORD_RESET: {
        "requests": 3,
        "window": 3600,
    },  # 3 попытки в час
}

# Настройки логирования
LOG_LOGIN_SUCCESS = "Пользователь {email} вошел в систему"
LOG_LOGIN_FAILED = "Неудачная попытка входа для {email}"
LOG_LOGOUT = "Пользователь {email} вышел из системы"
LOG_PASSWORD_CHANGED = "Пользователь {email} изменил пароль"
LOG_PASSWORD_RESET_REQUESTED = "Запрос сброса пароля для {email}"
LOG_PASSWORD_RESET = "Пароль сброшен для {email}"
LOG_USER_CREATED = "Создан новый пользователь {email}"
LOG_USER_UPDATED = "Обновлен пользователь {email}"
LOG_USER_DELETED = "Удален пользователь {email}"
LOG_TOKEN_REFRESHED = "Обновлен токен для пользователя {email}"

# Настройки email
EMAIL_VERIFICATION_SUBJECT = "Подтверждение email"
EMAIL_PASSWORD_RESET_SUBJECT = "Сброс пароля"
EMAIL_FROM_NAME = "VK Comments Parser"
EMAIL_FROM_EMAIL = "noreply@vkcomments.com"

# Шаблоны email
EMAIL_VERIFICATION_TEMPLATE = """
Здравствуйте, {full_name}!

Для подтверждения вашего email перейдите по ссылке:
{verification_url}

Если вы не регистрировались в системе, проигнорируйте это письмо.

С уважением,
Команда VK Comments Parser
"""

EMAIL_PASSWORD_RESET_TEMPLATE = """
Здравствуйте, {full_name}!

Для сброса пароля перейдите по ссылке:
{reset_url}

Ссылка действительна в течение 24 часов.

Если вы не запрашивали сброс пароля, проигнорируйте это письмо.

С уважением,
Команда VK Comments Parser
"""

# Настройки OAuth (для будущих расширений)
OAUTH_PROVIDERS = {
    "google": {
        "client_id": None,
        "client_secret": None,
        "redirect_uri": None,
        "scope": ["openid", "email", "profile"],
    },
    "github": {
        "client_id": None,
        "client_secret": None,
        "redirect_uri": None,
        "scope": ["user:email"],
    },
}

# Настройки сессий
SESSION_COOKIE_NAME = "session_token"
SESSION_COOKIE_MAX_AGE = 86400  # 24 часа
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "lax"

# Настройки CORS для аутентификации
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "Origin",
    "X-Requested-With",
]


# Экспорт всех констант
__all__ = [
    # Роли пользователей
    "ROLE_USER",
    "ROLE_ADMIN",
    "ROLE_SUPERUSER",
    "ALLOWED_ROLES",
    # Статусы пользователей
    "USER_STATUS_ACTIVE",
    "USER_STATUS_INACTIVE",
    "USER_STATUS_PENDING",
    "USER_STATUS_SUSPENDED",
    "ALLOWED_USER_STATUSES",
    # Типы токенов
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
    "TOKEN_TYPE_RESET",
    "TOKEN_TYPE_VERIFICATION",
    "ALLOWED_TOKEN_TYPES",
    # Методы аутентификации
    "AUTH_METHOD_PASSWORD",
    "AUTH_METHOD_OAUTH",
    "AUTH_METHOD_TOKEN",
    "ALLOWED_AUTH_METHODS",
    # Сообщения об ошибках
    "ERROR_INVALID_CREDENTIALS",
    "ERROR_USER_NOT_FOUND",
    "ERROR_USER_INACTIVE",
    "ERROR_USER_SUSPENDED",
    "ERROR_INVALID_TOKEN",
    "ERROR_TOKEN_EXPIRED",
    "ERROR_INSUFFICIENT_PERMISSIONS",
    "ERROR_EMAIL_ALREADY_EXISTS",
    "ERROR_INVALID_EMAIL_FORMAT",
    "ERROR_PASSWORD_TOO_WEAK",
    "ERROR_PASSWORD_TOO_SHORT",
    "ERROR_CURRENT_PASSWORD_INCORRECT",
    "ERROR_RESET_TOKEN_INVALID",
    "ERROR_RESET_TOKEN_EXPIRED",
    "ERROR_VERIFICATION_TOKEN_INVALID",
    "ERROR_TOO_MANY_ATTEMPTS",
    # Сообщения об успехе
    "SUCCESS_USER_CREATED",
    "SUCCESS_USER_UPDATED",
    "SUCCESS_USER_DELETED",
    "SUCCESS_LOGIN_SUCCESSFUL",
    "SUCCESS_LOGOUT_SUCCESSFUL",
    "SUCCESS_PASSWORD_CHANGED",
    "SUCCESS_PASSWORD_RESET_REQUESTED",
    "SUCCESS_PASSWORD_RESET",
    "SUCCESS_EMAIL_VERIFIED",
    "SUCCESS_TOKEN_REFRESHED",
    # API поля
    "API_FIELD_ID",
    "API_FIELD_EMAIL",
    "API_FIELD_FULL_NAME",
    "API_FIELD_PASSWORD",
    "API_FIELD_CURRENT_PASSWORD",
    "API_FIELD_NEW_PASSWORD",
    "API_FIELD_IS_ACTIVE",
    "API_FIELD_IS_SUPERUSER",
    "API_FIELD_ROLE",
    "API_FIELD_STATUS",
    "API_FIELD_CREATED_AT",
    "API_FIELD_UPDATED_AT",
    "API_FIELD_LAST_LOGIN",
    "API_FIELD_ACCESS_TOKEN",
    "API_FIELD_REFRESH_TOKEN",
    "API_FIELD_TOKEN_TYPE",
    "API_FIELD_EXPIRES_IN",
    "API_FIELD_TOKEN",
    # Максимальные значения
    "MAX_EMAIL_LENGTH",
    "MAX_FULL_NAME_LENGTH",
    "MAX_PASSWORD_LENGTH",
    "MAX_TOKEN_LENGTH",
    # Кеширование
    "CACHE_KEY_USER",
    "CACHE_KEY_USER_EMAIL",
    "CACHE_KEY_TOKEN",
    "CACHE_KEY_RESET_TOKEN",
    "CACHE_KEY_VERIFICATION_TOKEN",
    "CACHE_USER_TTL",
    "CACHE_TOKEN_TTL",
    "CACHE_RESET_TOKEN_TTL",
    "CACHE_VERIFICATION_TOKEN_TTL",
    # Rate limiting
    "RATE_LIMIT_LOGIN",
    "RATE_LIMIT_REGISTER",
    "RATE_LIMIT_PASSWORD_RESET",
    "RATE_LIMIT_RULES",
    # Логирование
    "LOG_LOGIN_SUCCESS",
    "LOG_LOGIN_FAILED",
    "LOG_LOGOUT",
    "LOG_PASSWORD_CHANGED",
    "LOG_PASSWORD_RESET_REQUESTED",
    "LOG_PASSWORD_RESET",
    "LOG_USER_CREATED",
    "LOG_USER_UPDATED",
    "LOG_USER_DELETED",
    "LOG_TOKEN_REFRESHED",
    # Email
    "EMAIL_VERIFICATION_SUBJECT",
    "EMAIL_PASSWORD_RESET_SUBJECT",
    "EMAIL_FROM_NAME",
    "EMAIL_FROM_EMAIL",
    "EMAIL_VERIFICATION_TEMPLATE",
    "EMAIL_PASSWORD_RESET_TEMPLATE",
    # OAuth
    "OAUTH_PROVIDERS",
    # Сессии
    "SESSION_COOKIE_NAME",
    "SESSION_COOKIE_MAX_AGE",
    "SESSION_COOKIE_SECURE",
    "SESSION_COOKIE_HTTPONLY",
    "SESSION_COOKIE_SAMESITE",
    # CORS
    "CORS_ALLOW_CREDENTIALS",
    "CORS_ALLOW_HEADERS",
]
