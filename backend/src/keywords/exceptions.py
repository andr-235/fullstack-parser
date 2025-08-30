"""
Исключения модуля Keywords

Содержит специфические исключения для модуля управления ключевыми словами
"""

from ..exceptions import APIException


class KeywordNotFoundError(APIException):
    """Ключевое слово не найдено"""

    def __init__(self, keyword_id: int):
        super().__init__(
            status_code=404,
            detail=f"Ключевое слово с ID {keyword_id} не найдено",
            error_code="KEYWORD_NOT_FOUND",
            extra_data={"keyword_id": keyword_id},
        )


class KeywordAlreadyExistsError(APIException):
    """Ключевое слово уже существует"""

    def __init__(self, word: str):
        super().__init__(
            status_code=409,
            detail=f"Ключевое слово '{word}' уже существует",
            error_code="KEYWORD_ALREADY_EXISTS",
            extra_data={"word": word},
        )


class KeywordValidationError(APIException):
    """Ошибка валидации ключевого слова"""

    def __init__(self, message: str, field: str = None, value: str = None):
        detail = f"Ошибка валидации ключевого слова: {message}"
        extra_data = {"message": message}
        if field:
            extra_data["field"] = field
        if value:
            extra_data["value"] = value

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="KEYWORD_VALIDATION_ERROR",
            extra_data=extra_data,
        )


class KeywordTooLongError(APIException):
    """Ключевое слово слишком длинное"""

    def __init__(self, word: str, max_length: int):
        super().__init__(
            status_code=413,
            detail=f"Ключевое слово слишком длинное: {len(word)} символов (макс {max_length})",
            error_code="KEYWORD_TOO_LONG",
            extra_data={
                "word": word,
                "word_length": len(word),
                "max_length": max_length,
            },
        )


class DescriptionTooLongError(APIException):
    """Описание слишком длинное"""

    def __init__(self, description_length: int, max_length: int):
        super().__init__(
            status_code=413,
            detail=f"Описание слишком длинное: {description_length} символов (макс {max_length})",
            error_code="DESCRIPTION_TOO_LONG",
            extra_data={
                "description_length": description_length,
                "max_length": max_length,
            },
        )


class CategoryTooLongError(APIException):
    """Название категории слишком длинное"""

    def __init__(self, category: str, max_length: int):
        super().__init__(
            status_code=413,
            detail=f"Название категории слишком длинное: {len(category)} символов (макс {max_length})",
            error_code="CATEGORY_TOO_LONG",
            extra_data={
                "category": category,
                "category_length": len(category),
                "max_length": max_length,
            },
        )


class InvalidPriorityError(APIException):
    """Неверный приоритет"""

    def __init__(self, priority: int, min_priority: int, max_priority: int):
        super().__init__(
            status_code=422,
            detail=f"Неверный приоритет: {priority} (должен быть от {min_priority} до {max_priority})",
            error_code="INVALID_PRIORITY",
            extra_data={
                "priority": priority,
                "min_priority": min_priority,
                "max_priority": max_priority,
            },
        )


class BulkOperationError(APIException):
    """Ошибка массовой операции"""

    def __init__(
        self, action: str, errors: list, successful: int, failed: int
    ):
        detail = f"Ошибка массовой операции '{action}': {failed} неудачных из {successful + failed}"
        extra_data = {
            "action": action,
            "successful": successful,
            "failed": failed,
            "errors": errors[:10],  # Ограничиваем количество ошибок в ответе
        }

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="BULK_OPERATION_ERROR",
            extra_data=extra_data,
        )


class BulkSizeExceededError(APIException):
    """Превышен размер пакета"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            status_code=413,
            detail=f"Превышен размер пакета: {size} элементов (макс {max_size})",
            error_code="BULK_SIZE_EXCEEDED",
            extra_data={"size": size, "max_size": max_size},
        )


class CannotDeleteActiveKeywordError(APIException):
    """Нельзя удалять активное ключевое слово"""

    def __init__(self, keyword_id: int, word: str):
        super().__init__(
            status_code=422,
            detail=f"Нельзя удалять активное ключевое слово '{word}' (ID: {keyword_id})",
            error_code="CANNOT_DELETE_ACTIVE_KEYWORD",
            extra_data={"keyword_id": keyword_id, "word": word},
        )


class CannotActivateArchivedKeywordError(APIException):
    """Нельзя активировать архивированное ключевое слово"""

    def __init__(self, keyword_id: int, word: str):
        super().__init__(
            status_code=422,
            detail=f"Нельзя активировать архивированное ключевое слово '{word}' (ID: {keyword_id})",
            error_code="CANNOT_ACTIVATE_ARCHIVED_KEYWORD",
            extra_data={"keyword_id": keyword_id, "word": word},
        )


class InvalidBulkActionError(APIException):
    """Недопустимое действие массовой операции"""

    def __init__(self, action: str, allowed_actions: list):
        super().__init__(
            status_code=422,
            detail=f"Недопустимое действие массовой операции: {action}",
            error_code="INVALID_BULK_ACTION",
            extra_data={"action": action, "allowed_actions": allowed_actions},
        )


class InvalidExportFormatError(APIException):
    """Недопустимый формат экспорта"""

    def __init__(self, format_type: str, allowed_formats: list):
        super().__init__(
            status_code=422,
            detail=f"Недопустимый формат экспорта: {format_type}",
            error_code="INVALID_EXPORT_FORMAT",
            extra_data={
                "format": format_type,
                "allowed_formats": allowed_formats,
            },
        )


class ExportFailedError(APIException):
    """Ошибка экспорта"""

    def __init__(self, format_type: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка экспорта в формате {format_type}: {error}",
            error_code="EXPORT_FAILED",
            extra_data={"format": format_type, "error": error},
        )


class ImportFailedError(APIException):
    """Ошибка импорта"""

    def __init__(self, error: str, successful: int = 0, failed: int = 0):
        detail = f"Ошибка импорта: {error}"
        extra_data = {"error": error}
        if successful or failed:
            detail += f" (успешно: {successful}, неудачно: {failed})"
            extra_data["successful"] = successful
            extra_data["failed"] = failed

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="IMPORT_FAILED",
            extra_data=extra_data,
        )


class InvalidImportDataError(APIException):
    """Неверный формат данных импорта"""

    def __init__(self, error: str, data_sample: str = None):
        detail = f"Неверный формат данных импорта: {error}"
        extra_data = {"error": error}
        if data_sample:
            extra_data["data_sample"] = (
                data_sample[:200] + "..."
                if len(data_sample) > 200
                else data_sample
            )

        super().__init__(
            status_code=422,
            detail=detail,
            error_code="INVALID_IMPORT_DATA",
            extra_data=extra_data,
        )


class SearchTimeoutError(APIException):
    """Превышено время поиска"""

    def __init__(self, query: str, timeout: float):
        super().__init__(
            status_code=408,
            detail=f"Превышено время поиска для запроса '{query}': {timeout} секунд",
            error_code="SEARCH_TIMEOUT",
            extra_data={"query": query, "timeout": timeout},
        )


class TooManySearchResultsError(APIException):
    """Слишком много результатов поиска"""

    def __init__(self, query: str, result_count: int, max_results: int):
        super().__init__(
            status_code=413,
            detail=f"Слишком много результатов поиска для запроса '{query}': {result_count} (макс {max_results})",
            error_code="TOO_MANY_SEARCH_RESULTS",
            extra_data={
                "query": query,
                "result_count": result_count,
                "max_results": max_results,
            },
        )


class KeywordsCacheError(APIException):
    """Ошибка кеширования ключевых слов"""

    def __init__(self, operation: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка кеширования ключевых слов: {error}",
            error_code="KEYWORDS_CACHE_ERROR",
            extra_data={"operation": operation, "error": error},
        )


class KeywordsDataValidationError(APIException):
    """Ошибка валидации данных ключевых слов"""

    def __init__(self, data_type: str, errors: list):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации данных типа '{data_type}'",
            error_code="KEYWORDS_DATA_VALIDATION_ERROR",
            extra_data={"data_type": data_type, "validation_errors": errors},
        )


class KeywordsResourceLimitError(APIException):
    """Превышен лимит ресурсов ключевых слов"""

    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            status_code=507,
            detail=f"Превышен лимит ресурса '{resource}': {current}/{limit}",
            error_code="KEYWORDS_RESOURCE_LIMIT",
            extra_data={
                "resource": resource,
                "limit": limit,
                "current": current,
            },
        )


class KeywordsExternalServiceError(APIException):
    """Ошибка внешнего сервиса ключевых слов"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            status_code=502,
            detail=f"Ошибка внешнего сервиса '{service_name}': {error_message}",
            error_code="KEYWORDS_EXTERNAL_SERVICE_ERROR",
            extra_data={
                "service": service_name,
                "error_message": error_message,
            },
        )


class KeywordsConcurrencyError(APIException):
    """Ошибка параллелизма ключевых слов"""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=409,
            detail=f"Ошибка параллелизма ключевых слов: {reason}",
            error_code="KEYWORDS_CONCURRENCY_ERROR",
            extra_data={"operation": operation, "reason": reason},
        )


class KeywordsPerformanceError(APIException):
    """Ошибка производительности ключевых слов"""

    def __init__(self, operation: str, duration: float, threshold: float):
        super().__init__(
            status_code=504,
            detail=f"Превышен порог производительности: {duration:.2f}s > {threshold:.2f}s",
            error_code="KEYWORDS_PERFORMANCE_ERROR",
            extra_data={
                "operation": operation,
                "duration": duration,
                "threshold": threshold,
            },
        )


class KeywordsConfigurationError(APIException):
    """Ошибка конфигурации ключевых слов"""

    def __init__(self, config_key: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка конфигурации ключевых слов: {error}",
            error_code="KEYWORDS_CONFIGURATION_ERROR",
            extra_data={"config_key": config_key, "error": error},
        )


class KeywordsOperationNotAllowedError(APIException):
    """Операция не разрешена для ключевых слов"""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=403,
            detail=f"Операция '{operation}' не разрешена: {reason}",
            error_code="KEYWORDS_OPERATION_NOT_ALLOWED",
            extra_data={"operation": operation, "reason": reason},
        )


# Экспорт всех исключений
__all__ = [
    "KeywordNotFoundError",
    "KeywordAlreadyExistsError",
    "KeywordValidationError",
    "KeywordTooLongError",
    "DescriptionTooLongError",
    "CategoryTooLongError",
    "InvalidPriorityError",
    "BulkOperationError",
    "BulkSizeExceededError",
    "CannotDeleteActiveKeywordError",
    "CannotActivateArchivedKeywordError",
    "InvalidBulkActionError",
    "InvalidExportFormatError",
    "ExportFailedError",
    "ImportFailedError",
    "InvalidImportDataError",
    "SearchTimeoutError",
    "TooManySearchResultsError",
    "KeywordsCacheError",
    "KeywordsDataValidationError",
    "KeywordsResourceLimitError",
    "KeywordsExternalServiceError",
    "KeywordsConcurrencyError",
    "KeywordsPerformanceError",
    "KeywordsConfigurationError",
    "KeywordsOperationNotAllowedError",
]
