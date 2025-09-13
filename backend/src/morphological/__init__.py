"""
Модуль морфологического анализа текста

Простой и эффективный модуль для анализа русских текстов с использованием pymorphy2
"""

from .router import router
from .schemas import (
    KeywordExtractionRequest,
    KeywordExtractionResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
    WordAnalysisRequest,
    WordAnalysisResponse,
)
from .service import MorphologicalService

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
