"""
Сервис морфологического анализа текста
"""

import time
import re
from typing import List, Optional, Dict, Any
from collections import Counter

from shared.presentation.exceptions import ValidationException, InternalServerException


class MorphologicalService:
    """Сервис для морфологического анализа текста"""

    def __init__(self):
        self._analyzer = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "words_analyzed": 0,
            "texts_analyzed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    @property
    def analyzer(self):
        """Ленивая инициализация анализатора"""
        if self._analyzer is None:
            try:
                import pymorphy2
                self._analyzer = pymorphy2.MorphAnalyzer()
            except ImportError:
                self._analyzer = self._create_fallback_analyzer()
        return self._analyzer

    def _create_fallback_analyzer(self):
        """Создать заглушку анализатора"""
        class FallbackAnalyzer:
            def parse(self, word):
                class MockParse:
                    def __init__(self, word):
                        self.word = word
                        self.normal_form = word.lower()
                        self.POS = "UNKNOWN"
                        self.tag = None
                return [MockParse(word)]
        return FallbackAnalyzer()

    async def analyze_word(self, word: str) -> Dict[str, Any]:
        """Анализировать слово морфологически"""
        if not word or not word.strip():
            raise ValidationException("Слово не может быть пустым", field="word")

        word = word.strip()
        if len(word) > 100:
            raise ValidationException("Слово слишком длинное (макс 100 символов)", field="word")

        # Проверяем кеш
        cache_key = f"word:{word.lower()}"
        if cache_key in self._cache:
            self._stats["cache_hits"] += 1
            return self._cache[cache_key]

        self._stats["cache_misses"] += 1
        start_time = time.time()

        try:
            parses = self.analyzer.parse(word)
            
            if not parses:
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
                best_parse = parses[0]
                lemma = getattr(best_parse, "normal_form", word.lower())
                pos = getattr(best_parse, "POS", "UNKNOWN")

                # Извлекаем морфологические признаки
                features = {}
                if hasattr(best_parse, "tag") and best_parse.tag:
                    tag = best_parse.tag
                    feature_mapping = {
                        "case": "Case", "number": "Number", "gender": "Gender",
                        "tense": "Tense", "person": "Person", "aspect": "Aspect",
                        "voice": "Voice", "mood": "Mood",
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
            self._stats["words_analyzed"] += 1
            return result

        except Exception as e:
            raise InternalServerException(f"Ошибка анализа слова '{word}': {str(e)}")

    async def analyze_text(self, text: str, extract_keywords: bool = True) -> Dict[str, Any]:
        """Анализировать текст морфологически"""
        if not text or not text.strip():
            raise ValidationException("Текст не может быть пустым", field="text")

        text = text.strip()
        if len(text) > 10000:
            raise ValidationException("Текст слишком длинный (макс 10000 символов)", field="text")

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
                sentence_analysis = await self._analyze_sentence(sentence_text, extract_keywords)
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

            self._stats["texts_analyzed"] += 1
            return result

        except Exception as e:
            raise InternalServerException(f"Ошибка анализа текста: {str(e)}")

    async def extract_keywords(
        self,
        text: str,
        max_keywords: int = 20,
        min_length: int = 3,
        pos_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Извлечь ключевые слова из текста"""
        text_analysis = await self.analyze_text(text, extract_keywords=True)
        
        # Фильтруем слова по критериям
        candidate_keywords = []
        for word_info in text_analysis["words"]:
            if len(word_info["word"]) < min_length:
                continue
            if pos_filter and word_info["pos"] not in pos_filter:
                continue
            if word_info["pos"] not in ["NOUN", "VERB", "ADJ", "ADV"]:
                continue
            candidate_keywords.append(word_info)

        # Считаем частоту лемм
        lemma_counts = Counter(word["lemma"] for word in candidate_keywords)

        # Создаем список ключевых слов
        keywords = []
        for lemma, count in lemma_counts.most_common(max_keywords):
            word_info = next((w for w in candidate_keywords if w["lemma"] == lemma), None)
            if word_info:
                keywords.append({
                    "word": word_info["word"],
                    "lemma": lemma,
                    "pos": word_info["pos"],
                    "frequency": count,
                    "weight": float(count) / len(candidate_keywords),
                })

        return {
            "text": text,
            "keywords": keywords,
            "total_words": text_analysis["word_count"],
            "keyword_count": len(keywords),
            "extraction_time": text_analysis["analysis_time"],
        }

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Определить язык текста"""
        # Простая эвристика для определения русского языка
        cyrillic_chars = sum(1 for char in text if "\u0400" <= char <= "\u04FF")
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
            "supported_languages": ["ru", "en", "unknown"],
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику морфологического анализа"""
        total_requests = self._stats["cache_hits"] + self._stats["cache_misses"]
        cache_hit_rate = self._stats["cache_hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "total_words_analyzed": self._stats["words_analyzed"],
            "total_texts_analyzed": self._stats["texts_analyzed"],
            "cache_hit_rate": cache_hit_rate,
            "average_analysis_time": 0.05,  # Заглушка
            "supported_languages": ["ru", "en", "unknown"],
            "analyzer_version": "pymorphy2" if self._analyzer else "fallback",
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """Разбить текст на предложения"""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _tokenize_text(self, text: str) -> List[str]:
        """Разбить текст на слова"""
        words = re.findall(r"\b\w+\b", text.lower())
        return words

    async def _analyze_sentence(self, sentence: str, extract_keywords: bool = True) -> Dict[str, Any]:
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
        return word_info["pos"] in ["NOUN", "VERB", "ADJ", "ADV"]

    async def _get_word_forms(self, word: str, lemma: str) -> List[str]:
        """Получить все формы слова"""
        try:
            forms = set()
            parses = self.analyzer.parse(word)
            
            if parses:
                for parse in parses[:3]:  # Берем первые 3 разбора
                    if hasattr(parse, "lexeme"):
                        for lexeme in parse.lexeme:
                            if hasattr(lexeme, "word"):
                                forms.add(lexeme.word.lower())

            forms.add(lemma.lower())
            
            if not forms:
                forms = {word.lower(), lemma.lower()}

            return sorted(list(forms))

        except Exception:
            return [word.lower(), lemma.lower()]