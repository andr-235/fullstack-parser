"""
Кастомные исключения для модуля Keywords
"""


class KeywordsException(Exception):
    """Базовое исключение для модуля Keywords"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class KeywordNotFoundError(KeywordsException):
    """Исключение, когда ключевое слово не найдено"""

    def __init__(self, keyword_id: int = None, word: str = None):
        if keyword_id:
            message = f"Ключевое слово с ID {keyword_id} не найдено"
        elif word:
            message = f"Ключевое слово '{word}' не найдено"
        else:
            message = "Ключевое слово не найдено"
        super().__init__(message, status_code=404)


class KeywordAlreadyExistsError(KeywordsException):
    """Исключение, когда ключевое слово уже существует"""

    def __init__(self, word: str):
        message = f"Ключевое слово '{word}' уже существует"
        super().__init__(message, status_code=409)


class KeywordValidationError(KeywordsException):
    """Исключение при валидации ключевого слова"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class KeywordTooShortError(KeywordValidationError):
    """Исключение, когда ключевое слово слишком короткое"""

    def __init__(self, min_length: int):
        message = f"Ключевое слово должно содержать минимум {min_length} символа"
        super().__init__(message)


class KeywordTooLongError(KeywordValidationError):
    """Исключение, когда ключевое слово слишком длинное"""

    def __init__(self, max_length: int):
        message = f"Ключевое слово не может превышать {max_length} символов"
        super().__init__(message)


class InvalidPriorityError(KeywordValidationError):
    """Исключение при некорректном приоритете"""

    def __init__(self, min_val: int, max_val: int):
        message = f"Приоритет должен быть в диапазоне от {min_val} до {max_val}"
        super().__init__(message)


class InvalidCategoryLengthError(KeywordValidationError):
    """Исключение при некорректной длине категории"""

    def __init__(self, max_length: int):
        message = f"Название категории не может превышать {max_length} символов"
        super().__init__(message)


class InvalidDescriptionLengthError(KeywordValidationError):
    """Исключение при некорректной длине описания"""

    def __init__(self, max_length: int):
        message = f"Описание не может превышать {max_length} символов"
        super().__init__(message)


class CannotActivateArchivedKeywordError(KeywordsException):
    """Исключение при попытке активировать архивированное ключевое слово"""

    def __init__(self):
        message = "Нельзя активировать архивированное ключевое слово"
        super().__init__(message, status_code=400)


class DatabaseError(KeywordsException):
    """Исключение при ошибках базы данных"""

    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message, status_code=500)


class RepositoryError(KeywordsException):
    """Исключение при ошибках репозитория"""

    def __init__(self, message: str = "Ошибка репозитория"):
        super().__init__(message, status_code=500)