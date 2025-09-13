"""
Исключения модуля VK API
"""

from typing import Optional


class VKAPIError(Exception):
    """Базовая ошибка VK API"""

    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
