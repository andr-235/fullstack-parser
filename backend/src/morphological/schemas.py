"""
Pydantic схемы для модуля Morphological

Определяет входные и выходные модели данных для API морфологического анализа
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class WordFeatures(BaseModel):
    """Морфологические признаки слова"""

    case: Optional[str] = Field(None, description="Падеж")
    number: Optional[str] = Field(None, description="Число")
    gender: Optional[str] = Field(None, description="Род")
    tense: Optional[str] = Field(None, description="Время")
    person: Optional[str] = Field(None, description="Лицо")
    aspect: Optional[str] = Field(None, description="Вид")
    voice: Optional[str] = Field(None, description="Залог")
    mood: Optional[str] = Field(None, description="Наклонение")


class WordInfo(BaseModel):
    """Информация о слове"""

    model_config = ConfigDict(from_attributes=True)

    word: str = Field(..., description="Исходное слово")
    lemma: str = Field(..., description="Лемма (начальная форма)")
    pos: str = Field(..., description="Часть речи")
    features: WordFeatures = Field(
        default_factory=WordFeatures, description="Морфологические признаки"
    )
    forms: List[str] = Field(
        default_factory=list, description="Все формы слова"
    )
    confidence: float = Field(
        1.0, description="Уверенность анализа", ge=0.0, le=1.0
    )


class WordAnalysisRequest(BaseModel):
    """Запрос на анализ слова"""

    word: str = Field(
        ..., min_length=1, max_length=100, description="Слово для анализа"
    )


class WordAnalysisResponse(BaseModel):
    """Ответ с анализом слова"""

    word_info: WordInfo = Field(..., description="Информация о слове")
    analysis_time: float = Field(..., description="Время анализа в секундах")


class WordFormsRequest(BaseModel):
    """Запрос на получение форм слова"""

    word: str = Field(
        ..., min_length=1, max_length=100, description="Слово для анализа"
    )


class WordFormsResponse(BaseModel):
    """Ответ с формами слова"""

    word: str = Field(..., description="Исходное слово")
    lemma: str = Field(..., description="Лемма")
    forms: List[str] = Field(..., description="Все формы слова")
    count: int = Field(..., description="Количество форм")


class TextAnalysisRequest(BaseModel):
    """Запрос на анализ текста"""

    text: str = Field(
        ..., min_length=1, max_length=10000, description="Текст для анализа"
    )
    extract_keywords: bool = Field(
        True, description="Извлекать ключевые слова"
    )
    include_sentences: bool = Field(
        True, description="Включать анализ предложений"
    )


class SentenceAnalysis(BaseModel):
    """Анализ предложения"""

    text: str = Field(..., description="Текст предложения")
    words: List[WordInfo] = Field(..., description="Слова в предложении")
    keywords: List[str] = Field(
        ..., description="Ключевые слова в предложении"
    )


class TextAnalysisResponse(BaseModel):
    """Ответ с анализом текста"""

    text: str = Field(..., description="Исходный текст")
    sentences: List[SentenceAnalysis] = Field(
        ..., description="Анализ предложений"
    )
    words: List[WordInfo] = Field(..., description="Все слова в тексте")
    lemmas: List[str] = Field(..., description="Все леммы")
    keywords: List[str] = Field(..., description="Ключевые слова")
    word_count: int = Field(..., description="Количество слов")
    sentence_count: int = Field(..., description="Количество предложений")
    analysis_time: float = Field(..., description="Время анализа в секундах")


class SearchPatternRequest(BaseModel):
    """Запрос на создание паттерна поиска"""

    base_word: str = Field(
        ..., min_length=1, max_length=100, description="Базовое слово"
    )
    case_sensitive: bool = Field(
        False, description="Чувствительность к регистру"
    )
    whole_word: bool = Field(True, description="Поиск целых слов")
    include_forms: bool = Field(True, description="Включать все формы слова")


class SearchPattern(BaseModel):
    """Паттерн поиска"""

    pattern: str = Field(..., description="Текст паттерна")
    type: str = Field(..., description="Тип паттерна")
    description: str = Field(..., description="Описание паттерна")


class SearchPatternResponse(BaseModel):
    """Ответ с паттернами поиска"""

    base_word: str = Field(..., description="Базовое слово")
    lemma: str = Field(..., description="Лемма")
    patterns: List[SearchPattern] = Field(..., description="Паттерны поиска")
    count: int = Field(..., description="Количество паттернов")


class MorphologicalConfig(BaseModel):
    """Конфигурация морфологического анализа"""

    analyzer_type: str = Field("pymorphy2", description="Тип анализатора")
    language: str = Field("ru", description="Язык анализа")
    cache_enabled: bool = Field(True, description="Включить кеширование")
    max_text_length: int = Field(
        10000, description="Максимальная длина текста"
    )
    timeout_seconds: float = Field(5.0, description="Таймаут анализа")


class MorphologicalStats(BaseModel):
    """Статистика морфологического анализа"""

    total_words_analyzed: int = Field(
        ..., description="Всего проанализировано слов"
    )
    total_texts_analyzed: int = Field(
        ..., description="Всего проанализировано текстов"
    )
    cache_hit_rate: float = Field(..., description="Процент попаданий в кеш")
    average_analysis_time: float = Field(
        ..., description="Среднее время анализа"
    )
    supported_languages: List[str] = Field(
        ..., description="Поддерживаемые языки"
    )
    analyzer_version: str = Field(..., description="Версия анализатора")


class BatchAnalysisRequest(BaseModel):
    """Запрос на пакетный анализ"""

    texts: List[str] = Field(
        ..., description="Список текстов для анализа", max_length=100
    )
    extract_keywords: bool = Field(
        True, description="Извлекать ключевые слова"
    )


class BatchAnalysisItem(BaseModel):
    """Элемент пакетного анализа"""

    text_index: int = Field(..., description="Индекс текста в запросе")
    analysis: TextAnalysisResponse = Field(
        ..., description="Результат анализа"
    )


class BatchAnalysisResponse(BaseModel):
    """Ответ на пакетный анализ"""

    results: List[BatchAnalysisItem] = Field(
        ..., description="Результаты анализа"
    )
    total_texts: int = Field(..., description="Общее количество текстов")
    successful_analyses: int = Field(..., description="Успешных анализов")
    failed_analyses: int = Field(..., description="Неудачных анализов")
    total_analysis_time: float = Field(..., description="Общее время анализа")


class KeywordExtractionRequest(BaseModel):
    """Запрос на извлечение ключевых слов"""

    text: str = Field(
        ..., min_length=1, max_length=10000, description="Текст для анализа"
    )
    max_keywords: int = Field(
        20, description="Максимум ключевых слов", ge=1, le=100
    )
    min_keyword_length: int = Field(
        3, description="Минимальная длина ключевого слова", ge=1, le=50
    )
    pos_filter: Optional[List[str]] = Field(
        None, description="Фильтр по частям речи"
    )


class KeywordInfo(BaseModel):
    """Информация о ключевом слове"""

    word: str = Field(..., description="Ключевое слово")
    lemma: str = Field(..., description="Лемма")
    pos: str = Field(..., description="Часть речи")
    frequency: int = Field(..., description="Частота встречаемости")
    weight: float = Field(..., description="Вес ключевого слова")


class KeywordExtractionResponse(BaseModel):
    """Ответ с извлечением ключевых слов"""

    text: str = Field(..., description="Исходный текст")
    keywords: List[KeywordInfo] = Field(..., description="Ключевые слова")
    total_words: int = Field(..., description="Общее количество слов")
    keyword_count: int = Field(..., description="Количество ключевых слов")
    extraction_time: float = Field(..., description="Время извлечения")


class LanguageDetectionRequest(BaseModel):
    """Запрос на определение языка"""

    text: str = Field(
        ..., min_length=1, max_length=1000, description="Текст для анализа"
    )


class LanguageDetectionResponse(BaseModel):
    """Ответ с определением языка"""

    text: str = Field(..., description="Исходный текст")
    detected_language: str = Field(..., description="Определенный язык")
    confidence: float = Field(
        ..., description="Уверенность определения", ge=0.0, le=1.0
    )
    supported_languages: List[str] = Field(
        ..., description="Поддерживаемые языки"
    )


# Экспорт всех схем
__all__ = [
    "WordFeatures",
    "WordInfo",
    "WordAnalysisRequest",
    "WordAnalysisResponse",
    "WordFormsRequest",
    "WordFormsResponse",
    "TextAnalysisRequest",
    "SentenceAnalysis",
    "TextAnalysisResponse",
    "SearchPatternRequest",
    "SearchPattern",
    "SearchPatternResponse",
    "MorphologicalConfig",
    "MorphologicalStats",
    "BatchAnalysisRequest",
    "BatchAnalysisItem",
    "BatchAnalysisResponse",
    "KeywordExtractionRequest",
    "KeywordInfo",
    "KeywordExtractionResponse",
    "LanguageDetectionRequest",
    "LanguageDetectionResponse",
]
