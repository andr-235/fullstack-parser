"""
Модуль Parser

Модуль для парсинга данных из VK API с использованием FastAPI
"""

# Основные компоненты
from parser.config import ParserSettings, parser_settings
from parser.service import ParserService
from parser.models import TaskStatus, TaskPriority, ParsingTaskModel
from parser.schemas import (
    ParseRequest,
    ParseResponse,
    ParseStatus,
    ParserState,
    StopParseRequest,
    StopParseResponse,
    VKGroupInfo,
    VKPostInfo,
    VKCommentInfo,
    ParseResult,
    ParseTask,
    ParseTaskListResponse,
    ParseStats,
    VKAPIError,
)
from parser.exceptions import (
    TaskNotFoundException,
    InvalidTaskDataException,
    ParsingException,
    VKAPITimeoutException,
    VKAPILimitExceededException,
    ParserConfigurationException,
    ParserDataValidationException,
    ParserServiceUnavailableException,
)
from parser.dependencies import get_parser_service
from parser.router import router as parser_router
from parser.group_parser import GroupParser, VKAPIServiceProtocol

# Версия модуля
__version__ = "2.0.0"

# Основные экспорты
__all__ = [
    # Конфигурация
    "ParserSettings",
    "parser_settings",
    # Модели
    "TaskStatus",
    "TaskPriority",
    "ParsingTaskModel",
    # Схемы
    "ParseRequest",
    "ParseResponse",
    "ParseStatus",
    "ParserState",
    "StopParseRequest",
    "StopParseResponse",
    "VKGroupInfo",
    "VKPostInfo",
    "VKCommentInfo",
    "ParseResult",
    "ParseTask",
    "ParseTaskListResponse",
    "ParseStats",
    "VKAPIError",
    # Исключения
    "TaskNotFoundException",
    "InvalidTaskDataException",
    "ParsingException",
    "VKAPITimeoutException",
    "VKAPILimitExceededException",
    "ParserConfigurationException",
    "ParserDataValidationException",
    "ParserServiceUnavailableException",
    # Зависимости
    "get_parser_service",
    # Роутер
    "parser_router",
    # Сервис
    "ParserService",
    "GroupParser",
    "VKAPIServiceProtocol",
    # Метаданные
    "__version__",
]
