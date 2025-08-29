"""
Переделанный роутер morphological с новой архитектурой (DDD + Middleware)
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Request, Depends, Query
from ..application.morphological_service import MorphologicalApplicationService
from ..handlers.common import create_success_response, create_error_response


router = APIRouter(prefix="/morphological", tags=["Morphological Analysis"])


# Dependency для Morphological Service
def get_morphological_service() -> MorphologicalApplicationService:
    """Получить экземпляр Morphological Service"""
    return MorphologicalApplicationService()


@router.get(
    "/word/{word}",
    summary="Analyze Word",
    description="Проанализировать слово морфологически",
)
async def analyze_word(
    request: Request,
    word: str = Query(..., description="Слово для анализа"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Проанализировать слово"""
    try:
        word_info = await morphological_service.analyze_word(word)
        return await create_success_response(request, word_info.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "WORD_ANALYSIS_FAILED",
            f"Failed to analyze word '{word}': {str(e)}",
        )


@router.get(
    "/word/{word}/forms",
    summary="Get Word Forms",
    description="Получить все морфологические формы слова",
)
async def get_word_forms(
    request: Request,
    word: str = Query(..., description="Слово для анализа"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Получить формы слова"""
    try:
        forms = await morphological_service.get_search_patterns(word)
        return await create_success_response(
            request,
            {
                "word": word,
                "forms": forms,
                "count": len(forms),
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "FORMS_GENERATION_FAILED",
            f"Failed to generate forms for word '{word}': {str(e)}",
        )


@router.post(
    "/analyze-text",
    summary="Analyze Text",
    description="Проанализировать текст морфологически",
)
async def analyze_text(
    request: Request,
    text: str = Query(..., description="Текст для анализа"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Проанализировать текст"""
    try:
        result = await morphological_service.analyze_text(text)
        return await create_success_response(request, result.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "TEXT_ANALYSIS_FAILED",
            f"Failed to analyze text: {str(e)}",
        )


@router.post(
    "/search-pattern",
    summary="Create Search Pattern",
    description="Создать паттерн поиска с морфологическими формами",
)
async def create_search_pattern(
    request: Request,
    base_word: str = Query(..., description="Базовое слово"),
    case_sensitive: bool = Query(
        False, description="Чувствительность к регистру"
    ),
    whole_word: bool = Query(True, description="Искать как целое слово"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Создать паттерн поиска"""
    try:
        pattern = await morphological_service.create_search_pattern(
            base_word=base_word,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
        )
        return await create_success_response(request, pattern.to_dict())
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "PATTERN_CREATION_FAILED",
            f"Failed to create search pattern for '{base_word}': {str(e)}",
        )


@router.post(
    "/find-keywords",
    summary="Find Keywords in Text",
    description="Найти ключевые слова в тексте",
)
async def find_keywords_in_text(
    request: Request,
    text: str = Query(..., description="Текст для поиска"),
    keywords: List[str] = Query(..., description="Ключевые слова для поиска"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Найти ключевые слова в тексте"""
    try:
        result = await morphological_service.find_keywords_in_text(
            text, keywords
        )
        return await create_success_response(request, result)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "KEYWORDS_SEARCH_FAILED",
            f"Failed to find keywords in text: {str(e)}",
        )


@router.get(
    "/compare/{word1}/{word2}",
    summary="Compare Word Similarity",
    description="Сравнить схожесть двух слов",
)
async def compare_word_similarity(
    request: Request,
    word1: str = Query(..., description="Первое слово"),
    word2: str = Query(..., description="Второе слово"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Сравнить схожесть слов"""
    try:
        similarity = await morphological_service.compare_word_similarity(
            word1, word2
        )
        return await create_success_response(request, similarity)
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "SIMILARITY_COMPARISON_FAILED",
            f"Failed to compare words '{word1}' and '{word2}': {str(e)}",
        )


@router.get(
    "/variations/{word}",
    summary="Generate Word Variations",
    description="Генерировать вариации слова",
)
async def generate_word_variations(
    request: Request,
    word: str = Query(..., description="Базовое слово"),
    max_variations: int = Query(
        10, description="Максимальное количество вариаций"
    ),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Генерировать вариации слова"""
    try:
        variations = await morphological_service.generate_word_variations(
            word=word, max_variations=max_variations
        )
        return await create_success_response(
            request,
            {
                "word": word,
                "variations": variations,
                "count": len(variations),
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "VARIATIONS_GENERATION_FAILED",
            f"Failed to generate variations for word '{word}': {str(e)}",
        )


@router.post(
    "/batch/analyze",
    summary="Batch Analyze Words",
    description="Массовый анализ слов",
)
async def batch_analyze_words(
    request: Request,
    words: List[str] = Query(..., description="Список слов для анализа"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Массовый анализ слов"""
    try:
        results = []
        successful = 0
        failed = 0

        for word in words:
            try:
                word_info = await morphological_service.analyze_word(word)
                results.append(
                    {
                        "word": word,
                        "success": True,
                        "data": word_info.to_dict(),
                    }
                )
                successful += 1
            except Exception as e:
                results.append(
                    {
                        "word": word,
                        "success": False,
                        "error": str(e),
                    }
                )
                failed += 1

        return await create_success_response(
            request,
            {
                "results": results,
                "summary": {
                    "total": len(words),
                    "successful": successful,
                    "failed": failed,
                },
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "BATCH_ANALYSIS_FAILED",
            f"Failed to perform batch analysis: {str(e)}",
        )


@router.post(
    "/batch/forms",
    summary="Batch Get Word Forms",
    description="Массовое получение форм слов",
)
async def batch_get_word_forms(
    request: Request,
    words: List[str] = Query(..., description="Список слов"),
    morphological_service: MorphologicalApplicationService = Depends(
        get_morphological_service
    ),
) -> Dict[str, Any]:
    """Массовое получение форм слов"""
    try:
        results = []
        successful = 0
        failed = 0

        for word in words:
            try:
                forms = await morphological_service.get_search_patterns(word)
                results.append(
                    {
                        "word": word,
                        "success": True,
                        "forms": forms,
                        "count": len(forms),
                    }
                )
                successful += 1
            except Exception as e:
                results.append(
                    {
                        "word": word,
                        "success": False,
                        "error": str(e),
                    }
                )
                failed += 1

        return await create_success_response(
            request,
            {
                "results": results,
                "summary": {
                    "total": len(words),
                    "successful": successful,
                    "failed": failed,
                },
            },
        )
    except Exception as e:
        return await create_error_response(
            request,
            500,
            "BATCH_FORMS_FAILED",
            f"Failed to get batch forms: {str(e)}",
        )
