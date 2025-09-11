"""
Интерфейс сервиса паролей для Application Layer

Определяет контракт для работы с паролями в слое приложения
"""

from abc import ABC, abstractmethod
from auth.domain.value_objects.password import Password


class PasswordServiceInterface(ABC):
    """
    Интерфейс сервиса паролей для Application Layer
    
    Определяет методы для работы с паролями в слое приложения
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
