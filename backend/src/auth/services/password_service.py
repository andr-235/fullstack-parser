"""
Сервис паролей
"""

import bcrypt
from shared.infrastructure.logging import get_logger


class PasswordService:
    """Сервис паролей с использованием bcrypt"""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
        self.logger = get_logger()
    
    async def hash_password(self, password: str) -> str:
        """Захешировать пароль"""
        try:
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error hashing password: {e}")
            raise
    
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f"Error verifying password: {e}")
            return False
