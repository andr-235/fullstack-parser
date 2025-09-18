"""
Shared компоненты модуля Keywords

Содержит общие компоненты, константы и исключения
"""

from .constants import (
    DEFAULT_KEYWORD_PRIORITY,
    MAX_KEYWORD_LENGTH,
    MIN_KEYWORD_LENGTH,
    DEFAULT_KEYWORDS_LIMIT,
    MAX_KEYWORDS_LIMIT,
)
from .exceptions import (
    KeywordNotFoundError,
    KeywordValidationError,
    KeywordAlreadyExistsError,
    KeywordOperationError,
)

__all__ = [
    "DEFAULT_KEYWORD_PRIORITY",
    "MAX_KEYWORD_LENGTH",
    "MIN_KEYWORD_LENGTH",
    "DEFAULT_KEYWORDS_LIMIT",
    "MAX_KEYWORDS_LIMIT",
    "KeywordNotFoundError",
    "KeywordValidationError",
    "KeywordAlreadyExistsError",
    "KeywordOperationError",
]