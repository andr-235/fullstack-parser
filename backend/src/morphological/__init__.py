"""
Модуль морфологического анализа текста

Простой и эффективный модуль для анализа русских текстов с использованием pymorphy2
"""

from .service import MorphologicalService
from .schemas import (
    WordAnalysisRequest,
    WordAnalysisResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
    KeywordExtractionRequest,
    KeywordExtractionResponse,
)
from .router import router

__all__ = [
    "MorphologicalService",
    "WordAnalysisRequest",
    "WordAnalysisResponse", 
    "TextAnalysisRequest",
    "TextAnalysisResponse",
    "KeywordExtractionRequest",
    "KeywordExtractionResponse",
    "router",
]
