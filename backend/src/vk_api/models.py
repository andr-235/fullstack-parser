"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
Модели для модуля VK API

Определяет репозиторий для работы с VK API
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..database import get_db_session


class VKAPIRepository:
    """
    Репозиторий для работы с данными VK API

    Предоставляет интерфейс для кеширования результатов запросов к VK API
    """

    def __init__(self, db=None):
        self.db = db
        # In-memory кеш для простоты (в продакшене использовать Redis)
        self._cache = {}
        self._cache_expiry = {}

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def save_cached_result(
        self, cache_key: str, data: Dict[str, Any], ttl_seconds: int
    ) -> None:
        """
        Сохранить результат в кеш

        Args:
            cache_key: Ключ кеша
            data: Данные для сохранения
            ttl_seconds: Время жизни в секундах
        """
        expiry_time = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        self._cache[cache_key] = data
        self._cache_expiry[cache_key] = expiry_time

        # Очищаем устаревший кеш
        await self._cleanup_expired_cache()

    async def get_cached_result(
        self, cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить результат из кеша

        Args:
            cache_key: Ключ кеша

        Returns:
            Optional[Dict[str, Any]]: Данные из кеша или None
        """
        # Проверяем, есть ли данные в кеше
        if cache_key not in self._cache:
            return None

        # Проверяем срок действия
        if cache_key in self._cache_expiry:
            if datetime.utcnow() > self._cache_expiry[cache_key]:
                # Кеш устарел, удаляем
                await self.delete_cached_result(cache_key)
                return None

        return self._cache[cache_key]

    async def delete_cached_result(self, cache_key: str) -> bool:
        """
        Удалить результат из кеша

        Args:
            cache_key: Ключ кеша

        Returns:
            bool: Успешно ли удалено
        """
        deleted = False

        if cache_key in self._cache:
            del self._cache[cache_key]
            deleted = True

        if cache_key in self._cache_expiry:
            del self._cache_expiry[cache_key]

        return deleted

    async def clear_cache(self) -> int:
        """
        Очистить весь кеш

        Returns:
            int: Количество удаленных записей
        """
        count = len(self._cache)
        self._cache.clear()
        self._cache_expiry.clear()
        return count

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получить статистику кеша

        Returns:
            Dict[str, Any]: Статистика кеша
        """
        current_time = datetime.utcnow()

        total_entries = len(self._cache)
        expired_entries = sum(
            1
            for expiry in self._cache_expiry.values()
            if current_time > expiry
        )
        active_entries = total_entries - expired_entries

        # Распределение по типам
        group_entries = sum(
            1 for key in self._cache.keys() if key.startswith("group:")
        )
        post_entries = sum(
            1 for key in self._cache.keys() if key.startswith("post:")
        )
        user_entries = sum(
            1 for key in self._cache.keys() if key.startswith("user:")
        )
        search_entries = sum(
            1 for key in self._cache.keys() if key.startswith("search:")
        )

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "group_entries": group_entries,
            "post_entries": post_entries,
            "user_entries": user_entries,
            "search_entries": search_entries,
        }

    async def _cleanup_expired_cache(self) -> int:
        """
        Очистить устаревший кеш

        Returns:
            int: Количество удаленных записей
        """
        current_time = datetime.utcnow()
        expired_keys = []

        for key, expiry_time in self._cache_expiry.items():
            if current_time > expiry_time:
                expired_keys.append(key)

        # Удаляем устаревшие записи
        for key in expired_keys:
            if key in self._cache:
                del self._cache[key]
            del self._cache_expiry[key]

        return len(expired_keys)

    async def save_request_log(
        self,
        method: str,
        params: Dict[str, Any],
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Сохранить лог запроса

        Args:
            method: Метод VK API
            params: Параметры запроса
            response_time: Время ответа
            success: Успешность запроса
            error_message: Сообщение об ошибке
        """
        # В простой реализации просто сохраняем в память
        # В продакшене это должно сохраняться в БД
        log_entry = {
            "method": method,
            "params_count": len(params),
            "response_time": response_time,
            "success": success,
            "error_message": error_message,
            "timestamp": datetime.utcnow(),
        }

        # Сохраняем последние 1000 логов
        if not hasattr(self, "_request_logs"):
            self._request_logs = []

        self._request_logs.append(log_entry)
        if len(self._request_logs) > 1000:
            self._request_logs = self._request_logs[-1000:]

    async def get_request_logs(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получить логи запросов

        Args:
            limit: Количество записей
            offset: Смещение

        Returns:
            List[Dict[str, Any]]: Логи запросов
        """
        if not hasattr(self, "_request_logs"):
            return []

        logs = self._request_logs[::-1]  # Обратный порядок (новые сверху)
        return logs[offset : offset + limit]

    async def get_request_stats(self) -> Dict[str, Any]:
        """
        Получить статистику запросов

        Returns:
            Dict[str, Any]: Статистика запросов
        """
        if not hasattr(self, "_request_logs") or not self._request_logs:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0,
                "error_rate": 0,
            }

        logs = self._request_logs
        total_requests = len(logs)
        successful_requests = sum(1 for log in logs if log["success"])
        failed_requests = total_requests - successful_requests

        response_times = [
            log["response_time"] for log in logs if log["success"]
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        error_rate = (
            failed_requests / total_requests if total_requests > 0 else 0
        )

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_response_time": round(avg_response_time, 3),
            "error_rate": round(error_rate, 3),
        }

    async def save_error_log(
        self,
        method: str,
        error_code: int,
        error_message: str,
        params: Dict[str, Any],
    ) -> None:
        """
        Сохранить лог ошибки

        Args:
            method: Метод VK API
            error_code: Код ошибки
            error_message: Сообщение об ошибке
            params: Параметры запроса
        """
        # В простой реализации просто сохраняем в память
        # В продакшене это должно сохраняться в БД
        error_entry = {
            "method": method,
            "error_code": error_code,
            "error_message": error_message,
            "params": params,
            "timestamp": datetime.utcnow(),
        }

        if not hasattr(self, "_error_logs"):
            self._error_logs = []

        self._error_logs.append(error_entry)
        if len(self._error_logs) > 1000:
            self._error_logs = self._error_logs[-1000:]

    async def get_error_logs(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Получить логи ошибок

        Args:
            limit: Количество записей
            offset: Смещение

        Returns:
            List[Dict[str, Any]]: Логи ошибок
        """
        if not hasattr(self, "_error_logs"):
            return []

        logs = self._error_logs[::-1]  # Обратный порядок (новые сверху)
        return logs[offset : offset + limit]

    async def get_error_stats(self) -> Dict[str, Any]:
        """
        Получить статистику ошибок

        Returns:
            Dict[str, Any]: Статистика ошибок
        """
        if not hasattr(self, "_error_logs") or not self._error_logs:
            return {
                "total_errors": 0,
                "unique_error_codes": [],
                "most_common_error": None,
            }

        logs = self._error_logs
        total_errors = len(logs)

        # Уникальные коды ошибок
        error_codes = list(set(log["error_code"] for log in logs))
        error_codes.sort()

        # Самая распространенная ошибка
        error_counts = {}
        for log in logs:
            error_code = log["error_code"]
            error_counts[error_code] = error_counts.get(error_code, 0) + 1

        most_common_error = (
            max(error_counts.items(), key=lambda x: x[1])
            if error_counts
            else None
        )

        return {
            "total_errors": total_errors,
            "unique_error_codes": error_codes,
            "most_common_error": most_common_error,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить общую статистику репозитория

        Returns:
            Dict[str, Any]: Статистика
        """
        cache_stats = await self.get_cache_stats()
        request_stats = await self.get_request_stats()
        error_stats = await self.get_error_stats()

        return {
            "cache": cache_stats,
            "requests": request_stats,
            "errors": error_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить здоровье репозитория

        Returns:
            Dict[str, Any]: Результат проверки здоровья
        """
        try:
            # Проверяем основные функции
            cache_stats = await self.get_cache_stats()
            request_stats = await self.get_request_stats()

            return {
                "status": "healthy",
                "cache_entries": cache_stats["total_entries"],
                "total_requests": request_stats["total_requests"],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Функции для создания репозитория
async def get_vk_api_repository(db=None) -> VKAPIRepository:
    """Создать репозиторий VK API"""
    return VKAPIRepository(db)


# Экспорт
__all__ = [
    "VKAPIRepository",
    "get_vk_api_repository",
]
