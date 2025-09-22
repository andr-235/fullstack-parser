"""
Кастомные исключения для модуля авторов
"""

from typing import Dict, Optional


# Константы для кодов ошибок
AUTHOR_NOT_FOUND = "AUTHOR_NOT_FOUND"
AUTHOR_ALREADY_EXISTS = "AUTHOR_ALREADY_EXISTS"
AUTHOR_VALIDATION_ERROR = "AUTHOR_VALIDATION_ERROR"


class AuthorError(Exception):
  """
  Базовое исключение для модуля авторов.

  Attributes:
    message (str): Сообщение об ошибке.
    details (dict): Дополнительные детали ошибки.
    code (str): Машиночитаемый код ошибки.
    message_key (str): Ключ для локализации сообщения.
  """

  def __init__(
    self,
    message: str,
    details: Optional[Dict] = None,
    code: str = "AUTHOR_ERROR",
    message_key: Optional[str] = None
  ):
    super().__init__(message)
    self.message = message
    self.details = details or {}
    self.code = code
    self.message_key = message_key or self.__class__.__name__

  def to_dict(self) -> Dict:
    """
    Сериализует исключение в словарь для JSON API.

    Returns:
      Dict: Словарь с кодом, сообщением и деталями.
    """
    return {
      "code": self.code,
      "message": self.message,
      "details": self.details,
      "message_key": self.message_key
    }


class AuthorNotFoundError(AuthorError):
  """
  Исключение, когда автор не найден.

  Args:
    author_id (Optional[int]): ID автора.
    vk_id (Optional[int]): VK ID автора.
  """

  def __init__(self, author_id: Optional[int] = None, vk_id: Optional[int] = None):
    if author_id:
      message = f"Автор с ID {author_id} не найден"
      details = {"author_id": author_id}
      message_key = "AUTHOR_NOT_FOUND_BY_ID"
    elif vk_id:
      message = f"Автор с VK ID {vk_id} не найден"
      details = {"vk_id": vk_id}
      message_key = "AUTHOR_NOT_FOUND_BY_VK_ID"
    else:
      message = "Автор не найден"
      details = {}
      message_key = "AUTHOR_NOT_FOUND"

    super().__init__(message, details, AUTHOR_NOT_FOUND, message_key)


class AuthorAlreadyExistsError(AuthorError):
  """
  Исключение, когда автор уже существует.

  Args:
    vk_id (int): VK ID автора.
  """

  def __init__(self, vk_id: int):
    message = f"Автор с VK ID {vk_id} уже существует"
    details = {"vk_id": vk_id}
    message_key = "AUTHOR_ALREADY_EXISTS"
    super().__init__(message, details, AUTHOR_ALREADY_EXISTS, message_key)


class AuthorValidationError(AuthorError):
  """
  Исключение для ошибок валидации.

  Args:
    field (str): Поле с ошибкой.
    value (str): Значение поля.
    reason (str): Причина ошибки.
  """

  def __init__(self, field: str, value: str, reason: str):
    message = f"Ошибка валидации поля '{field}': {reason}"
    details = {"field": field, "value": value, "reason": reason}
    message_key = "AUTHOR_VALIDATION_ERROR"
    super().__init__(message, details, AUTHOR_VALIDATION_ERROR, message_key)