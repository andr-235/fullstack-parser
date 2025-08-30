"""
Инфраструктурный сервис хеширования

Предоставляет различные алгоритмы хеширования и функции для создания хешей
"""

import hashlib
import hmac
from typing import Any, Optional
from functools import lru_cache

from .security import security_service


class HashingService:
    """
    Инфраструктурный сервис для хеширования данных

    Предоставляет различные алгоритмы хеширования
    и функции для создания хешей
    """

    def __init__(self):
        self.secret_key = security_service.secret_key

    def hash_string(self, text: str, algorithm: str = "sha256") -> str:
        """
        Захешировать строку

        Args:
            text: Строка для хеширования
            algorithm: Алгоритм хеширования (sha256, sha512, md5)

        Returns:
            Хеш строки в hex формате
        """
        if algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(text.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def hash_file(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Посчитать хеш файла

        Args:
            file_path: Путь к файлу
            algorithm: Алгоритм хеширования

        Returns:
            Хеш файла
        """
        hash_obj = getattr(hashlib, algorithm)()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def create_hmac(self, message: str, key: Optional[str] = None) -> str:
        """
        Создать HMAC подпись

        Args:
            message: Сообщение для подписи
            key: Ключ (если не указан, используется секретный ключ)

        Returns:
            HMAC подпись в hex формате
        """
        key_to_use = key or self.secret_key
        return hmac.new(
            key_to_use.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

    def verify_hmac(
        self, message: str, signature: str, key: Optional[str] = None
    ) -> bool:
        """
        Проверить HMAC подпись

        Args:
            message: Сообщение
            signature: Подпись для проверки
            key: Ключ (если не указан, используется секретный ключ)

        Returns:
            True если подпись верна
        """
        expected_signature = self.create_hmac(message, key)
        return hmac.compare_digest(expected_signature, signature)

    def hash_password_for_storage(self, password: str) -> str:
        """
        Захешировать пароль для хранения (делегируется SecurityService)

        Args:
            password: Пароль

        Returns:
            Захешированный пароль
        """
        return security_service.hash_password(password)

    def create_checksum(self, data: Any) -> str:
        """
        Создать контрольную сумму для данных

        Args:
            data: Данные для хеширования

        Returns:
            Контрольная сумма
        """
        if isinstance(data, (dict, list)):
            import json

            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = str(data)

        return self.hash_string(data_str)

    def get_supported_algorithms(self) -> list[str]:
        """
        Получить список поддерживаемых алгоритмов

        Returns:
            Список алгоритмов
        """
        return ["sha256", "sha512", "md5"]

    def hash_with_salt(
        self, text: str, salt: str, algorithm: str = "sha256"
    ) -> str:
        """
        Захешировать строку с солью

        Args:
            text: Строка для хеширования
            salt: Соль
            algorithm: Алгоритм хеширования

        Returns:
            Хеш с солью
        """
        salted_text = f"{salt}{text}"
        return self.hash_string(salted_text, algorithm)

    def generate_salt(self, length: int = 16) -> str:
        """
        Сгенерировать соль

        Args:
            length: Длина соли

        Returns:
            Случайная соль
        """
        import secrets

        return secrets.token_hex(length)

    def hash_multiple(
        self, texts: list[str], algorithm: str = "sha256"
    ) -> list[str]:
        """
        Захешировать несколько строк

        Args:
            texts: Список строк для хеширования
            algorithm: Алгоритм хеширования

        Returns:
            Список хешей
        """
        return [self.hash_string(text, algorithm) for text in texts]

    def compare_hashes(self, hash1: str, hash2: str) -> bool:
        """
        Сравнить два хеша безопасным способом

        Args:
            hash1: Первый хеш
            hash2: Второй хеш

        Returns:
            True если хеши совпадают
        """
        return hmac.compare_digest(hash1, hash2)

    def get_hash_info(self, hash_value: str) -> dict[str, Any]:
        """
        Получить информацию о хеше

        Args:
            hash_value: Значение хеша

        Returns:
            Информация о хеше
        """
        length = len(hash_value)

        # Определяем алгоритм по длине
        if length == 32:
            algorithm = "md5"
        elif length == 64:
            algorithm = "sha256"
        elif length == 128:
            algorithm = "sha512"
        else:
            algorithm = "unknown"

        return {
            "length": length,
            "algorithm": algorithm,
            "hex_format": all(
                c in "0123456789abcdef" for c in hash_value.lower()
            ),
        }


# Глобальный экземпляр сервиса хеширования
@lru_cache(maxsize=1)
def get_hashing_service() -> HashingService:
    """Получить экземпляр сервиса хеширования (кешируется)"""
    return HashingService()


# Глобальный объект для обратной совместимости
hashing_service = get_hashing_service()


# Экспорт
__all__ = [
    "HashingService",
    "get_hashing_service",
    "hashing_service",
]
