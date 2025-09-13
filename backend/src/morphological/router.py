"""
FastAPI роутер для морфологического анализа
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from .service import MorphologicalService
from .schemas import (
    WordAnalysisRequest,
    WordAnalysisResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
    KeywordExtractionRequest,
    KeywordExtractionResponse,
    LanguageDetectionRequest,
    LanguageDetectionResponse,
    MorphologicalStats,
)

router = APIRouter(
    prefix="/morphological",
    tags=["Morphological Analysis"],
    responses={
        400: {"description": "Bad request - invalid input"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


def get_morphological_service() -> MorphologicalService:
    """Получить сервис морфологического анализа"""
    return MorphologicalService()


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
        result = await service.analyze_text(request.text, request.extract_keywords)
        return TextAnalysisResponse(**result)
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
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "analyzer_available": False,
        }