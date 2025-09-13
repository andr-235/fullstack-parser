"""
Конфигурация модуля Health
"""

from typing import List


class HealthConfig:
    """Конфигурация для модуля Health"""
    
    # Основные настройки
    ENABLED = True
    CHECK_TIMEOUT = 10  # seconds
    CACHE_TTL = 60  # seconds
    
    # Компоненты для проверки
    COMPONENTS = ["database", "memory", "disk", "cpu", "process"]
    CRITICAL_COMPONENTS = ["database", "process"]
    
    # Пороги для метрик
    MEMORY_CRITICAL = 90.0  # %
    MEMORY_WARNING = 80.0   # %
    DISK_CRITICAL = 95.0    # %
    DISK_WARNING = 85.0     # %
    CPU_CRITICAL = 95.0     # %
    CPU_WARNING = 80.0      # %
    
    # Настройки повторных попыток
    RETRY_MAX_ATTEMPTS = 3
    RETRY_BACKOFF_FACTOR = 2.0
    
    @classmethod
    def is_critical(cls, component: str) -> bool:
        """Проверить, является ли компонент критическим"""
        return component in cls.CRITICAL_COMPONENTS
    
    @classmethod
    def get_components(cls) -> List[str]:
        """Получить список компонентов"""
        return cls.COMPONENTS.copy()


# Экземпляр конфигурации
health_config = HealthConfig()


__all__ = ["HealthConfig", "health_config"]
