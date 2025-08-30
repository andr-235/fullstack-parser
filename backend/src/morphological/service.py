"""
Сервис для работы с морфологическим анализом

Содержит бизнес-логику для операций морфологического анализа текста
"""

import time
import re
from typing import List, Optional, Dict, Any
from collections import Counter

from ..exceptions import ValidationError, ServiceUnavailableError
from .models import MorphologicalRepository
from .constants import (
    POS_NOUN,
    POS_VERB,
    POS_ADJECTIVE,
    POS_ADVERB,
    SUPPORTED_LANGUAGES,
    MAX_TEXT_LENGTH,
    MAX_WORD_LENGTH,
)


class MorphologicalService:
    """
    Сервис для морфологического анализа текста

    Реализует бизнес-логику для анализа слов и текста на русском языке
    """

    def __init__(self, repository: MorphologicalRepository):
        self.repository = repository
        self._analyzer = None
        # Кеш результатов анализа: ключ -> результат анализа слова
        self._cache: Dict[str, Dict[str, Any]] = {}

    @property
    def analyzer(self):
        """Ленивая инициализация анализатора"""
        if self._analyzer is None:
            try:
                import pymorphy2

                self._analyzer = pymorphy2.MorphAnalyzer()
            except ImportError:
                # Заглушка для случаев, когда pymorphy2 недоступен
                self._analyzer = self._create_fallback_analyzer()
        return self._analyzer

    def _create_fallback_analyzer(self):
        """Создать заглушку анализатора"""

        class FallbackAnalyzer:
            def parse(self, word):
                # Возвращаем базовую информацию без анализа
                class MockParse:
                    def __init__(self, word):
                        self.word = word
                        self.normal_form = word.lower()
                        self.POS = "UNKNOWN"
                        self.tag = None

                return [MockParse(word)]

        return FallbackAnalyzer()

    async def analyze_word(self, word: str) -> Dict[str, Any]:
        """
        Анализировать слово морфологически

        Args:
            word: Слово для анализа

        Returns:
            Dict[str, Any]: Результат анализа слова
        """
        if not word or not word.strip():
            raise ValidationError("Слово не может быть пустым", field="word")

        word = word.strip()
        if len(word) > MAX_WORD_LENGTH:
            raise ValidationError(
                f"Слово слишком длинное (макс {MAX_WORD_LENGTH} символов)",
                field="word",
            )

        # Проверяем кеш
        cache_key = f"word:{word.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        start_time = time.time()

        try:
            # Анализируем слово
            parses = self.analyzer.parse(word)

            if not parses:
                # Если анализатор не смог разобрать слово
                result = {
                    "word": word,
                    "lemma": word.lower(),
                    "pos": "UNKNOWN",
                    "features": {},
                    "forms": [word.lower()],
                    "confidence": 0.0,
                    "analysis_time": time.time() - start_time,
                }
            else:
                # Берем наиболее вероятный разбор
                best_parse = parses[0]

                # Извлекаем информацию
                lemma = getattr(best_parse, "normal_form", word.lower())
                pos = getattr(best_parse, "POS", "UNKNOWN")

                # Извлекаем морфологические признаки
                features = {}
                if hasattr(best_parse, "tag") and best_parse.tag:
                    tag = best_parse.tag

                    # Сопоставляем признаки с нашей моделью
                    feature_mapping = {
                        "case": "Case",
                        "number": "Number",
                        "gender": "Gender",
                        "tense": "Tense",
                        "person": "Person",
                        "aspect": "Aspect",
                        "voice": "Voice",
                        "mood": "Mood",
                    }

                    for our_key, pymorphy_key in feature_mapping.items():
                        if hasattr(tag, pymorphy_key):
                            value = getattr(tag, pymorphy_key)
                            if value:
                                features[our_key] = str(value)

                # Получаем все формы слова
                forms = await self._get_word_forms(word, lemma)

                result = {
                    "word": word,
                    "lemma": lemma,
                    "pos": pos,
                    "features": features,
                    "forms": forms,
                    "confidence": getattr(best_parse, "score", 1.0),
                    "analysis_time": time.time() - start_time,
                }

            # Сохраняем в кеш
            self._cache[cache_key] = result

            return result

        except Exception as e:
            raise ServiceUnavailableError(
                f"Ошибка анализа слова '{word}': {str(e)}"
            )

    async def get_word_forms(self, word: str) -> Dict[str, Any]:
        """
        Получить все морфологические формы слова

        Args:
            word: Слово для анализа

        Returns:
            Dict[str, Any]: Формы слова
        """
        word_info = await self.analyze_word(word)

        return {
            "word": word,
            "lemma": word_info["lemma"],
            "forms": word_info["forms"],
            "count": len(word_info["forms"]),
        }

    async def analyze_text(
        self, text: str, extract_keywords: bool = True
    ) -> Dict[str, Any]:
        """
        Анализировать текст морфологически

        Args:
            text: Текст для анализа
            extract_keywords: Извлекать ли ключевые слова

        Returns:
            Dict[str, Any]: Результат анализа текста
        """
        if not text or not text.strip():
            raise ValidationError("Текст не может быть пустым", field="text")

        text = text.strip()
        if len(text) > MAX_TEXT_LENGTH:
            raise ValidationError(
                f"Текст слишком длинный (макс {MAX_TEXT_LENGTH} символов)",
                field="text",
            )

        start_time = time.time()

        try:
            # Разбиваем текст на предложения
            sentences = self._split_into_sentences(text)

            # Анализируем каждое предложение
            analyzed_sentences = []
            all_words = []
            all_lemmas = []
            all_keywords = []

            for sentence_text in sentences:
                sentence_analysis = await self._analyze_sentence(
                    sentence_text, extract_keywords
                )
                analyzed_sentences.append(sentence_analysis)

                all_words.extend(sentence_analysis["words"])
                all_lemmas.extend(sentence_analysis["lemmas"])
                all_keywords.extend(sentence_analysis["keywords"])

            # Убираем дубликаты
            all_lemmas = list(set(all_lemmas))
            all_keywords = list(set(all_keywords))

            result = {
                "text": text,
                "sentences": analyzed_sentences,
                "words": all_words,
                "lemmas": all_lemmas,
                "keywords": all_keywords if extract_keywords else [],
                "word_count": len(all_words),
                "sentence_count": len(sentences),
                "analysis_time": time.time() - start_time,
            }

            return result

        except Exception as e:
            raise ServiceUnavailableError(f"Ошибка анализа текста: {str(e)}")

    async def create_search_patterns(
        self, base_word: str, **options
    ) -> Dict[str, Any]:
        """
        Создать паттерны поиска для слова

        Args:
            base_word: Базовое слово
            **options: Опции поиска

        Returns:
            Dict[str, Any]: Паттерны поиска
        """
        word_info = await self.analyze_word(base_word)

        patterns = []
        include_forms = options.get("include_forms", True)
        case_sensitive = options.get("case_sensitive", False)

        # Базовая лемма
        patterns.append(
            {
                "pattern": word_info["lemma"],
                "type": "lemma",
                "description": "Лемма слова",
            }
        )

        if include_forms:
            # Все формы слова
            for form in word_info["forms"]:
                if form != word_info["lemma"]:  # Избегаем дублирования
                    patterns.append(
                        {
                            "pattern": form,
                            "type": "form",
                            "description": f"Форма слова: {form}",
                        }
                    )

        # Паттерны для разных частей речи
        if word_info["pos"] == POS_NOUN:
            patterns.extend(await self._create_noun_patterns(word_info))
        elif word_info["pos"] == POS_VERB:
            patterns.extend(await self._create_verb_patterns(word_info))
        elif word_info["pos"] == POS_ADJECTIVE:
            patterns.extend(await self._create_adjective_patterns(word_info))

        return {
            "base_word": base_word,
            "lemma": word_info["lemma"],
            "patterns": patterns,
            "count": len(patterns),
        }

    async def extract_keywords(
        self,
        text: str,
        max_keywords: int = 20,
        min_length: int = 3,
        pos_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Извлечь ключевые слова из текста

        Args:
            text: Текст для анализа
            max_keywords: Максимум ключевых слов
            min_length: Минимальная длина слова
            pos_filter: Фильтр по частям речи

        Returns:
            Dict[str, Any]: Ключевые слова
        """
        text_analysis = await self.analyze_text(text, extract_keywords=True)

        # Фильтруем слова по критериям
        candidate_keywords = []

        for word_info in text_analysis["words"]:
            # Проверяем длину
            if len(word_info["word"]) < min_length:
                continue

            # Проверяем часть речи
            if pos_filter and word_info["pos"] not in pos_filter:
                continue

            # Проверяем, что это существительное, прилагательное или глагол
            if word_info["pos"] not in [POS_NOUN, POS_VERB, POS_ADJECTIVE]:
                continue

            candidate_keywords.append(word_info)

        # Считаем частоту лемм
        lemma_counts = Counter(word["lemma"] for word in candidate_keywords)

        # Создаем список ключевых слов
        keywords = []
        for lemma, count in lemma_counts.most_common(max_keywords):
            # Находим информацию о слове
            word_info = next(
                (w for w in candidate_keywords if w["lemma"] == lemma), None
            )

            if word_info:
                keywords.append(
                    {
                        "word": word_info["word"],
                        "lemma": lemma,
                        "pos": word_info["pos"],
                        "frequency": count,
                        "weight": float(count)
                        / len(candidate_keywords),  # Простой вес
                    }
                )

        return {
            "text": text,
            "keywords": keywords,
            "total_words": text_analysis["word_count"],
            "keyword_count": len(keywords),
            "extraction_time": text_analysis["analysis_time"],
        }

    async def batch_analyze(
        self, texts: List[str], extract_keywords: bool = True
    ) -> Dict[str, Any]:
        """
        Пакетный анализ текстов

        Args:
            texts: Список текстов для анализа
            extract_keywords: Извлекать ли ключевые слова

        Returns:
            Dict[str, Any]: Результаты анализа
        """
        if len(texts) > 100:
            raise ValidationError(
                "Максимум 100 текстов за один запрос", field="texts"
            )

        start_time = time.time()
        results = []
        successful = 0
        failed = 0

        for i, text in enumerate(texts):
            try:
                analysis = await self.analyze_text(text, extract_keywords)
                results.append(
                    {
                        "text_index": i,
                        "analysis": analysis,
                    }
                )
                successful += 1
            except Exception as e:
                results.append(
                    {
                        "text_index": i,
                        "analysis": None,
                        "error": str(e),
                    }
                )
                failed += 1

        return {
            "results": results,
            "total_texts": len(texts),
            "successful_analyses": successful,
            "failed_analyses": failed,
            "total_analysis_time": time.time() - start_time,
        }

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Определить язык текста

        Args:
            text: Текст для анализа

        Returns:
            Dict[str, Any]: Результат определения языка
        """
        # Простая эвристика для определения русского языка
        cyrillic_chars = sum(
            1 for char in text if "\u0400" <= char <= "\u04FF"
        )
        total_chars = len(text.replace(" ", ""))

        if total_chars == 0:
            confidence = 0.0
            detected_lang = "unknown"
        else:
            cyrillic_ratio = cyrillic_chars / total_chars
            if cyrillic_ratio > 0.3:
                confidence = min(cyrillic_ratio, 1.0)
                detected_lang = "ru"
            else:
                confidence = 1.0 - cyrillic_ratio
                detected_lang = "unknown"

        return {
            "text": text,
            "detected_language": detected_lang,
            "confidence": confidence,
            "supported_languages": SUPPORTED_LANGUAGES,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику морфологического анализа

        Returns:
            Dict[str, Any]: Статистика
        """
        cache_size = len(self._cache)
        cache_hit_rate = 0.8  # Заглушка

        return {
            "total_words_analyzed": cache_size,
            "total_texts_analyzed": cache_size // 10,  # Примерная оценка
            "cache_hit_rate": cache_hit_rate,
            "average_analysis_time": 0.05,  # Заглушка
            "supported_languages": SUPPORTED_LANGUAGES,
            "analyzer_version": (
                "pymorphy2"
                if hasattr(self, "_analyzer") and self._analyzer
                else "fallback"
            ),
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """Разбить текст на предложения"""
        # Простая разбивка по точкам, восклицательным и вопросительным знакам
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _tokenize_text(self, text: str) -> List[str]:
        """Разбить текст на слова"""
        # Удаляем пунктуацию и разбиваем по пробелам
        words = re.findall(r"\b\w+\b", text.lower())
        return words

    async def _analyze_sentence(
        self, sentence: str, extract_keywords: bool = True
    ) -> Dict[str, Any]:
        """Анализировать предложение"""
        words = self._tokenize_text(sentence)
        analyzed_words = []
        lemmas = []
        keywords = []

        for word in words:
            if word.strip():
                word_info = await self.analyze_word(word.strip())
                analyzed_words.append(word_info)
                lemmas.append(word_info["lemma"])

                # Извлекаем ключевые слова
                if extract_keywords and self._is_keyword(word_info):
                    keywords.append(word_info["lemma"])

        return {
            "text": sentence,
            "words": analyzed_words,
            "lemmas": lemmas,
            "keywords": keywords,
        }

    def _is_keyword(self, word_info: Dict[str, Any]) -> bool:
        """Проверить, является ли слово ключевым"""
        return word_info["pos"] in [
            POS_NOUN,
            POS_VERB,
            POS_ADJECTIVE,
            POS_ADVERB,
        ]

    async def _get_word_forms(self, word: str, lemma: str) -> List[str]:
        """Получить все формы слова"""
        try:
            # Пытаемся получить формы через анализатор
            forms = set()

            # Анализируем исходное слово
            parses = self.analyzer.parse(word)
            if parses:
                for parse in parses[:3]:  # Берем первые 3 разбора
                    if hasattr(parse, "lexeme"):
                        for lexeme in parse.lexeme:
                            if hasattr(lexeme, "word"):
                                forms.add(lexeme.word.lower())

            # Добавляем лемму
            forms.add(lemma.lower())

            # Если не удалось получить формы, возвращаем базовые
            if not forms:
                forms = {word.lower(), lemma.lower()}

            return sorted(list(forms))

        except Exception:
            # В случае ошибки возвращаем базовые формы
            return [word.lower(), lemma.lower()]

    async def _create_noun_patterns(
        self, word_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Создать паттерны для существительных"""
        patterns = []

        # Паттерны для разных падежей
        if "case" in word_info["features"]:
            case = word_info["features"]["case"]
            patterns.append(
                {
                    "pattern": word_info["lemma"],
                    "type": f"noun_{case.lower()}",
                    "description": f"Существительное в {case.lower()} падеже",
                }
            )

        return patterns

    async def _create_verb_patterns(
        self, word_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Создать паттерны для глаголов"""
        patterns = []

        # Паттерны для разных времен
        if "tense" in word_info["features"]:
            tense = word_info["features"]["tense"]
            patterns.append(
                {
                    "pattern": word_info["lemma"],
                    "type": f"verb_{tense.lower()}",
                    "description": f"Глагол в {tense.lower()} времени",
                }
            )

        return patterns

    async def _create_adjective_patterns(
        self, word_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Создать паттерны для прилагательных"""
        patterns = []

        # Паттерны для разных родов и чисел
        features = word_info["features"]
        if "gender" in features and "number" in features:
            gender = features["gender"]
            number = features["number"]
            patterns.append(
                {
                    "pattern": word_info["lemma"],
                    "type": f"adj_{gender.lower()}_{number.lower()}",
                    "description": f"Прилагательное {gender.lower()} рода, {number.lower()} числа",
                }
            )

        return patterns


# Экспорт
__all__ = [
    "MorphologicalService",
]
