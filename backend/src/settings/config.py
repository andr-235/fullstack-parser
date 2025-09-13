"""
Конфигурация модуля Settings

Содержит настройки специфичные для модуля управления настройками
"""

from typing import Optional, Dict, Any

from settings.config import settings


class SettingsConfig:
    """Конфигурация для модуля Settings"""

    # Основные настройки модуля
    ENABLED = True
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 минут
    VALIDATION_ENABLED = True
    AUDIT_ENABLED = True

    # Настройки экспорта/импорта
    EXPORT_FORMAT = "json"
    EXPORT_COMPRESSION = False
    IMPORT_MERGE_DEFAULT = True
    IMPORT_BACKUP_BEFORE_IMPORT = True

    # Настройки валидации
    VALIDATION_STRICT_MODE = False
    VALIDATION_ALLOW_UNKNOWN_SECTIONS = False
    VALIDATION_ALLOW_UNKNOWN_KEYS = False

    # Настройки аудита
    AUDIT_LOG_CHANGES = True
    AUDIT_LOG_ACCESS = False
    AUDIT_RETENTION_DAYS = 90

    # Настройки кеширования
    CACHE_PREFIX = "settings"
    CACHE_SECTIONS_SEPARATELY = True
    CACHE_VALUES_SEPARATELY = False

    # Настройки производительности
    MAX_SETTINGS_SIZE = 1024 * 1024  # 1MB
    MAX_SECTIONS_COUNT = 50
    MAX_VALUES_PER_SECTION = 100

    # Настройки безопасности
    REQUIRE_AUTH_FOR_WRITE = True
    REQUIRE_ADMIN_FOR_CRITICAL = True
    ALLOW_RESET_TO_DEFAULTS = True

    # Критические секции (требуют админ прав)
    CRITICAL_SECTIONS = ["database", "security", "cache"]

    # Секции только для чтения
    READONLY_SECTIONS = ["system"]

    # Настройки по умолчанию для секций
    DEFAULT_SECTIONS = {
        "vk_api": {
            "access_token": "",
            "api_version": "5.199",
            "requests_per_second": 3,
            "max_posts_per_request": 10,
            "max_comments_per_request": 100,
            "max_groups_per_request": 10000,
            "max_users_per_request": 1000,
        },
        "monitoring": {
            "scheduler_interval_seconds": 300,
            "max_concurrent_groups": 5,
            "group_delay_seconds": 1.0,
            "auto_start_scheduler": False,
            "enabled": True,
            "health_check_interval": 60,
        },
        "database": {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
            "echo": False,
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "include_timestamp": True,
        },
        "ui": {
            "theme": "system",
            "auto_refresh": True,
            "refresh_interval": 30,
            "items_per_page": 20,
            "show_notifications": True,
        },
        "cache": {
            "enabled": True,
            "ttl": 300,
            "max_size": 1000,
            "backend": "memory",
        },
        "security": {
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
            "password_min_length": 8,
            "require_special_chars": True,
        },
    }

    # Настройки метрик
    METRICS_ENABLED = True
    METRICS_PREFIX = "settings"
    METRICS_UPDATE_INTERVAL = 60

    # Настройки логирования
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "json"
    LOG_FILE = None

    @classmethod
    def get_default_settings(cls) -> Dict[str, Any]:
        """Получить настройки по умолчанию"""
        return cls.DEFAULT_SECTIONS.copy()

    @classmethod
    def get_critical_sections(cls) -> list:
        """Получить список критических секций"""
        return cls.CRITICAL_SECTIONS.copy()

    @classmethod
    def get_readonly_sections(cls) -> list:
        """Получить список секций только для чтения"""
        return cls.READONLY_SECTIONS.copy()

    @classmethod
    def is_critical_section(cls, section: str) -> bool:
        """Проверить, является ли секция критической"""
        return section in cls.CRITICAL_SECTIONS

    @classmethod
    def is_readonly_section(cls, section: str) -> bool:
        """Проверить, является ли секция только для чтения"""
        return section in cls.READONLY_SECTIONS

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": cls.CACHE_ENABLED,
            "ttl": cls.CACHE_TTL,
            "prefix": cls.CACHE_PREFIX,
            "sections_separately": cls.CACHE_SECTIONS_SEPARATELY,
            "values_separately": cls.CACHE_VALUES_SEPARATELY,
        }

    @classmethod
    def get_validation_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию валидации"""
        return {
            "enabled": cls.VALIDATION_ENABLED,
            "strict_mode": cls.VALIDATION_STRICT_MODE,
            "allow_unknown_sections": cls.VALIDATION_ALLOW_UNKNOWN_SECTIONS,
            "allow_unknown_keys": cls.VALIDATION_ALLOW_UNKNOWN_KEYS,
        }

    @classmethod
    def get_audit_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию аудита"""
        return {
            "enabled": cls.AUDIT_ENABLED,
            "log_changes": cls.AUDIT_LOG_CHANGES,
            "log_access": cls.AUDIT_LOG_ACCESS,
            "retention_days": cls.AUDIT_RETENTION_DAYS,
        }

    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию безопасности"""
        return {
            "require_auth_for_write": cls.REQUIRE_AUTH_FOR_WRITE,
            "require_admin_for_critical": cls.REQUIRE_ADMIN_FOR_CRITICAL,
            "allow_reset_to_defaults": cls.ALLOW_RESET_TO_DEFAULTS,
            "critical_sections": cls.CRITICAL_SECTIONS,
            "readonly_sections": cls.READONLY_SECTIONS,
        }

    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию производительности"""
        return {
            "max_settings_size": cls.MAX_SETTINGS_SIZE,
            "max_sections_count": cls.MAX_SECTIONS_COUNT,
            "max_values_per_section": cls.MAX_VALUES_PER_SECTION,
        }

    @classmethod
    def get_metrics_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию метрик"""
        return {
            "enabled": cls.METRICS_ENABLED,
            "prefix": cls.METRICS_PREFIX,
            "update_interval": cls.METRICS_UPDATE_INTERVAL,
        }

    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию логирования"""
        return {
            "level": cls.LOG_LEVEL,
            "format": cls.LOG_FORMAT,
            "file": cls.LOG_FILE,
        }

    @classmethod
    def get_export_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию экспорта"""
        return {
            "format": cls.EXPORT_FORMAT,
            "compression": cls.EXPORT_COMPRESSION,
        }

    @classmethod
    def get_import_config(cls) -> Dict[str, Any]:
        """Получить конфигурацию импорта"""
        return {
            "merge_default": cls.IMPORT_MERGE_DEFAULT,
            "backup_before_import": cls.IMPORT_BACKUP_BEFORE_IMPORT,
        }


# Экземпляр конфигурации
settings_config = SettingsConfig()


# Экспорт
__all__ = [
    "SettingsConfig",
    "settings_config",
]
