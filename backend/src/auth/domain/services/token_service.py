"""
Доменный сервис для работы с токенами

Инкапсулирует бизнес-логику работы с JWT токенами
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from auth.domain.entities.user import User


class TokenService(ABC):
    """
    Абстрактный сервис для работы с токенами
    
    Определяет интерфейс для создания и проверки JWT токенов
    """
    
    @abstractmethod
    def create_access_token(self, user: User) -> str:
        """
        Создать access токен
        
        Args:
            user: Пользователь
            
        Returns:
            str: Access токен
        """
        pass
    
    @abstractmethod
    def create_refresh_token(self, user: User) -> str:
        """
        Создать refresh токен
        
        Args:
            user: Пользователь
            
        Returns:
            str: Refresh токен
        """
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Декодировать токен
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[Dict[str, Any]]: Декодированные данные или None
        """
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> bool:
        """
        Проверить токен
        
        Args:
            token: JWT токен
            
        Returns:
            bool: True если токен валиден
        """
        pass
    
    @abstractmethod
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Получить время истечения токена
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[datetime]: Время истечения или None
        """
        pass
