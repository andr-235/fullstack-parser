"""
Domain сущности для системы морфологического анализа (DDD)
"""

from typing import Dict, Any, List, Optional
from .base import ValueObject


class WordInfo(ValueObject):
    """Информация о слове"""

    def __init__(
        self,
        word: str,
        lemma: str,
        pos: str,  # part of speech
        features: Optional[Dict[str, str]] = None,
        forms: Optional[List[str]] = None,
    ):
        self.word = word.lower()
        self.lemma = lemma.lower()
        self.pos = pos
        self.features = features or {}
        self.forms = forms or []

    def is_noun(self) -> bool:
        """Проверить, является ли существительным"""
        return self.pos == "NOUN"

    def is_verb(self) -> bool:
        """Проверить, является ли глаголом"""
        return self.pos == "VERB"

    def is_adjective(self) -> bool:
        """Проверить, является ли прилагательным"""
        return self.pos == "ADJ"

    def get_case(self) -> Optional[str]:
        """Получить падеж (для существительных)"""
        return self.features.get("Case")

    def get_number(self) -> Optional[str]:
        """Получить число"""
        return self.features.get("Number")

    def get_gender(self) -> Optional[str]:
        """Получить род (для существительных и прилагательных)"""
        return self.features.get("Gender")

    def get_tense(self) -> Optional[str]:
        """Получить время (для глаголов)"""
        return self.features.get("Tense")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "word": self.word,
            "lemma": self.lemma,
            "pos": self.pos,
            "features": self.features,
            "forms": self.forms,
        }


class MorphologicalPattern(ValueObject):
    """Морфологический паттерн для поиска"""

    def __init__(
        self,
        lemma: str,
        pos: str,
        patterns: Optional[List[str]] = None,
        include_forms: bool = True,
    ):
        self.lemma = lemma.lower()
        self.pos = pos
        self.patterns = patterns or []
        self.include_forms = include_forms

    def add_pattern(self, pattern: str) -> None:
        """Добавить паттерн поиска"""
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def generate_patterns(self, word_info: WordInfo) -> List[str]:
        """Генерировать паттерны на основе информации о слове"""
        patterns = []

        # Базовая лемма
        patterns.append(self.lemma)

        if self.include_forms:
            # Все формы слова
            patterns.extend(word_info.forms)

            # Дополнительные паттерны для разных частей речи
            if word_info.is_noun():
                patterns.extend(self._generate_noun_patterns(word_info))
            elif word_info.is_verb():
                patterns.extend(self._generate_verb_patterns(word_info))
            elif word_info.is_adjective():
                patterns.extend(self._generate_adjective_patterns(word_info))

        # Удалить дубликаты и отсортировать
        unique_patterns = list(set(patterns))
        unique_patterns.sort()

        self.patterns = unique_patterns
        return self.patterns

    def _generate_noun_patterns(self, word_info: WordInfo) -> List[str]:
        """Генерировать паттерны для существительных"""
        patterns = []

        # Родительный падеж часто используется в поиске
        if word_info.get_case() == "Gen":
            patterns.append(word_info.word)

        # Множественное число
        if word_info.get_number() == "Plur":
            patterns.append(word_info.word)

        return patterns

    def _generate_verb_patterns(self, word_info: WordInfo) -> List[str]:
        """Генерировать паттерны для глаголов"""
        patterns = []

        # Инфинитив часто используется в поиске
        if (
            "VerbForm" in word_info.features
            and word_info.features["VerbForm"] == "Inf"
        ):
            patterns.append(word_info.word)

        # Разные времена
        tense = word_info.get_tense()
        if tense:
            patterns.append(word_info.word)

        return patterns

    def _generate_adjective_patterns(self, word_info: WordInfo) -> List[str]:
        """Генерировать паттерны для прилагательных"""
        patterns = []

        # Краткая форма
        if (
            "Variant" in word_info.features
            and word_info.features["Variant"] == "Short"
        ):
            patterns.append(word_info.word)

        return patterns

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "lemma": self.lemma,
            "pos": self.pos,
            "patterns": self.patterns,
            "include_forms": self.include_forms,
        }


class TextAnalysisResult(ValueObject):
    """Результат анализа текста"""

    def __init__(
        self,
        text: str,
        words: Optional[List[WordInfo]] = None,
        sentences: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        lemmas: Optional[List[str]] = None,
    ):
        self.text = text
        self.words = words or []
        self.sentences = sentences or []
        self.keywords = keywords or []
        self.lemmas = lemmas or []

    def add_word(self, word_info: WordInfo) -> None:
        """Добавить информацию о слове"""
        self.words.append(word_info)

    def add_keyword(self, keyword: str) -> None:
        """Добавить ключевое слово"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)

    def get_unique_lemmas(self) -> List[str]:
        """Получить уникальные леммы"""
        unique_lemmas = list(set(self.lemmas))
        unique_lemmas.sort()
        return unique_lemmas

    def get_pos_distribution(self) -> Dict[str, int]:
        """Получить распределение частей речи"""
        distribution = {}
        for word in self.words:
            pos = word.pos
            distribution[pos] = distribution.get(pos, 0) + 1
        return distribution

    def get_most_common_lemmas(self, limit: int = 10) -> List[tuple]:
        """Получить наиболее частые леммы"""
        lemma_counts = {}
        for lemma in self.lemmas:
            lemma_counts[lemma] = lemma_counts.get(lemma, 0) + 1

        sorted_lemmas = sorted(
            lemma_counts.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_lemmas[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "text": self.text,
            "word_count": len(self.words),
            "sentence_count": len(self.sentences),
            "keywords": self.keywords,
            "unique_lemmas": self.get_unique_lemmas(),
            "pos_distribution": self.get_pos_distribution(),
            "most_common_lemmas": self.get_most_common_lemmas(),
            "words": [word.to_dict() for word in self.words],
        }


class SearchPattern(ValueObject):
    """Паттерн поиска с морфологическими формами"""

    def __init__(
        self,
        base_word: str,
        patterns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        whole_word: bool = True,
    ):
        self.base_word = base_word
        self.patterns = patterns or [base_word]
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word

    def add_pattern(self, pattern: str) -> None:
        """Добавить паттерн поиска"""
        if pattern not in self.patterns:
            self.patterns.append(pattern)

    def get_regex_pattern(self) -> str:
        """Получить регулярное выражение для поиска"""
        if self.whole_word:
            # Искать как целое слово
            word_patterns = []
            for pattern in self.patterns:
                if self.case_sensitive:
                    word_patterns.append(rf"\b{pattern}\b")
                else:
                    word_patterns.append(rf"\b{pattern}\b(?i)")
            return "|".join(word_patterns)
        else:
            # Искать как подстроку
            if self.case_sensitive:
                return "|".join(self.patterns)
            else:
                return "|".join(
                    [f"(?i:{pattern})" for pattern in self.patterns]
                )

    def matches(self, text: str) -> bool:
        """Проверить, соответствует ли текст паттерну"""
        import re

        pattern = self.get_regex_pattern()
        return bool(re.search(pattern, text))

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "base_word": self.base_word,
            "patterns": self.patterns,
            "case_sensitive": self.case_sensitive,
            "whole_word": self.whole_word,
            "regex_pattern": self.get_regex_pattern(),
        }
