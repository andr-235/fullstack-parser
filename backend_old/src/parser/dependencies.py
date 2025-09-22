"""
Зависимости для модуля Parser

Определяет FastAPI зависимости для работы с парсером
"""

from vk_api.dependencies import create_vk_api_service

# Глобальный экземпляр сервиса парсера для сохранения состояния задач
_parser_service_instance = None


async def get_parser_service():
    """
    Получить сервис парсера (синглтон)

    Returns:
        ParserService: Сервис для бизнес-логики парсинга
    """
    global _parser_service_instance

    # Создаем экземпляр только один раз
    if _parser_service_instance is None:
        # Импорт здесь для избежания циклических зависимостей
        from .group_parser import GroupParser
        from .service import ParserService

        vk_api_service = await create_vk_api_service()
        group_parser = GroupParser(vk_api_service)
        _parser_service_instance = ParserService(group_parser)

    return _parser_service_instance


# Экспорт зависимостей
__all__ = [
    "get_parser_service",
]
