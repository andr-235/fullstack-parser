"""
Исключения модуля Morphological

Содержит специфические исключения для модуля морфологического анализа
"""

from ..exceptions import APIException


class MorphologicalAnalysisError(APIException):
    """Ошибка морфологического анализа"""

    def __init__(self, message: str, text: str = None):
        detail = f"Ошибка морфологического анализа: {message}"
        extra_data = {"message": message}
        if text:
            extra_data["text_preview"] = (
                text[:100] + "..." if len(text) > 100 else text
            )

        super().__init__(
            status_code=500,
            detail=detail,
            error_code="MORPHOLOGICAL_ANALYSIS_ERROR",
            extra_data=extra_data,
        )


class TextTooLongError(APIException):
    """Текст слишком длинный для анализа"""

    def __init__(self, text_length: int, max_length: int):
        super().__init__(
            status_code=413,
            detail=f"Текст слишком длинный для анализа: {text_length} символов (макс {max_length})",
            error_code="TEXT_TOO_LONG",
            extra_data={"text_length": text_length, "max_length": max_length},
        )


class WordTooLongError(APIException):
    """Слово слишком длинное для анализа"""

    def __init__(self, word: str, word_length: int, max_length: int):
        super().__init__(
            status_code=413,
            detail=f"Слово слишком длинное для анализа: {word_length} символов (макс {max_length})",
            error_code="WORD_TOO_LONG",
            extra_data={
                "word": word,
                "word_length": word_length,
                "max_length": max_length,
            },
        )


class AnalyzerNotAvailableError(APIException):
    """Морфологический анализатор недоступен"""

    def __init__(self, analyzer_type: str = None):
        detail = "Морфологический анализатор недоступен"
        extra_data = {}
        if analyzer_type:
            detail += f": {analyzer_type}"
            extra_data["analyzer_type"] = analyzer_type

        super().__init__(
            status_code=503,
            detail=detail,
            error_code="ANALYZER_NOT_AVAILABLE",
            extra_data=extra_data,
        )


class UnsupportedLanguageError(APIException):
    """Неподдерживаемый язык"""

    def __init__(self, language: str, supported_languages: list = None):
        detail = f"Неподдерживаемый язык: {language}"
        extra_data = {"language": language}
        if supported_languages:
            detail += f". Поддерживаемые: {', '.join(supported_languages)}"
            extra_data["supported_languages"] = supported_languages

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="UNSUPPORTED_LANGUAGE",
            extra_data=extra_data,
        )


class InvalidPartOfSpeechError(APIException):
    """Неверная часть речи"""

    def __init__(self, pos: str, allowed_pos: list = None):
        detail = f"Неверная часть речи: {pos}"
        extra_data = {"pos": pos}
        if allowed_pos:
            detail += f". Допустимые: {', '.join(allowed_pos)}"
            extra_data["allowed_pos"] = allowed_pos

        super().__init__(
            status_code=400,
            detail=detail,
            error_code="INVALID_PART_OF_SPEECH",
            extra_data=extra_data,
        )


class BatchTooLargeError(APIException):
    """Слишком большой пакет для анализа"""

    def __init__(self, batch_size: int, max_batch_size: int):
        super().__init__(
            status_code=413,
            detail=f"Слишком большой пакет для анализа: {batch_size} текстов (макс {max_batch_size})",
            error_code="BATCH_TOO_LARGE",
            extra_data={
                "batch_size": batch_size,
                "max_batch_size": max_batch_size,
            },
        )


class AnalysisTimeoutError(APIException):
    """Превышено время анализа"""

    def __init__(self, timeout: float, operation: str = "анализа"):
        super().__init__(
            status_code=408,
            detail=f"Превышено время {operation}: {timeout} секунд",
            error_code="ANALYSIS_TIMEOUT",
            extra_data={"timeout": timeout, "operation": operation},
        )


class MorphologicalConfigError(APIException):
    """Ошибка конфигурации морфологического анализа"""

    def __init__(self, config_key: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка конфигурации морфологического анализа: {error}",
            error_code="MORPHOLOGICAL_CONFIG_ERROR",
            extra_data={"config_key": config_key, "error": error},
        )


class PatternGenerationError(APIException):
    """Ошибка генерации паттернов поиска"""

    def __init__(self, word: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка генерации паттернов поиска для слова '{word}': {error}",
            error_code="PATTERN_GENERATION_ERROR",
            extra_data={"word": word, "error": error},
        )


class KeywordExtractionError(APIException):
    """Ошибка извлечения ключевых слов"""

    def __init__(self, text_length: int, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка извлечения ключевых слов: {error}",
            error_code="KEYWORD_EXTRACTION_ERROR",
            extra_data={"text_length": text_length, "error": error},
        )


class LanguageDetectionError(APIException):
    """Ошибка определения языка"""

    def __init__(self, text_sample: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка определения языка: {error}",
            error_code="LANGUAGE_DETECTION_ERROR",
            extra_data={
                "text_sample": (
                    text_sample[:50] + "..."
                    if len(text_sample) > 50
                    else text_sample
                ),
                "error": error,
            },
        )


class MorphologicalCacheError(APIException):
    """Ошибка кеширования морфологического анализа"""

    def __init__(self, operation: str, error: str):
        super().__init__(
            status_code=500,
            detail=f"Ошибка кеширования морфологического анализа: {error}",
            error_code="MORPHOLOGICAL_CACHE_ERROR",
            extra_data={"operation": operation, "error": error},
        )


class MorphologicalDataValidationError(APIException):
    """Ошибка валидации данных морфологического анализа"""

    def __init__(self, data_type: str, errors: list):
        super().__init__(
            status_code=422,
            detail=f"Ошибка валидации данных типа '{data_type}'",
            error_code="MORPHOLOGICAL_DATA_VALIDATION_ERROR",
            extra_data={"data_type": data_type, "validation_errors": errors},
        )


class MorphologicalResourceLimitError(APIException):
    """Превышен лимит ресурсов морфологического анализа"""

    def __init__(self, resource: str, limit: int, current: int):
        super().__init__(
            status_code=507,
            detail=f"Превышен лимит ресурса '{resource}': {current}/{limit}",
            error_code="MORPHOLOGICAL_RESOURCE_LIMIT",
            extra_data={
                "resource": resource,
                "limit": limit,
                "current": current,
            },
        )


class MorphologicalExternalServiceError(APIException):
    """Ошибка внешнего сервиса морфологического анализа"""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            status_code=502,
            detail=f"Ошибка внешнего сервиса '{service_name}': {error_message}",
            error_code="MORPHOLOGICAL_EXTERNAL_SERVICE_ERROR",
            extra_data={
                "service": service_name,
                "error_message": error_message,
            },
        )


class MorphologicalConcurrencyError(APIException):
    """Ошибка параллелизма морфологического анализа"""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=409,
            detail=f"Ошибка параллелизма морфологического анализа: {reason}",
            error_code="MORPHOLOGICAL_CONCURRENCY_ERROR",
            extra_data={"operation": operation, "reason": reason},
        )


class MorphologicalPerformanceError(APIException):
    """Ошибка производительности морфологического анализа"""

    def __init__(self, operation: str, duration: float, threshold: float):
        super().__init__(
            status_code=504,
            detail=f"Превышен порог производительности: {duration:.2f}s > {threshold:.2f}s",
            error_code="MORPHOLOGICAL_PERFORMANCE_ERROR",
            extra_data={
                "operation": operation,
                "duration": duration,
                "threshold": threshold,
            },
        )


# Экспорт всех исключений
__all__ = [
    "MorphologicalAnalysisError",
    "TextTooLongError",
    "WordTooLongError",
    "AnalyzerNotAvailableError",
    "UnsupportedLanguageError",
    "InvalidPartOfSpeechError",
    "BatchTooLargeError",
    "AnalysisTimeoutError",
    "MorphologicalConfigError",
    "PatternGenerationError",
    "KeywordExtractionError",
    "LanguageDetectionError",
    "MorphologicalCacheError",
    "MorphologicalDataValidationError",
    "MorphologicalResourceLimitError",
    "MorphologicalExternalServiceError",
    "MorphologicalConcurrencyError",
    "MorphologicalPerformanceError",
]
