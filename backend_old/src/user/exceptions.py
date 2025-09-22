"""
Исключения модуля пользователей
"""


class UserError(Exception):
    """Базовое исключение для пользователей"""
    pass


class UserNotFoundError(UserError):
    """Пользователь не найден"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Пользователь с ID {user_id} не найден")


class UserAlreadyExistsError(UserError):
    """Пользователь уже существует"""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Пользователь с email {email} уже существует")


class UserInactiveError(UserError):
    """Пользователь неактивен"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Пользователь {user_id} неактивен")


class UserLockedError(UserError):
    """Пользователь заблокирован"""

    def __init__(self, user_id: int, unlock_time: str = None):
        self.user_id = user_id
        self.unlock_time = unlock_time
        message = f"Пользователь {user_id} заблокирован"
        if unlock_time:
            message += f" до {unlock_time}"
        super().__init__(message)
