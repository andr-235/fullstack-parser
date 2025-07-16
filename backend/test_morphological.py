#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации морфологического анализа ключевых слов
"""

import os
import sys

# Добавляем путь к модулям приложения
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.morphological_service import morphological_service


def test_word_forms():
    """Тестирование получения морфологических форм слов"""
    print("🔍 Тестирование морфологического анализа слов")
    print("=" * 60)

    test_words = [
        "спам",
        "реклама",
        "мошенничество",
        "взлом",
        "пароль",
        "компьютер",
        "программа",
        "система",
    ]

    for word in test_words:
        print(f"\n📝 Слово: '{word}'")
        word_info = morphological_service.get_word_info(word)

        print(f"   Нормальная форма: {word_info['normal_form']}")
        print(
            f"   Часть речи: {word_info.get('part_of_speech', 'не определено')}"
        )
        print(f"   Русское слово: {word_info['is_russian']}")

        forms = morphological_service.get_search_patterns(word)
        print(f"   Всего форм: {len(forms)}")
        print(
            f"   Формы: {', '.join(forms[:10])}{'...' if len(forms) > 10 else ''}"
        )


def test_text_search():
    """Тестирование поиска ключевых слов в тексте"""
    print("\n\n🔍 Тестирование поиска в тексте")
    print("=" * 60)

    # Тестовый текст с различными формами слов
    test_text = """
    В этой группе много спама и рекламы. Спамщики постоянно
    отправляют спамные сообщения. Рекламщики размещают рекламные
    посты. Мошенники пытаются обмануть людей мошенническими схемами.
    Хакеры взламывают аккаунты и крадут пароли. Программисты
    пишут программы для компьютерных систем.
    """

    test_keywords = ["спам", "реклама", "мошенничество", "взлом", "пароль"]

    print("📄 Текст для анализа:")
    print(f"'{test_text.strip()}'")

    for keyword in test_keywords:
        print(f"\n🔍 Поиск слова '{keyword}':")

        # Поиск с морфологическим анализом
        matches = morphological_service.find_morphological_matches(
            text=test_text,
            keyword=keyword,
            case_sensitive=False,
            whole_word=True,
        )

        if matches:
            print(f"   Найдено совпадений: {len(matches)}")
            for i, (matched_text, position) in enumerate(matches, 1):
                # Получаем контекст
                start = max(0, position - 20)
                end = min(len(test_text), position + len(matched_text) + 20)
                context = test_text[start:end]
                if start > 0:
                    context = "..." + context
                if end < len(test_text):
                    context = context + "..."

                print(f"   {i}. '{matched_text}' (позиция {position})")
                print(f"      Контекст: '{context.strip()}'")
        else:
            print("   Совпадений не найдено")


def test_comparison():
    """Сравнение старого и нового алгоритма поиска"""
    print("\n\n⚖️ Сравнение алгоритмов поиска")
    print("=" * 60)

    test_text = "Спамщики отправляют спамные сообщения. Рекламщики размещают рекламные посты."
    keyword = "спам"

    print(f"📄 Текст: '{test_text}'")
    print(f"🔍 Ключевое слово: '{keyword}'")

    # Старый алгоритм (простой поиск подстроки)
    old_matches = []
    text_lower = test_text.lower()
    keyword_lower = keyword.lower()

    pos = 0
    while True:
        pos = text_lower.find(keyword_lower, pos)
        if pos == -1:
            break
        old_matches.append((keyword_lower, pos))
        pos += 1

    # Новый алгоритм (морфологический анализ)
    new_matches = morphological_service.find_morphological_matches(
        text=test_text, keyword=keyword, case_sensitive=False, whole_word=True
    )

    print("\n📊 Результаты сравнения:")
    print(f"   Старый алгоритм: {len(old_matches)} совпадений")
    for match in old_matches:
        print(f"     - '{match[0]}' (позиция {match[1]})")

    print(f"   Новый алгоритм: {len(new_matches)} совпадений")
    for match in new_matches:
        print(f"     - '{match[0]}' (позиция {match[1]})")

    print(
        f"\n✅ Улучшение: новый алгоритм нашел на {len(new_matches) - len(old_matches)} совпадений больше!"
    )


def test_performance():
    """Тестирование производительности"""
    print("\n\n⚡ Тестирование производительности")
    print("=" * 60)

    import time

    # Генерируем большой текст
    base_text = "Спамщики отправляют спамные сообщения. Рекламщики размещают рекламные посты. "
    large_text = base_text * 1000  # ~50KB текста

    keywords = ["спам", "реклама", "мошенничество", "взлом", "пароль"]

    print(f"📄 Размер текста: {len(large_text)} символов")
    print(f"🔍 Количество ключевых слов: {len(keywords)}")

    # Тестируем производительность
    start_time = time.time()

    for keyword in keywords:
        morphological_service.find_morphological_matches(
            text=large_text,
            keyword=keyword,
            case_sensitive=False,
            whole_word=True,
        )

    end_time = time.time()
    processing_time = end_time - start_time

    print(f"⏱️ Время обработки: {processing_time:.3f} секунд")
    print(f"📈 Скорость: {len(large_text) / processing_time:.0f} символов/сек")


def main():
    """Главная функция тестирования"""
    print("🚀 Демонстрация морфологического анализа ключевых слов")
    print("=" * 80)

    try:
        test_word_forms()
        test_text_search()
        test_comparison()
        test_performance()

        print("\n\n✅ Все тесты завершены успешно!")
        print("\n📋 Примеры использования:")
        print("   - GET /api/v1/morphological/word-forms/спам")
        print("   - POST /api/v1/morphological/analyze-text")
        print("   - POST /api/v1/morphological/analyze-multiple-keywords")

    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
