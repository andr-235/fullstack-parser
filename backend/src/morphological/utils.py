"""
Вспомогательные функции модуля Morphological

Содержит утилиты для работы с морфологическим анализом текста
"""

import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter

from .constants import (
    MAX_TEXT_LENGTH,
    MAX_WORD_LENGTH,
    MAX_BATCH_SIZE,
    REGEX_TOKENIZE,
    REGEX_SENTENCE_SPLIT,
    REGEX_CYRILLIC,
    LANGUAGE_CYRILLIC_THRESHOLD,
    SUPPORTED_LANGUAGES,
    ALLOWED_POS,
)


def validate_text_input(text: str) -> Tuple[bool, str]:
    """
    Валидировать текст для анализа

    Args:
        text: Текст для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not text or not text.strip():
        return False, "Текст не может быть пустым"

    text = text.strip()
    if len(text) > MAX_TEXT_LENGTH:
        return (
            False,
            f"Текст слишком длинный (макс {MAX_TEXT_LENGTH} символов)",
        )

    return True, ""


def validate_word_input(word: str) -> Tuple[bool, str]:
    """
    Валидировать слово для анализа

    Args:
        word: Слово для валидации

    Returns:
        Tuple[bool, str]: (валидно ли, сообщение об ошибке)
    """
    if not word or not word.strip():
        return False, "Слово не может быть пустым"

    word = word.strip()
    if len(word) > MAX_WORD_LENGTH:
        return (
            False,
            f"Слово слишком длинное (макс {MAX_WORD_LENGTH} символов)",
        )

    # Проверка на допустимые символы
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-_\'"]+$', word):
        return False, "Слово содержит недопустимые символы"

    return True, ""


def validate_batch_input(texts: List[str]) -> Tuple[bool, str]:
    """
    Валидировать пакет текстов для анализа

    Args:
        texts: Список текстов для валидации

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not texts:
        return False, "Список текстов не может быть пустым"

    if len(texts) > MAX_BATCH_SIZE:
        return False, f"Слишком большой пакет (макс {MAX_BATCH_SIZE} текстов)"

    # Проверить каждый текст
    for i, text in enumerate(texts):
        is_valid, error = validate_text_input(text)
        if not is_valid:
            return False, f"Текст {i}: {error}"

    return True, ""


def tokenize_text(text: str) -> List[str]:
    """
    Разбить текст на слова (токенизация)

    Args:
        text: Текст для токенизации

    Returns:
        List[str]: Список слов
    """
    if not text:
        return []

    # Используем регулярное выражение для извлечения слов
    words = re.findall(REGEX_TOKENIZE, text.lower())

    # Фильтруем пустые строки и слишком короткие слова
    return [word for word in words if len(word) >= 2]


def split_into_sentences(text: str) -> List[str]:
    """
    Разбить текст на предложения

    Args:
        text: Текст для разбивки

    Returns:
        List[str]: Список предложений
    """
    if not text:
        return []

    # Разбиваем по точкам, восклицательным и вопросительным знакам
    sentences = re.split(REGEX_SENTENCE_SPLIT, text.strip())

    # Фильтруем пустые предложения
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def detect_language(text: str) -> Tuple[str, float]:
    """
    Определить язык текста

    Args:
        text: Текст для анализа

    Returns:
        Tuple[str, float]: (язык, уверенность)
    """
    if not text:
        return "unknown", 0.0

    # Подсчитываем количество кириллических символов
    cyrillic_chars = len(re.findall(REGEX_CYRILLIC, text))
    total_chars = len(re.sub(r"\s", "", text))

    if total_chars == 0:
        return "unknown", 0.0

    # Вычисляем долю кириллицы
    cyrillic_ratio = cyrillic_chars / total_chars

    if cyrillic_ratio >= LANGUAGE_CYRILLIC_THRESHOLD:
        return "ru", cyrillic_ratio
    else:
        return "unknown", 1.0 - cyrillic_ratio


def calculate_text_stats(text: str) -> Dict[str, Any]:
    """
    Вычислить статистику текста

    Args:
        text: Текст для анализа

    Returns:
        Dict[str, Any]: Статистика текста
    """
    sentences = split_into_sentences(text)
    words = tokenize_text(text)

    return {
        "total_chars": len(text),
        "total_chars_no_spaces": len(re.sub(r"\s", "", text)),
        "sentence_count": len(sentences),
        "word_count": len(words),
        "avg_words_per_sentence": (
            len(words) / len(sentences) if sentences else 0
        ),
        "avg_word_length": (
            sum(len(word) for word in words) / len(words) if words else 0
        ),
    }


def extract_keywords_from_words(
    words: List[Dict[str, Any]],
    max_keywords: int = 20,
    pos_filter: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Извлечь ключевые слова из списка проанализированных слов

    Args:
        words: Список проанализированных слов
        max_keywords: Максимум ключевых слов
        pos_filter: Фильтр по частям речи

    Returns:
        List[Dict[str, Any]]: Ключевые слова
    """
    if not words:
        return []

    # Фильтруем слова по части речи
    if pos_filter:
        filtered_words = [
            word for word in words if word.get("pos") in pos_filter
        ]
    else:
        # По умолчанию используем существительные, глаголы и прилагательные
        filtered_words = [
            word
            for word in words
            if word.get("pos") in ["NOUN", "VERB", "ADJ", "ADV"]
        ]

    if not filtered_words:
        return []

    # Считаем частоту лемм
    lemma_counts = Counter(
        word.get("lemma", word.get("word", "")) for word in filtered_words
    )

    # Создаем список ключевых слов
    keywords = []
    for lemma, count in lemma_counts.most_common(max_keywords):
        # Находим информацию о слове
        word_info = next(
            (word for word in filtered_words if word.get("lemma") == lemma),
            None,
        )

        if word_info:
            keywords.append(
                {
                    "word": word_info.get("word", lemma),
                    "lemma": lemma,
                    "pos": word_info.get("pos", "UNKNOWN"),
                    "frequency": count,
                    "weight": count / len(filtered_words),  # Простой вес
                }
            )

    return keywords


def generate_cache_key(operation: str, data: str, **params) -> str:
    """
    Сгенерировать ключ кеша для операции

    Args:
        operation: Тип операции
        data: Данные для хеширования
        **params: Дополнительные параметры

    Returns:
        str: Ключ кеша
    """
    # Создаем строку для хеширования
    cache_string = f"{operation}:{data}"

    if params:
        sorted_params = sorted(params.items())
        cache_string += f":{sorted_params}"

    # Создаем хеш
    return hashlib.md5(cache_string.encode()).hexdigest()[:16]


def normalize_text(text: str) -> str:
    """
    Нормализовать текст для анализа

    Args:
        text: Исходный текст

    Returns:
        str: Нормализованный текст
    """
    if not text:
        return ""

    # Приводим к нижнему регистру
    text = text.lower()

    # Убираем лишние пробелы
    text = re.sub(r"\s+", " ", text.strip())

    return text


def sanitize_text(text: str) -> str:
    """
    Очистить текст от потенциально опасных символов

    Args:
        text: Исходный текст

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удаляем HTML-теги (простая версия)
    text = re.sub(r"<[^>]+>", "", text)

    # Удаляем потенциально опасные символы
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, "")

    return text


def format_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Форматировать результат анализа для API

    Args:
        result: Результат анализа

    Returns:
        Dict[str, Any]: Форматированный результат
    """
    formatted = result.copy()

    # Форматирование числовых полей
    float_fields = ["analysis_time", "confidence", "weight"]
    for field in float_fields:
        if field in formatted and formatted[field] is not None:
            formatted[field] = round(formatted[field], 3)

    # Форматирование списков
    if "forms" in formatted and formatted["forms"]:
        formatted["forms"] = sorted(list(set(formatted["forms"])))

    if "keywords" in formatted and formatted["keywords"]:
        # Сортируем ключевые слова по весу
        formatted["keywords"] = sorted(
            formatted["keywords"],
            key=lambda x: x.get("weight", 0),
            reverse=True,
        )

    return formatted


def create_morphological_summary(
    words: List[Dict[str, Any]], sentences: List[str]
) -> Dict[str, Any]:
    """
    Создать сводку морфологического анализа

    Args:
        words: Проанализированные слова
        sentences: Предложения

    Returns:
        Dict[str, Any]: Сводка анализа
    """
    if not words:
        return {
            "total_words": 0,
            "total_sentences": 0,
            "pos_distribution": {},
            "avg_word_length": 0,
            "unique_lemmas": 0,
        }

    # Распределение по частям речи
    pos_counts = Counter(word.get("pos", "UNKNOWN") for word in words)

    # Статистика длин слов
    word_lengths = [len(word.get("word", "")) for word in words]

    # Уникальные леммы
    unique_lemmas = len(
        set(word.get("lemma", word.get("word", "")) for word in words)
    )

    return {
        "total_words": len(words),
        "total_sentences": len(sentences),
        "pos_distribution": dict(pos_counts),
        "avg_word_length": (
            sum(word_lengths) / len(word_lengths) if word_lengths else 0
        ),
        "unique_lemmas": unique_lemmas,
        "most_common_pos": pos_counts.most_common(3),
    }


def validate_pos_list(pos_list: List[str]) -> Tuple[bool, str]:
    """
    Валидировать список частей речи

    Args:
        pos_list: Список частей речи

    Returns:
        Tuple[bool, str]: (валиден ли, сообщение об ошибке)
    """
    if not pos_list:
        return True, ""  # Пустой список разрешен

    invalid_pos = [pos for pos in pos_list if pos not in ALLOWED_POS]
    if invalid_pos:
        return (
            False,
            f"Недопустимые части речи: {', '.join(invalid_pos)}. Допустимые: {', '.join(ALLOWED_POS)}",
        )

    return True, ""


def calculate_analysis_performance(
    start_time: float, end_time: float, word_count: int, text_length: int
) -> Dict[str, Any]:
    """
    Вычислить показатели производительности анализа

    Args:
        start_time: Время начала
        end_time: Время окончания
        word_count: Количество слов
        text_length: Длина текста

    Returns:
        Dict[str, Any]: Показатели производительности
    """
    total_time = end_time - start_time

    return {
        "total_time": round(total_time, 3),
        "words_per_second": (
            round(word_count / total_time, 2) if total_time > 0 else 0
        ),
        "chars_per_second": (
            round(text_length / total_time, 2) if total_time > 0 else 0
        ),
        "avg_time_per_word": (
            round(total_time / word_count, 4) if word_count > 0 else 0
        ),
    }


def create_error_summary(errors: List[str]) -> Dict[str, Any]:
    """
    Создать сводку ошибок анализа

    Args:
        errors: Список ошибок

    Returns:
        Dict[str, Any]: Сводка ошибок
    """
    if not errors:
        return {
            "total_errors": 0,
            "error_types": {},
            "most_common_error": None,
        }

    error_counts = Counter(errors)

    return {
        "total_errors": len(errors),
        "error_types": dict(error_counts),
        "most_common_error": (
            error_counts.most_common(1)[0] if error_counts else None
        ),
        "unique_errors": len(error_counts),
    }


# Экспорт всех функций
__all__ = [
    "validate_text_input",
    "validate_word_input",
    "validate_batch_input",
    "tokenize_text",
    "split_into_sentences",
    "detect_language",
    "calculate_text_stats",
    "extract_keywords_from_words",
    "generate_cache_key",
    "normalize_text",
    "sanitize_text",
    "format_analysis_result",
    "create_morphological_summary",
    "validate_pos_list",
    "calculate_analysis_performance",
    "create_error_summary",
]
