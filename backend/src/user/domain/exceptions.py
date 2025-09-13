"""
Domain исключения модуля User

Содержит исключения специфичные для пользователей
"""


class DomainException(Exception):
    """Базовое исключение domain слоя"""
    pass


class UserNotFoundError(DomainException):
    """Пользователь не найден"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Пользователь с ID {user_id} не найден")


class UserAlreadyExistsError(DomainException):
    """Пользователь уже существует"""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Пользователь с email {email} уже существует")


class UserInactiveError(DomainException):
    """Пользователь не активен"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Пользователь {user_id} не активен")


class UserLockedError(DomainException):
    """Пользователь заблокирован"""
    
    def __init__(self, user_id: int, unlock_time: str = None):
        self.user_id = user_id
        self.unlock_time = unlock_time
        message = f"Пользователь {user_id} заблокирован"
        if unlock_time:
            message += f" до {unlock_time}"
        super().__init__(message)
