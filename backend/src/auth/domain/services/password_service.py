"""
Доменный сервис для работы с паролями

Инкапсулирует бизнес-логику работы с паролями
"""

from abc import ABC, abstractmethod
from auth.domain.value_objects.password import Password


class PasswordService(ABC):
    """
    Абстрактный сервис для работы с паролями
    
    Определяет интерфейс для хеширования и проверки паролей
    """
    
    @abstractmethod
    def hash_password(self, password: Password) -> Password:
        """
        Захешировать пароль
        
        Args:
            password: Пароль для хеширования
            
        Returns:
            Password: Захешированный пароль
        """
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: Password) -> bool:
        """
        Проверить пароль
        
        Args:
            plain_password: Пароль в открытом виде
            hashed_password: Захешированный пароль
            
        Returns:
            bool: True если пароль верный
        """
        pass
