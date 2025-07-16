"""
Сервис для морфологического анализа ключевых слов
"""

import re
from functools import lru_cache
from typing import List, Set, Tuple

import pymorphy2


class MorphologicalService:
    """
    Сервис для морфологического анализа русских слов.

    Использует pymorphy2 для лемматизации и получения всех возможных
    морфологических форм слова.
    """

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def get_word_forms(self, word: str) -> Set[str]:
        """
        Получить все возможные морфологические формы слова.

        Args:
            word: Исходное слово

        Returns:
            Множество всех возможных форм слова
        """
        forms = set()

        # Добавляем исходное слово
        forms.add(word.lower())

        # Получаем все возможные формы через pymorphy2
        parsed_word = self.morph.parse(word.lower())

        for parse in parsed_word:
            # Добавляем нормальную форму (лемму)
            forms.add(parse.normal_form)

            # Добавляем все возможные формы слова
            for form in parse.lexeme:
                forms.add(form.word.lower())

        return forms

    def get_search_patterns(self, keyword: str) -> List[str]:
        """
        Получить список паттернов для поиска ключевого слова.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Список паттернов для поиска
        """
        word_forms = self.get_word_forms(keyword)
        return list(word_forms)

    def find_morphological_matches(
        self,
        text: str,
        keyword: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> List[Tuple[str, int]]:
        """
        Найти все морфологические формы ключевого слова в тексте.

        Args:
            text: Текст для поиска
            keyword: Ключевое слово
            case_sensitive: Учитывать регистр
            whole_word: Искать только целые слова

        Returns:
            Список кортежей (найденное_слово, позиция)
        """
        matches = []
        word_forms = self.get_word_forms(keyword)

        search_text = text if case_sensitive else text.lower()

        for form in word_forms:
            search_form = form if case_sensitive else form.lower()

            if whole_word:
                # Поиск целых слов с границами
                pattern = r"\b" + re.escape(search_form) + r"\b"
                flags = re.IGNORECASE if not case_sensitive else 0

                for match in re.finditer(pattern, search_text, flags):
                    matches.append((match.group(0), match.start()))
            else:
                # Поиск подстрок
                pos = 0
                while True:
                    pos = search_text.find(search_form, pos)
                    if pos == -1:
                        break
                    matches.append((search_form, pos))
                    pos += 1

        # Убираем дубликаты и сортируем по позиции
        unique_matches = []
        seen_positions = set()

        for word, pos in sorted(matches, key=lambda x: x[1]):
            if pos not in seen_positions:
                unique_matches.append((word, pos))
                seen_positions.add(pos)

        return unique_matches

    def is_russian_word(self, word: str) -> bool:
        """
        Проверить, является ли слово русским.

        Args:
            word: Слово для проверки

        Returns:
            True, если слово русское
        """
        # Простая проверка на наличие русских букв
        russian_pattern = re.compile(r"[а-яё]", re.IGNORECASE)
        return bool(russian_pattern.search(word))

    def normalize_word(self, word: str) -> str:
        """
        Нормализовать слово (привести к лемме).

        Args:
            word: Исходное слово

        Returns:
            Нормализованная форма слова
        """
        if not self.is_russian_word(word):
            return word.lower()

        parsed = self.morph.parse(word.lower())
        if parsed:
            return parsed[0].normal_form
        return word.lower()

    def get_word_info(self, word: str) -> dict:
        """
        Получить информацию о слове.

        Args:
            word: Слово для анализа

        Returns:
            Словарь с информацией о слове
        """
        if not self.is_russian_word(word):
            return {
                "normal_form": word.lower(),
                "forms": [word.lower()],
                "is_russian": False,
            }

        parsed = self.morph.parse(word.lower())
        if not parsed:
            return {
                "normal_form": word.lower(),
                "forms": [word.lower()],
                "is_russian": True,
                "analysis_failed": True,
            }

        # Получаем все формы
        all_forms = set()
        normal_form = parsed[0].normal_form

        for parse in parsed:
            for form in parse.lexeme:
                all_forms.add(form.word.lower())

        return {
            "normal_form": normal_form,
            "forms": list(all_forms),
            "is_russian": True,
            "part_of_speech": parsed[0].tag.POS if parsed[0].tag.POS else None,
            "grammar_info": str(parsed[0].tag),
        }


# Глобальный экземпляр сервиса
morphological_service = MorphologicalService()
