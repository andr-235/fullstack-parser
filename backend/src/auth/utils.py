"""
Вспомогательные функции модуля Auth

Содержит утилиты для работы с аутентификацией и пользователями
"""

import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from .constants import (
    MAX_EMAIL_LENGTH,
    MAX_FULL_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    PASSWORD_MIN_LENGTH,
)


def validate_user_registration_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Валидировать данные регистрации пользователя

    Args:
        data: Данные для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    # Проверка обязательных полей
    required_fields = ["email", "full_name", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Обязательное поле '{field}' не заполнено"

    # Валидация email
    email = str(data["email"]).strip().lower()
    if not validate_email_format(email):
        return False, "Неверный формат email"

    if len(email) > MAX_EMAIL_LENGTH:
        return (
            False,
            f"Email слишком длинный (макс {MAX_EMAIL_LENGTH} символов)",
        )

    # Валидация имени
    full_name = str(data["full_name"]).strip()
    if len(full_name) > MAX_FULL_NAME_LENGTH:
        return (
            False,
            f"Имя слишком длинное (макс {MAX_FULL_NAME_LENGTH} символов)",
        )

    if not validate_name_format(full_name):
        return False, "Имя содержит недопустимые символы"

    # Валидация пароля
    password = str(data["password"])
    password_valid, password_error = validate_password_strength(password)
    if not password_valid:
        return False, password_error

    return True, ""


def validate_email_format(email: str) -> bool:
    """
    Валидировать формат email

    Args:
        email: Email для валидации

    Returns:
        bool: Валиден ли email
    """
    if not email or "@" not in email:
        return False

    # Простая регулярка для базовой валидации
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_name_format(name: str) -> bool:
    """
    Валидировать формат имени

    Args:
        name: Имя для валидации

    Returns:
        bool: Валидно ли имя
    """
    if not name:
        return False

    # Разрешены буквы, пробелы, дефисы, апострофы
    pattern = r"^[a-zA-Zа-яА-ЯёЁ\s\-']+$"
    return bool(re.match(pattern, name))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Валидировать сложность пароля

    Args:
        password: Пароль для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return (
            False,
            f"Пароль должен содержать минимум {PASSWORD_MIN_LENGTH} символов",
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        return (
            False,
            f"Пароль слишком длинный (макс {MAX_PASSWORD_LENGTH} символов)",
        )

    # Проверка наличия разных типов символов
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    if not (has_upper and has_lower and has_digit):
        return (
            False,
            "Пароль должен содержать заглавные и строчные буквы, а также цифры",
        )

    # Проверка на распространенные слабые пароли
    weak_passwords = [
        "password",
        "123456",
        "qwerty",
        "admin",
        "user",
        "password123",
        "123456789",
        "qwerty123",
    ]

    if password.lower() in weak_passwords:
        return False, "Пароль слишком простой, выберите более сложный"

    return True, ""


def generate_secure_token(length: int = 32) -> str:
    """
    Сгенерировать безопасный токен

    Args:
        length: Длина токена в байтах

    Returns:
        str: URL-safe токен
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """
    Захешировать токен для хранения

    Args:
        token: Токен для хеширования

    Returns:
        str: Хеш токена
    """
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()


def generate_password_reset_token() -> str:
    """
    Сгенерировать токен для сброса пароля

    Returns:
        str: Токен сброса пароля
    """
    return generate_secure_token(32)


def generate_email_verification_token() -> str:
    """
    Сгенерировать токен для верификации email

    Returns:
        str: Токен верификации
    """
    return generate_secure_token(32)


def normalize_email(email: str) -> str:
    """
    Нормализовать email (привести к нижнему регистру и удалить пробелы)

    Args:
        email: Email для нормализации

    Returns:
        str: Нормализованный email
    """
    return email.strip().lower()


def sanitize_user_input(text: str, max_length: int = 255) -> str:
    """
    Очистить пользовательский ввод

    Args:
        text: Текст для очистки
        max_length: Максимальная длина

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удалить лишние пробелы
    text = re.sub(r"\s+", " ", text.strip())

    # Удалить потенциально опасные символы
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    # Ограничить длину
    return text[:max_length]


def calculate_password_strength_score(password: str) -> int:
    """
    Вычислить оценку сложности пароля (0-100)

    Args:
        password: Пароль для оценки

    Returns:
        int: Оценка сложности
    """
    score = 0

    # Длина пароля
    length = len(password)
    if length >= 8:
        score += 25
    if length >= 12:
        score += 15
    if length >= 16:
        score += 10

    # Наличие разных типов символов
    if re.search(r"[a-z]", password):
        score += 10
    if re.search(r"[A-Z]", password):
        score += 10
    if re.search(r"\d", password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 15

    # Разнообразие символов
    unique_chars = len(set(password))
    if unique_chars > 10:
        score += 5
    if unique_chars > 15:
        score += 5

    # Штрафы за слабые пароли
    if password.lower() in ["password", "123456", "qwerty"]:
        score -= 20

    return max(0, min(100, score))


def is_password_compromised(password: str) -> bool:
    """
    Проверить, скомпрометирован ли пароль (заглушка)

    В реальном приложении здесь был бы запрос к API типа HaveIBeenPwned

    Args:
        password: Пароль для проверки

    Returns:
        bool: Скомпрометирован ли пароль
    """
    # Заглушка - в реальном приложении проверка через API
    compromised_passwords = [
        "password123",
        "qwerty123",
        "123456789",
        "admin123",
    ]

    return password.lower() in compromised_passwords


def extract_user_agent_info(user_agent: str) -> Dict[str, str]:
    """
    Извлечь информацию из User-Agent

    Args:
        user_agent: Строка User-Agent

    Returns:
        Dict[str, str]: Информация о клиенте
    """
    info = {
        "browser": "unknown",
        "os": "unknown",
        "device": "unknown",
    }

    if not user_agent:
        return info

    ua = user_agent.lower()

    # Определение браузера
    if "chrome" in ua and "safari" in ua:
        info["browser"] = "chrome"
    elif "firefox" in ua:
        info["browser"] = "firefox"
    elif "safari" in ua and "chrome" not in ua:
        info["browser"] = "safari"
    elif "edge" in ua:
        info["browser"] = "edge"
    elif "opera" in ua:
        info["browser"] = "opera"

    # Определение ОС
    if "windows" in ua:
        info["os"] = "windows"
    elif "macintosh" in ua or "mac os" in ua:
        info["os"] = "macos"
    elif "linux" in ua:
        info["os"] = "linux"
    elif "android" in ua:
        info["os"] = "android"
    elif "ios" in ua or "iphone" in ua or "ipad" in ua:
        info["os"] = "ios"

    # Определение устройства
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        info["device"] = "mobile"
    elif "tablet" in ua or "ipad" in ua:
        info["device"] = "tablet"
    else:
        info["device"] = "desktop"

    return info


def generate_session_id() -> str:
    """
    Сгенерировать ID сессии

    Returns:
        str: ID сессии
    """
    return secrets.token_hex(32)


def validate_session_id(session_id: str) -> bool:
    """
    Валидировать ID сессии

    Args:
        session_id: ID сессии для валидации

    Returns:
        bool: Валиден ли ID сессии
    """
    if not session_id or len(session_id) != 64:
        return False

    # Проверка на hex символы
    try:
        int(session_id, 16)
        return True
    except ValueError:
        return False


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Замаскировать чувствительные данные

    Args:
        data: Данные для маскировки
        visible_chars: Количество видимых символов в конце

    Returns:
        str: Замаскированные данные
    """
    if not data or len(data) <= visible_chars:
        return "*" * len(data)

    masked_length = len(data) - visible_chars
    return ("*" * masked_length) + data[-visible_chars:]


# Экспорт всех функций
__all__ = [
    "validate_user_registration_data",
    "validate_email_format",
    "validate_name_format",
    "validate_password_strength",
    "generate_secure_token",
    "hash_token",
    "generate_password_reset_token",
    "generate_email_verification_token",
    "normalize_email",
    "sanitize_user_input",
    "calculate_password_strength_score",
    "is_password_compromised",
    "extract_user_agent_info",
    "generate_session_id",
    "validate_session_id",
    "mask_sensitive_data",
]
