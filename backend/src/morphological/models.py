"""
Модели для модуля Morphological

Определяет репозиторий для работы с морфологическим анализом
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db_session


class MorphologicalRepository:
    """
    Репозиторий для работы с данными морфологического анализа

    Предоставляет интерфейс для хранения результатов анализа
    """

    def __init__(self, db=None):
        self.db = db
        # В памяти для простоты (в продакшене использовать Redis/DB)
        self._analysis_cache = {}
        self._stats_cache = {}

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def save_word_analysis(
        self, word: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сохранить результат анализа слова

        Args:
            word: Слово
            analysis: Результат анализа

        Returns:
            Dict[str, Any]: Сохраненный результат
        """
        cache_key = f"word:{word.lower()}"
        analysis["cached_at"] = datetime.utcnow()
        self._analysis_cache[cache_key] = analysis
        return analysis

    async def get_word_analysis(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Получить результат анализа слова

        Args:
            word: Слово

        Returns:
            Optional[Dict[str, Any]]: Результат анализа или None
        """
        cache_key = f"word:{word.lower()}"
        result = self._analysis_cache.get(cache_key)

        if result:
            # Проверяем актуальность кеша (TTL = 30 минут)
            cached_at = result.get("cached_at")
            if cached_at and (datetime.utcnow() - cached_at).seconds < 1800:
                return result
            else:
                # Удаляем устаревший кеш
                del self._analysis_cache[cache_key]

        return None

    async def save_text_analysis(
        self, text_hash: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сохранить результат анализа текста

        Args:
            text_hash: Хеш текста
            analysis: Результат анализа

        Returns:
            Dict[str, Any]: Сохраненный результат
        """
        cache_key = f"text:{text_hash}"
        analysis["cached_at"] = datetime.utcnow()
        self._analysis_cache[cache_key] = analysis
        return analysis

    async def get_text_analysis(
        self, text_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить результат анализа текста

        Args:
            text_hash: Хеш текста

        Returns:
            Optional[Dict[str, Any]]: Результат анализа или None
        """
        cache_key = f"text:{text_hash}"
        result = self._analysis_cache.get(cache_key)

        if result:
            # Проверяем актуальность кеша (TTL = 15 минут)
            cached_at = result.get("cached_at")
            if cached_at and (datetime.utcnow() - cached_at).seconds < 900:
                return result
            else:
                # Удаляем устаревший кеш
                del self._analysis_cache[cache_key]

        return None

    async def save_search_patterns(
        self, word: str, patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Сохранить паттерны поиска для слова

        Args:
            word: Слово
            patterns: Паттерны поиска

        Returns:
            List[Dict[str, Any]]: Сохраненные паттерны
        """
        cache_key = f"patterns:{word.lower()}"
        self._analysis_cache[cache_key] = {
            "patterns": patterns,
            "cached_at": datetime.utcnow(),
        }
        return patterns

    async def get_search_patterns(
        self, word: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Получить паттерны поиска для слова

        Args:
            word: Слово

        Returns:
            Optional[List[Dict[str, Any]]]: Паттерны поиска или None
        """
        cache_key = f"patterns:{word.lower()}"
        result = self._analysis_cache.get(cache_key)

        if result:
            # Проверяем актуальность кеша (TTL = 1 час)
            cached_at = result.get("cached_at")
            if cached_at and (datetime.utcnow() - cached_at).seconds < 3600:
                return result.get("patterns")
            else:
                # Удаляем устаревший кеш
                del self._analysis_cache[cache_key]

        return None

    async def update_stats(self, stat_type: str, value: Any) -> None:
        """
        Обновить статистику

        Args:
            stat_type: Тип статистики
            value: Значение
        """
        self._stats_cache[stat_type] = {
            "value": value,
            "updated_at": datetime.utcnow(),
        }

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику морфологического анализа

        Returns:
            Dict[str, Any]: Статистика
        """
        # Базовая статистика
        stats = {
            "total_words_analyzed": 0,
            "total_texts_analyzed": 0,
            "cache_hit_rate": 0.8,  # Заглушка
            "average_analysis_time": 0.05,  # Заглушка
            "supported_languages": ["ru", "en", "unknown"],
            "analyzer_version": "pymorphy2",
            "cache_size": len(self._analysis_cache),
        }

        # Обновляем из кеша статистики
        for stat_type, stat_data in self._stats_cache.items():
            stats[stat_type] = stat_data["value"]

        return stats

    async def clear_expired_cache(self) -> int:
        """
        Очистить устаревший кеш

        Returns:
            int: Количество удаленных записей
        """
        current_time = datetime.utcnow()
        expired_keys = []

        for key, data in self._analysis_cache.items():
            cached_at = data.get("cached_at")
            if cached_at:
                # Разные TTL для разных типов данных
                if key.startswith("word:"):
                    ttl = 1800  # 30 минут
                elif key.startswith("text:"):
                    ttl = 900  # 15 минут
                elif key.startswith("patterns:"):
                    ttl = 3600  # 1 час
                else:
                    ttl = 1800  # 30 минут по умолчанию

                if (current_time - cached_at).seconds > ttl:
                    expired_keys.append(key)

        # Удаляем устаревшие записи
        for key in expired_keys:
            del self._analysis_cache[key]

        return len(expired_keys)

    async def get_cache_info(self) -> Dict[str, Any]:
        """
        Получить информацию о кеше

        Returns:
            Dict[str, Any]: Информация о кеше
        """
        total_entries = len(self._analysis_cache)

        # Классифицируем записи по типам
        word_entries = sum(
            1 for key in self._analysis_cache.keys() if key.startswith("word:")
        )
        text_entries = sum(
            1 for key in self._analysis_cache.keys() if key.startswith("text:")
        )
        pattern_entries = sum(
            1
            for key in self._analysis_cache.keys()
            if key.startswith("patterns:")
        )

        return {
            "total_entries": total_entries,
            "word_entries": word_entries,
            "text_entries": text_entries,
            "pattern_entries": pattern_entries,
            "cache_memory_usage": total_entries
            * 1024,  # Примерная оценка в байтах
        }

    async def save_batch_analysis(
        self, batch_id: str, results: List[Dict[str, Any]]
    ) -> str:
        """
        Сохранить результаты пакетного анализа

        Args:
            batch_id: ID пакета
            results: Результаты анализа

        Returns:
            str: ID сохраненного пакета
        """
        cache_key = f"batch:{batch_id}"
        self._analysis_cache[cache_key] = {
            "results": results,
            "saved_at": datetime.utcnow(),
            "result_count": len(results),
        }
        return batch_id

    async def get_batch_analysis(
        self, batch_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Получить результаты пакетного анализа

        Args:
            batch_id: ID пакета

        Returns:
            Optional[List[Dict[str, Any]]]: Результаты анализа или None
        """
        cache_key = f"batch:{batch_id}"
        result = self._analysis_cache.get(cache_key)

        if result:
            # Проверяем актуальность кеша (TTL = 1 час для батчей)
            saved_at = result.get("saved_at")
            if saved_at and (datetime.utcnow() - saved_at).seconds < 3600:
                return result.get("results")
            else:
                # Удаляем устаревший кеш
                del self._analysis_cache[cache_key]

        return None

    async def cleanup_stats_cache(self) -> int:
        """
        Очистить устаревший кеш статистики

        Returns:
            int: Количество удаленных записей
        """
        current_time = datetime.utcnow()
        expired_keys = []

        for key, data in self._stats_cache.items():
            updated_at = data.get("updated_at")
            if (
                updated_at and (current_time - updated_at).seconds > 300
            ):  # 5 минут
                expired_keys.append(key)

        # Удаляем устаревшие записи
        for key in expired_keys:
            del self._stats_cache[key]

        return len(expired_keys)


# Функции для создания репозитория
async def get_morphological_repository(db=None) -> MorphologicalRepository:
    """Создать репозиторий морфологического анализа"""
    return MorphologicalRepository(db)


# Экспорт
__all__ = [
    "MorphologicalRepository",
    "get_morphological_repository",
]
