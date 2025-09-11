"""
Адаптер для SecurityService

Адаптирует инфраструктурный SecurityService для доменного слоя
"""

from auth.domain.services.password_service import PasswordService
from auth.domain.services.token_service import TokenService
from auth.domain.value_objects.password import Password
from auth.domain.entities.user import User
from src.infrastructure import security_service
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class SecurityServicePasswordAdapter(PasswordService):
    """
    Адаптер SecurityService для работы с паролями
    
    Адаптирует инфраструктурный SecurityService для доменного слоя
    """
    
    def hash_password(self, password: Password) -> Password:
        """
        Захешировать пароль
        
        Args:
            password: Пароль для хеширования
            
        Returns:
            Password: Захешированный пароль
        """
        if password._plain_value:
            hashed_value = security_service.hash_password(password._plain_value)
            return Password.create_from_hash(hashed_value)
        else:
            return password
    
    def verify_password(self, plain_password: str, hashed_password: Password) -> bool:
        """
        Проверить пароль
        
        Args:
            plain_password: Пароль в открытом виде
            hashed_password: Захешированный пароль
            
        Returns:
            bool: True если пароль верный
        """
        return security_service.verify_password(plain_password, hashed_password.hashed_value)


class SecurityServiceTokenAdapter(TokenService):
    """
    Адаптер SecurityService для работы с токенами
    
    Адаптирует инфраструктурный SecurityService для доменного слоя
    """
    
    def create_access_token(self, user: User) -> str:
        """
        Создать access токен
        
        Args:
            user: Пользователь
            
        Returns:
            str: Access токен
        """
        token_data = {
            "sub": str(user.id.value),
            "email": user.email.value,
            "type": "user",
        }
        return security_service.create_access_token(token_data)
    
    def create_refresh_token(self, user: User) -> str:
        """
        Создать refresh токен
        
        Args:
            user: Пользователь
            
        Returns:
            str: Refresh токен
        """
        token_data = {
            "sub": str(user.id.value),
            "email": user.email.value,
            "type": "user",
        }
        return security_service.create_refresh_token(token_data)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Декодировать токен
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[Dict[str, Any]]: Декодированные данные или None
        """
        return security_service.decode_token(token)
    
    def verify_token(self, token: str) -> bool:
        """
        Проверить токен
        
        Args:
            token: JWT токен
            
        Returns:
            bool: True если токен валиден
        """
        payload = self.decode_token(token)
        return payload is not None
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Получить время истечения токена
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[datetime]: Время истечения или None
        """
        return security_service.get_token_expiration(token)
