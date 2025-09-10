"""
Модуль Parser

Модуль для парсинга данных из VK API с использованием FastAPI
"""

# Импорт основных компонентов
from .config import ParserSettings, ParserConfig, parser_settings
from .service import ParserService
from .models import (
    TaskStatus,
    TaskPriority,
    ParsingTask,
    ParsingTaskModel,
    ParserRepository,
)
from .schemas import (
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
from .exceptions import (
    TaskNotFoundException,
    InvalidTaskDataException,
    ParsingException,
    VKAPITimeoutException,
    VKAPILimitExceededException,
    ParserConfigurationException,
    ParserDataValidationException,
    ParserServiceUnavailableException,
)
from .dependencies import (
    get_parser_repository,
    get_parser_vk_api_service,
    get_parser_service,
)
from .router import router as parser_router

# Импорт утилит (объединенные)
from .utils import (
    retry_with_backoff,
    measure_execution_time,
    create_batch_chunks,
    safe_get,
    merge_dicts,
    filter_none_values,
    convert_to_utc,
    format_timestamp,
    calculate_percentage,
    clamp,
    is_valid_email,
    is_valid_url,
    truncate_string,
    deduplicate_list,
    chunked_async_generator,
    # Функции из data_utils
    generate_task_id,
    calculate_estimated_time,
    format_duration,
    format_file_size,
    clean_text,
    extract_hashtags,
    extract_mentions,
    calculate_sentiment_score,
    group_data_by_field,
    filter_data_by_condition,
    sort_data_by_field,
    calculate_statistics,
)

# Основные компоненты (объединенные)
from .service import (
    ParserService,
    TaskManager,
    VKAPIErrorHandler,
    ServiceErrorHandler,
)
from .group_parser import (
    GroupParser,
    VKAPIServiceProtocol,
    # VK Utils
    RateLimiter,
    parse_vk_error,
    extract_posts_from_response,
    extract_comments_from_response,
    extract_groups_from_response,
    extract_users_from_response,
    normalize_group_id,
    format_group_id_for_api,
    build_vk_api_url,
    parse_vk_date,
    format_vk_date,
    extract_photo_url,
    extract_video_url,
    extract_audio_url,
    is_private_group,
    is_deleted_group,
    is_banned_group,
    calculate_group_activity_score,
)
from .schemas import VKAPIValidators

# Версия модуля
__version__ = "2.0.0"

# Основные экспорты
__all__ = [
    # Конфигурация
    "ParserSettings",
    "ParserConfig",
    "parser_settings",
    # Модели
    "TaskStatus",
    "TaskPriority",
    "ParsingTask",
    "ParsingTaskModel",
    "ParserRepository",
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
    "get_parser_repository",
    "get_parser_vk_api_service",
    "get_parser_service",
    # Роутер
    "parser_router",
    # Сервис
    "ParserService",
    # Утилиты (объединенные)
    "retry_with_backoff",
    "measure_execution_time",
    "create_batch_chunks",
    "safe_get",
    "merge_dicts",
    "filter_none_values",
    "convert_to_utc",
    "format_timestamp",
    "calculate_percentage",
    "clamp",
    "is_valid_email",
    "is_valid_url",
    "truncate_string",
    "deduplicate_list",
    "chunked_async_generator",
    # Функции из data_utils
    "generate_task_id",
    "calculate_estimated_time",
    "format_duration",
    "format_file_size",
    "clean_text",
    "extract_hashtags",
    "extract_mentions",
    "calculate_sentiment_score",
    "group_data_by_field",
    "filter_data_by_condition",
    "sort_data_by_field",
    "calculate_statistics",
    # Основные компоненты (объединенные)
    "TaskManager",
    "GroupParser",
    "VKAPIServiceProtocol",
    "VKAPIErrorHandler",
    "ServiceErrorHandler",
    "VKAPIValidators",
    # VK утилиты
    "RateLimiter",
    "parse_vk_error",
    "extract_posts_from_response",
    "extract_comments_from_response",
    "extract_groups_from_response",
    "extract_users_from_response",
    "normalize_group_id",
    "format_group_id_for_api",
    "build_vk_api_url",
    "parse_vk_date",
    "format_vk_date",
    "extract_photo_url",
    "extract_video_url",
    "extract_audio_url",
    "is_private_group",
    "is_deleted_group",
    "is_banned_group",
    "calculate_group_activity_score",
    # Метаданные
    "__version__",
]
