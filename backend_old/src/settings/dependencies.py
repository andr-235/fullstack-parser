"""
Зависимости для модуля Settings

Определяет FastAPI зависимости для работы с настройками
"""


from settings.service import SettingsService


async def get_settings_service() -> SettingsService:
    """
    Получить сервис настроек

    Returns:
        SettingsService: Сервис настроек
    """
    return SettingsService()


# Экспорт зависимостей
__all__ = [
    "get_settings_service",
]
