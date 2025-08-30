"""
FastAPI роутер для модуля Morphological

Определяет API эндпоинты для морфологического анализа текста
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from .dependencies import get_morphological_service
from .schemas import (
    WordAnalysisRequest,
    WordAnalysisResponse,
    WordFormsRequest,
    WordFormsResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
    SearchPatternRequest,
    SearchPatternResponse,
    MorphologicalStats,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    KeywordExtractionRequest,
    KeywordExtractionResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
)
from .service import MorphologicalService

router = APIRouter(
    prefix="/morphological",
    tags=["Morphological Analysis"],
    responses={
        400: {"description": "Bad request - invalid input"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable"},
    },
)


@router.post(
    "/analyze-word",
    response_model=WordAnalysisResponse,
    summary="Анализ слова",
    description="Проанализировать слово морфологически",
)
async def analyze_word(
    request: WordAnalysisRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> WordAnalysisResponse:
    """Анализировать слово"""
    try:
        word_info = await service.analyze_word(request.word)
        return WordAnalysisResponse(
            word_info=word_info,
            analysis_time=word_info.pop("analysis_time", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/word/{word}",
    response_model=WordAnalysisResponse,
    summary="Анализ слова (GET)",
    description="Проанализировать слово морфологически",
)
async def analyze_word_get(
    word: str,
    service: MorphologicalService = Depends(get_morphological_service),
) -> WordAnalysisResponse:
    """Анализировать слово (GET версия)"""
    try:
        word_info = await service.analyze_word(word)
        return WordAnalysisResponse(
            word_info=word_info,
            analysis_time=word_info.pop("analysis_time", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/word-forms",
    response_model=WordFormsResponse,
    summary="Формы слова",
    description="Получить все морфологические формы слова",
)
async def get_word_forms(
    request: WordFormsRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> WordFormsResponse:
    """Получить формы слова"""
    try:
        result = await service.get_word_forms(request.word)
        return WordFormsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/word/{word}/forms",
    response_model=WordFormsResponse,
    summary="Формы слова (GET)",
    description="Получить все морфологические формы слова",
)
async def get_word_forms_get(
    word: str,
    service: MorphologicalService = Depends(get_morphological_service),
) -> WordFormsResponse:
    """Получить формы слова (GET версия)"""
    try:
        result = await service.get_word_forms(word)
        return WordFormsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/analyze-text",
    response_model=TextAnalysisResponse,
    summary="Анализ текста",
    description="Проанализировать текст морфологически",
)
async def analyze_text(
    request: TextAnalysisRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> TextAnalysisResponse:
    """Анализировать текст"""
    try:
        result = await service.analyze_text(
            request.text, request.extract_keywords
        )
        return TextAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/search-patterns",
    response_model=SearchPatternResponse,
    summary="Паттерны поиска",
    description="Создать паттерны поиска для слова с учетом морфологии",
)
async def create_search_patterns(
    request: SearchPatternRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> SearchPatternResponse:
    """Создать паттерны поиска"""
    try:
        result = await service.create_search_patterns(
            request.base_word,
            case_sensitive=request.case_sensitive,
            whole_word=request.whole_word,
            include_forms=request.include_forms,
        )
        return SearchPatternResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/extract-keywords",
    response_model=KeywordExtractionResponse,
    summary="Извлечение ключевых слов",
    description="Извлечь ключевые слова из текста с учетом морфологии",
)
async def extract_keywords(
    request: KeywordExtractionRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> KeywordExtractionResponse:
    """Извлечь ключевые слова"""
    try:
        result = await service.extract_keywords(
            request.text,
            request.max_keywords,
            request.min_keyword_length,
            request.pos_filter,
        )
        return KeywordExtractionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/batch-analyze",
    response_model=BatchAnalysisResponse,
    summary="Пакетный анализ",
    description="Проанализировать несколько текстов одновременно",
)
async def batch_analyze(
    request: BatchAnalysisRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> BatchAnalysisResponse:
    """Пакетный анализ текстов"""
    try:
        result = await service.batch_analyze(
            request.texts, request.extract_keywords
        )
        return BatchAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/detect-language",
    response_model=LanguageDetectionResponse,
    summary="Определение языка",
    description="Определить язык текста",
)
async def detect_language(
    request: LanguageDetectionRequest,
    service: MorphologicalService = Depends(get_morphological_service),
) -> LanguageDetectionResponse:
    """Определить язык текста"""
    try:
        result = await service.detect_language(request.text)
        return LanguageDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats",
    response_model=MorphologicalStats,
    summary="Статистика анализа",
    description="Получить статистику морфологического анализа",
)
async def get_morphological_stats(
    service: MorphologicalService = Depends(get_morphological_service),
) -> MorphologicalStats:
    """Получить статистику анализа"""
    try:
        stats = await service.get_stats()
        return MorphologicalStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Проверка здоровья",
    description="Проверить доступность морфологического анализатора",
)
async def morphological_health_check(
    service: MorphologicalService = Depends(get_morphological_service),
):
    """Проверка здоровья анализатора"""
    try:
        stats = await service.get_stats()

        return {
            "status": "healthy",
            "analyzer_available": stats["analyzer_version"] != "fallback",
            "cache_size": stats["total_words_analyzed"],
            "supported_languages": stats["supported_languages"],
            "timestamp": "2024-01-01T00:00:00Z",  # В реальности datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "analyzer_available": False,
            "timestamp": "2024-01-01T00:00:00Z",
        }


@router.post(
    "/test-word/{word}",
    summary="Тестовый анализ слова",
    description="Тестовый анализ слова без сохранения результатов",
)
async def test_word_analysis(
    word: str,
    include_details: bool = Query(
        False, description="Включить детальную информацию"
    ),
    service: MorphologicalService = Depends(get_morphological_service),
):
    """Тестовый анализ слова"""
    try:
        result = await service.analyze_word(word)

        if not include_details:
            # Упрощенный ответ
            return {
                "word": result["word"],
                "lemma": result["lemma"],
                "pos": result["pos"],
                "analysis_time": result["analysis_time"],
            }

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/compare-words",
    summary="Сравнение слов",
    description="Сравнить морфологические характеристики двух слов",
)
async def compare_words(
    word1: str = Query(..., description="Первое слово"),
    word2: str = Query(..., description="Второе слово"),
    service: MorphologicalService = Depends(get_morphological_service),
):
    """Сравнить два слова"""
    try:
        analysis1 = await service.analyze_word(word1)
        analysis2 = await service.analyze_word(word2)

        # Сравниваем характеристики
        comparison = {
            "word1": {
                "word": analysis1["word"],
                "lemma": analysis1["lemma"],
                "pos": analysis1["pos"],
            },
            "word2": {
                "word": analysis2["word"],
                "lemma": analysis2["lemma"],
                "pos": analysis2["pos"],
            },
            "same_lemma": analysis1["lemma"] == analysis2["lemma"],
            "same_pos": analysis1["pos"] == analysis2["pos"],
            "analysis_time": analysis1["analysis_time"]
            + analysis2["analysis_time"],
        }

        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Экспорт роутера
__all__ = ["router"]
