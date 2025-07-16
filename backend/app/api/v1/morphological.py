"""
API endpoints для морфологического анализа ключевых слов
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.services.morphological_service import morphological_service

router = APIRouter(tags=["Morphological Analysis"])


@router.get("/word-forms/{word}")
async def get_word_forms(word: str) -> dict:
    """
    Получить все морфологические формы слова.

    Args:
        word: Слово для анализа

    Returns:
        Словарь с информацией о слове и его формах
    """
    try:
        word_info = morphological_service.get_word_info(word)
        return {
            "word": word,
            "info": word_info,
            "forms": morphological_service.get_search_patterns(word),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при анализе слова: {str(e)}",
        ) from e


@router.post("/analyze-text")
async def analyze_text_in_text(
    text: str,
    keyword: str,
    case_sensitive: bool = False,
    whole_word: bool = False,
) -> dict:
    """
    Найти все морфологические формы ключевого слова в тексте.

    Args:
        text: Текст для поиска
        keyword: Ключевое слово
        case_sensitive: Учитывать регистр
        whole_word: Искать только целые слова

    Returns:
        Словарь с найденными совпадениями
    """
    try:
        matches = morphological_service.find_morphological_matches(
            text=text,
            keyword=keyword,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
        )

        return {
            "text": text,
            "keyword": keyword,
            "case_sensitive": case_sensitive,
            "whole_word": whole_word,
            "matches": [
                {
                    "matched_text": match[0],
                    "position": match[1],
                    "context": _get_context(text, match[1], len(match[0])),
                }
                for match in matches
            ],
            "total_matches": len(matches),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске в тексте: {str(e)}",
        ) from e


@router.post("/analyze-multiple-keywords")
async def analyze_multiple_keywords_in_text(
    text: str,
    keywords: List[str],
    case_sensitive: bool = False,
    whole_word: bool = False,
) -> dict:
    """
    Найти все морфологические формы нескольких ключевых слов в тексте.

    Args:
        text: Текст для поиска
        keywords: Список ключевых слов
        case_sensitive: Учитывать регистр
        whole_word: Искать только целые слова

    Returns:
        Словарь с найденными совпадениями по каждому ключевому слову
    """
    try:
        results = {}
        total_matches = 0

        for keyword in keywords:
            matches = morphological_service.find_morphological_matches(
                text=text,
                keyword=keyword,
                case_sensitive=case_sensitive,
                whole_word=whole_word,
            )

            results[keyword] = {
                "matches": [
                    {
                        "matched_text": match[0],
                        "position": match[1],
                        "context": _get_context(text, match[1], len(match[0])),
                    }
                    for match in matches
                ],
                "total_matches": len(matches),
            }
            total_matches += len(matches)

        return {
            "text": text,
            "keywords": keywords,
            "case_sensitive": case_sensitive,
            "whole_word": whole_word,
            "results": results,
            "total_matches": total_matches,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске ключевых слов: {str(e)}",
        ) from e


def _get_context(
    text: str, position: int, word_length: int, context_length: int = 50
) -> str:
    """
    Получить контекст вокруг найденного слова.

    Args:
        text: Исходный текст
        position: Позиция найденного слова
        word_length: Длина найденного слова
        context_length: Длина контекста с каждой стороны

    Returns:
        Контекст вокруг найденного слова
    """
    start = max(0, position - context_length)
    end = min(len(text), position + word_length + context_length)

    context = text[start:end]

    # Добавляем многоточие, если обрезали текст
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."

    return context
