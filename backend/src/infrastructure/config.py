"""
Конфигурация инфраструктурных сервисов

Централизованное управление настройками для всех инфраструктурных компонентов
"""

import os
from typing import Dict, Any, Optional


class InfrastructureConfig:
    """Централизованная конфигурация инфраструктуры"""

    # === SECURITY CONFIG ===
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    API_KEY_MIN_LENGTH = int(os.getenv("API_KEY_MIN_LENGTH", "16"))

    # === CACHE CONFIG ===
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # 5 minutes
    CACHE_PREFIX = os.getenv("CACHE_PREFIX", "vk_parser")
    CACHE_DECODE_RESPONSES = os.getenv("CACHE_DECODE_RESPONSES", "true").lower() == "true"
    CACHE_RETRY_ON_TIMEOUT = os.getenv("CACHE_RETRY_ON_TIMEOUT", "true").lower() == "true"
    CACHE_SOCKET_TIMEOUT = int(os.getenv("CACHE_SOCKET_TIMEOUT", "5"))
    CACHE_SOCKET_CONNECT_TIMEOUT = int(os.getenv("CACHE_SOCKET_CONNECT_TIMEOUT", "5"))

    # === LOGGING CONFIG ===
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    LOGGING_FORMAT = os.getenv(
        "LOGGING_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOGGING_DATE_FORMAT = os.getenv("LOGGING_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    # === HASHING CONFIG ===
    DEFAULT_HASH_ALGORITHM = os.getenv("DEFAULT_HASH_ALGORITHM", "sha256")
    SUPPORTED_HASH_ALGORITHMS = ["sha256", "sha512", "md5"]
    HMAC_KEY_LENGTH = int(os.getenv("HMAC_KEY_LENGTH", "32"))

    # === TIME UTILS CONFIG ===
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")
    BUSINESS_DAYS_WEEKDAYS = [0, 1, 2, 3, 4]  # Monday to Friday

    # === METRICS CONFIG ===
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    METRICS_PREFIX = os.getenv("METRICS_PREFIX", "infrastructure")

    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию безопасности"""
        return {
            "secret_key": cls.SECRET_KEY,
            "jwt_algorithm": cls.JWT_ALGORITHM,
            "access_token_expire_minutes": cls.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": cls.REFRESH_TOKEN_EXPIRE_DAYS,
            "password_min_length": cls.PASSWORD_MIN_LENGTH,
            "api_key_min_length": cls.API_KEY_MIN_LENGTH,
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "redis_url": cls.REDIS_URL,
            "default_ttl": cls.CACHE_DEFAULT_TTL,
            "prefix": cls.CACHE_PREFIX,
            "decode_responses": cls.CACHE_DECODE_RESPONSES,
            "retry_on_timeout": cls.CACHE_RETRY_ON_TIMEOUT,
            "socket_timeout": cls.CACHE_SOCKET_TIMEOUT,
            "socket_connect_timeout": cls.CACHE_SOCKET_CONNECT_TIMEOUT,
        }

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию логирования"""
        return {
            "level": cls.LOGGING_LEVEL,
            "format": cls.LOGGING_FORMAT,
            "date_format": cls.LOGGING_DATE_FORMAT,
        }

    @classmethod
    def get_hashing_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию хеширования"""
        return {
            "default_algorithm": cls.DEFAULT_HASH_ALGORITHM,
            "supported_algorithms": cls.SUPPORTED_HASH_ALGORITHMS,
            "hmac_key_length": cls.HMAC_KEY_LENGTH,
        }

    @classmethod
    def get_time_utils_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию утилит времени"""
        return {
            "default_timezone": cls.DEFAULT_TIMEZONE,
            "business_days_weekdays": cls.BUSINESS_DAYS_WEEKDAYS,
        }

    @classmethod
    def get_metrics_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию метрик"""
        return {
            "enabled": cls.METRICS_ENABLED,
            "prefix": cls.METRICS_PREFIX,
        }

    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Получить всю конфигурацию"""
        return {
            "security": cls.get_security_config(),
            "cache": cls.get_cache_config(),
            "logging": cls.get_logging_config(),
            "hashing": cls.get_hashing_config(),
            "time_utils": cls.get_time_utils_config(),
            "metrics": cls.get_metrics_config(),
        }


# Глобальный экземпляр конфигурации
infrastructure_config = InfrastructureConfig()


# Экспорт
__all__ = [
    "InfrastructureConfig",
    "infrastructure_config",
]
