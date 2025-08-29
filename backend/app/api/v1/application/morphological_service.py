"""
Application Service для системы морфологического анализа (DDD)
"""

from typing import List, Dict, Any, Optional
from ..domain.morphological import (
    WordInfo,
    MorphologicalPattern,
    TextAnalysisResult,
    SearchPattern,
)
from .base import ApplicationService


class MorphologicalApplicationService(ApplicationService):
    """Application Service для морфологического анализа"""

    def __init__(self, morphological_analyzer=None):
        self.morphological_analyzer = morphological_analyzer

    async def analyze_word(self, word: str) -> WordInfo:
        """Проанализировать слово"""
        if not self.morphological_analyzer:
            raise ValueError("Morphological analyzer not configured")

        try:
            # Получить морфологическую информацию
            analysis_result = self.morphological_analyzer.parse(word)

            if not analysis_result:
                # Если анализатор не смог разобрать слово, вернуть базовую информацию
                return WordInfo(
                    word=word,
                    lemma=word.lower(),
                    pos="UNKNOWN",
                    features={},
                    forms=[word.lower()],
                )

            # Взять первый наиболее вероятный разбор
            best_parse = analysis_result[0]

            # Извлечь информацию
            lemma = getattr(best_parse, "normal_form", word.lower())
            pos = getattr(best_parse, "POS", "UNKNOWN")

            # Извлечь морфологические признаки
            features = {}
            if hasattr(best_parse, "tag"):
                tag = best_parse.tag
                # Преобразовать теги в словарь
                for attr in [
                    "Case",
                    "Number",
                    "Gender",
                    "Tense",
                    "Person",
                    "Aspect",
                ]:
                    if hasattr(tag, attr):
                        value = getattr(tag, attr)
                        if value:
                            features[attr] = str(value)

            # Получить все формы слова
            forms = self._get_word_forms(word, lemma)

            return WordInfo(
                word=word,
                lemma=lemma,
                pos=pos,
                features=features,
                forms=forms,
            )

        except Exception as e:
            # В случае ошибки вернуть базовую информацию
            return WordInfo(
                word=word,
                lemma=word.lower(),
                pos="UNKNOWN",
                features={"error": str(e)},
                forms=[word.lower()],
            )

    async def get_search_patterns(self, word: str) -> List[str]:
        """Получить паттерны поиска для слова"""
        word_info = await self.analyze_word(word)

        # Создать морфологический паттерн
        pattern = MorphologicalPattern(
            lemma=word_info.lemma,
            pos=word_info.pos,
            include_forms=True,
        )

        # Генерировать паттерны
        patterns = pattern.generate_patterns(word_info)

        return patterns

    async def analyze_text(self, text: str) -> TextAnalysisResult:
        """Проанализировать текст"""
        if not self.morphological_analyzer:
            raise ValueError("Morphological analyzer not configured")

        result = TextAnalysisResult(text=text)

        try:
            # Разбить текст на предложения (упрощенная версия)
            sentences = self._split_into_sentences(text)
            result.sentences = sentences

            # Анализировать каждое слово
            words = self._tokenize_text(text)
            lemmas = []

            for word in words:
                if word.strip():  # Пропустить пустые строки
                    word_info = await self.analyze_word(word.strip())
                    result.add_word(word_info)
                    lemmas.append(word_info.lemma)

                    # Определить ключевые слова (существительные и прилагательные)
                    if word_info.is_noun() or word_info.is_adjective():
                        result.add_keyword(word_info.lemma)

            result.lemmas = lemmas

        except Exception as e:
            # В случае ошибки добавить информацию об ошибке
            error_word = WordInfo(
                word="ERROR",
                lemma="error",
                pos="UNKNOWN",
                features={"error": str(e)},
                forms=["error"],
            )
            result.add_word(error_word)

        return result

    async def create_search_pattern(
        self,
        base_word: str,
        case_sensitive: bool = False,
        whole_word: bool = True,
    ) -> SearchPattern:
        """Создать паттерн поиска"""
        word_info = await self.analyze_word(base_word)

        # Создать паттерн
        search_pattern = SearchPattern(
            base_word=base_word,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
        )

        # Добавить морфологические формы
        if word_info.forms:
            for form in word_info.forms:
                search_pattern.add_pattern(form)

        return search_pattern

    async def find_keywords_in_text(
        self, text: str, keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Найти ключевые слова в тексте"""
        result = {
            "found_keywords": [],
            "not_found_keywords": [],
            "matches": {},
        }

        # Создать паттерны поиска для каждого ключевого слова
        search_patterns = []
        for keyword in keywords:
            pattern = await self.create_search_pattern(keyword)
            search_patterns.append((keyword, pattern))

        # Искать каждое ключевое слово
        for keyword, pattern in search_patterns:
            if pattern.matches(text):
                result["found_keywords"].append(keyword)
                result["matches"][keyword] = pattern.patterns
            else:
                result["not_found_keywords"].append(keyword)

        return result

    async def compare_word_similarity(
        self, word1: str, word2: str
    ) -> Dict[str, Any]:
        """Сравнить схожесть слов"""
        word1_info = await self.analyze_word(word1)
        word2_info = await self.analyze_word(word2)

        similarity = {
            "word1": word1_info.to_dict(),
            "word2": word2_info.to_dict(),
            "same_lemma": word1_info.lemma == word2_info.lemma,
            "same_pos": word1_info.pos == word2_info.pos,
            "shared_features": {},
            "similarity_score": 0.0,
        }

        # Рассчитать схожесть
        score = 0.0

        if word1_info.lemma == word2_info.lemma:
            score += 0.5

        if word1_info.pos == word2_info.pos:
            score += 0.3

        # Проверить общие морфологические признаки
        shared_features = {}
        for feature in ["Case", "Number", "Gender"]:
            if (
                feature in word1_info.features
                and feature in word2_info.features
                and word1_info.features[feature]
                == word2_info.features[feature]
            ):
                shared_features[feature] = word1_info.features[feature]
                score += 0.1

        similarity["shared_features"] = shared_features
        similarity["similarity_score"] = min(score, 1.0)

        return similarity

    async def generate_word_variations(
        self, word: str, max_variations: int = 10
    ) -> List[str]:
        """Генерировать вариации слова"""
        word_info = await self.analyze_word(word)

        variations = []

        # Добавить лемму
        variations.append(word_info.lemma)

        # Добавить все формы
        variations.extend(word_info.forms)

        # Добавить дополнительные вариации для существительных
        if word_info.is_noun():
            variations.extend(self._generate_noun_variations(word_info))

        # Добавить дополнительные вариации для глаголов
        elif word_info.is_verb():
            variations.extend(self._generate_verb_variations(word_info))

        # Удалить дубликаты и ограничить количество
        unique_variations = list(set(variations))
        return unique_variations[:max_variations]

    def _get_word_forms(self, word: str, lemma: str) -> List[str]:
        """Получить формы слова"""
        forms = [word.lower(), lemma]

        try:
            if self.morphological_analyzer:
                # Получить все возможные формы
                inflected = self.morphological_analyzer.inflect(word)
                if inflected:
                    for form in inflected:
                        forms.append(str(form).lower())
        except Exception:
            pass

        return list(set(forms))  # Удалить дубликаты

    def _split_into_sentences(self, text: str) -> List[str]:
        """Разбить текст на предложения (упрощенная версия)"""
        import re

        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _tokenize_text(self, text: str) -> List[str]:
        """Токенизировать текст (упрощенная версия)"""
        import re

        # Разбить на слова, убрать пунктуацию
        words = re.findall(r"\b\w+\b", text.lower())
        return words

    def _generate_noun_variations(self, word_info: WordInfo) -> List[str]:
        """Генерировать вариации для существительных"""
        variations = []

        # Добавить форму множественного числа
        if word_info.get_number() == "Sing":
            # Попытаться получить множественное число
            try:
                plural = self.morphological_analyzer.inflect(
                    word_info.word, ["plur"]
                )
                if plural:
                    variations.append(str(plural[0]).lower())
            except Exception:
                pass

        return variations

    def _generate_verb_variations(self, word_info: WordInfo) -> List[str]:
        """Генерировать вариации для глаголов"""
        variations = []

        # Добавить различные формы глагола
        try:
            # Настоящее время
            present = self.morphological_analyzer.inflect(
                word_info.word, ["pres"]
            )
            if present:
                variations.append(str(present[0]).lower())

            # Прошедшее время
            past = self.morphological_analyzer.inflect(
                word_info.word, ["past"]
            )
            if past:
                variations.append(str(past[0]).lower())

        except Exception:
            pass

        return variations
