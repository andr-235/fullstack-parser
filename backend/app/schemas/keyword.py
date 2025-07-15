"""
Pydantic схемы для ключевых слов
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class KeywordBase(BaseModel):
    """Базовая схема ключевого слова"""

    word: str = Field(
        ..., min_length=1, max_length=200, description="Ключевое слово"
    )
    category: Optional[str] = Field(
        None, max_length=100, description="Категория ключевого слова"
    )
    description: Optional[str] = Field(
        None, description="Описание ключевого слова"
    )
    is_active: bool = Field(
        default=True, description="Активно ли ключевое слово"
    )
    is_case_sensitive: bool = Field(
        default=False, description="Учитывать регистр"
    )
    is_whole_word: bool = Field(
        default=False, description="Искать только целые слова"
    )


class KeywordCreate(KeywordBase):
    """Схема для создания ключевого слова"""

    pass


class KeywordUpdate(BaseModel):
    """Схема для обновления ключевого слова"""

    word: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_case_sensitive: Optional[bool] = None
    is_whole_word: Optional[bool] = None


class KeywordResponse(KeywordBase, IDMixin, TimestampMixin, BaseSchema):
    """Схема ответа ключевого слова"""

    total_matches: int = Field(
        default=0, description="Общее количество совпадений"
    )


class KeywordUploadResponse(BaseModel):
    """Схема ответа при загрузке ключевых слов из файла"""

    status: str = Field(description="Статус операции")
    message: str = Field(description="Сообщение о результате")
    total_processed: int = Field(description="Общее количество обработанных строк")
    created: int = Field(description="Количество созданных ключевых слов")
    skipped: int = Field(description="Количество пропущенных (дубликатов)")
    errors: list[str] = Field(default_factory=list, description="Список ошибок")
    created_keywords: list[KeywordResponse] = Field(
        default_factory=list, description="Созданные ключевые слова"
    )


class KeywordStats(BaseModel):
    """Статистика по ключевому слову"""

    keyword_id: int
    word: str
    total_matches: int
    recent_matches: int  # за последний период
    top_groups: list[str]  # группы где чаще всего встречается
