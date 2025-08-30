"""
Конфигурация модуля Morphological

Содержит настройки специфичные для модуля морфологического анализа
"""

from typing import Optional, List

from ..config import settings


class MorphologicalConfig:
    """Конфигурация для модуля морфологического анализа"""

    # Настройки анализатора
    ANALYZER_TYPE = "pymorphy2"
    LANGUAGE = "ru"
    CACHE_ENABLED = True
    MAX_CACHE_SIZE = 10000

    # Настройки производительности
    MAX_TEXT_LENGTH = 10000
    MAX_WORD_LENGTH = 100
    MAX_BATCH_SIZE = 100
    TIMEOUT_SECONDS = 5.0

    # Настройки обработки текста
    MIN_WORD_LENGTH = 2
    MAX_KEYWORDS = 50
    MIN_KEYWORD_LENGTH = 3

    # Настройки кеширования
    CACHE_TTL_SECONDS = 3600  # 1 час
    WORD_CACHE_TTL = 1800  # 30 минут
    TEXT_CACHE_TTL = 900  # 15 минут

    # Настройки частей речи для ключевых слов
    KEYWORD_POS = ["NOUN", "VERB", "ADJ", "ADV"]
    NOUN_POS = ["NOUN"]
    VERB_POS = ["VERB"]
    ADJECTIVE_POS = ["ADJ"]
    ADVERB_POS = ["ADV"]

    # Настройки токенизации
    TOKENIZE_PATTERN = r"\b\w+\b"
    SENTENCE_SPLIT_PATTERN = r"(?<=[.!?])\s+"

    # Настройки определения языка
    LANGUAGE_DETECTION_THRESHOLD = 0.3
    SUPPORTED_LANGUAGES = ["ru", "en", "unknown"]

    # Настройки статистики
    STATS_UPDATE_INTERVAL = 300  # 5 минут
    STATS_RETENTION_DAYS = 30

    @classmethod
    def get_analyzer_config(cls) -> dict:
        """Получить конфигурацию анализатора"""
        return {
            "type": cls.ANALYZER_TYPE,
            "language": cls.LANGUAGE,
            "cache_enabled": cls.CACHE_ENABLED,
            "max_cache_size": cls.MAX_CACHE_SIZE,
        }

    @classmethod
    def get_performance_config(cls) -> dict:
        """Получить конфигурацию производительности"""
        return {
            "max_text_length": cls.MAX_TEXT_LENGTH,
            "max_word_length": cls.MAX_WORD_LENGTH,
            "max_batch_size": cls.MAX_BATCH_SIZE,
            "timeout_seconds": cls.TIMEOUT_SECONDS,
        }

    @classmethod
    def get_text_processing_config(cls) -> dict:
        """Получить конфигурацию обработки текста"""
        return {
            "min_word_length": cls.MIN_WORD_LENGTH,
            "max_keywords": cls.MAX_KEYWORDS,
            "min_keyword_length": cls.MIN_KEYWORD_LENGTH,
            "tokenize_pattern": cls.TOKENIZE_PATTERN,
            "sentence_split_pattern": cls.SENTENCE_SPLIT_PATTERN,
        }

    @classmethod
    def get_keyword_config(cls) -> dict:
        """Получить конфигурацию ключевых слов"""
        return {
            "keyword_pos": cls.KEYWORD_POS,
            "noun_pos": cls.NOUN_POS,
            "verb_pos": cls.VERB_POS,
            "adjective_pos": cls.ADJECTIVE_POS,
            "adverb_pos": cls.ADVERB_POS,
        }

    @classmethod
    def get_cache_config(cls) -> dict:
        """Получить конфигурацию кеширования"""
        return {
            "cache_ttl": cls.CACHE_TTL_SECONDS,
            "word_cache_ttl": cls.WORD_CACHE_TTL,
            "text_cache_ttl": cls.TEXT_CACHE_TTL,
        }

    @classmethod
    def get_language_config(cls) -> dict:
        """Получить конфигурацию определения языка"""
        return {
            "detection_threshold": cls.LANGUAGE_DETECTION_THRESHOLD,
            "supported_languages": cls.SUPPORTED_LANGUAGES,
        }

    @classmethod
    def validate_text_length(cls, text: str) -> bool:
        """Проверить длину текста"""
        return len(text) <= cls.MAX_TEXT_LENGTH

    @classmethod
    def validate_word_length(cls, word: str) -> bool:
        """Проверить длину слова"""
        return cls.MIN_WORD_LENGTH <= len(word) <= cls.MAX_WORD_LENGTH

    @classmethod
    def validate_batch_size(cls, batch_size: int) -> bool:
        """Проверить размер батча"""
        return 1 <= batch_size <= cls.MAX_BATCH_SIZE

    @classmethod
    def is_supported_pos(cls, pos: str) -> bool:
        """Проверить, поддерживается ли часть речи"""
        return pos in cls.KEYWORD_POS

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Получить список поддерживаемых языков"""
        return cls.SUPPORTED_LANGUAGES.copy()


# Экземпляр конфигурации
morphological_config = MorphologicalConfig()


# Экспорт
__all__ = [
    "MorphologicalConfig",
    "morphological_config",
]
