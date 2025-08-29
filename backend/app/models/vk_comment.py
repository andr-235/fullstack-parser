"""
Модель VK комментария
"""

from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class VKComment(BaseModel):
    """Модель VK комментария"""

    __tablename__ = "vk_comments"

    # Основная информация
    vk_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="ID комментария в ВК"
    )
    text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Текст комментария"
    )

    # Связи
    post_id: Mapped[int] = mapped_column(
        ForeignKey("vk_posts.id"), nullable=False
    )
    post: Mapped["VKPost"] = relationship("VKPost", back_populates="comments")
    post_vk_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="ID поста в VK (для формирования ссылок)"
    )

    # Автор комментария
    author_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="ID автора комментария"
    )
    author_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="Имя автора"
    )
    author_screen_name: Mapped[Optional[str]] = mapped_column(
        String(100), comment="Короткое имя автора"
    )
    author_photo_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="URL фото автора"
    )

    # Метаданные
    published_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        comment="Дата публикации комментария",
    )
    likes_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество лайков"
    )

    # Иерархия комментариев
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vk_comments.id"), comment="ID родительского комментария"
    )
    parent_comment: Mapped[Optional["VKComment"]] = relationship(
        "VKComment", remote_side="VKComment.id"
    )

    # Вложения (упрощённо)
    has_attachments: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Есть ли вложения"
    )
    attachments_info: Mapped[Optional[str]] = mapped_column(
        Text, comment="JSON с информацией о вложениях"
    )

    # Состояние обработки
    is_processed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Обработан ли комментарий"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был обработан"
    )

    # Найденные ключевые слова
    matched_keywords_count: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество найденных ключевых слов"
    )

    # Статус просмотра и архивирования
    is_viewed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Просмотрен ли комментарий"
    )
    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был просмотрен"
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Архивирован ли комментарий"
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), comment="Когда был архивирован"
    )

    # Связи с ключевыми словами
    keyword_matches: Mapped[list["CommentKeywordMatch"]] = relationship(
        "CommentKeywordMatch",
        back_populates="comment",
        cascade="all, delete-orphan",
    )

    # DDD Domain Methods - Добавлены для совместимости с Domain Layer

    def validate_business_rules(self) -> None:
        """
        Валидация бизнес-правил домена (DDD метод)

        Выполняет проверки целостности данных комментария
        согласно бизнес-правилам домена.
        """
        if not self.text or len(self.text.strip()) == 0:
            raise ValueError("Comment text cannot be empty")

        if len(self.text) > 10000:
            raise ValueError("Comment text is too long (max 10000 characters)")

        if self.author_id <= 0:
            raise ValueError("Invalid author ID")

        if self.post_id <= 0:
            raise ValueError("Invalid post ID")

    def is_from_author(self, author_id: int) -> bool:
        """
        Проверяет, принадлежит ли комментарий указанному автору (DDD бизнес-правило)

        Args:
            author_id: ID автора для проверки

        Returns:
            True если комментарий от указанного автора
        """
        return self.author_id == author_id

    def contains_keywords(self, keywords: List[str]) -> bool:
        """
        Проверяет, содержит ли комментарий ключевые слова (DDD бизнес-правило)

        Args:
            keywords: Список ключевых слов для поиска

        Returns:
            True если найдено хотя бы одно ключевое слово
        """
        if not keywords:
            return False

        text_lower = self.text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def mark_as_viewed(self) -> None:
        """
        Отмечает комментарий как просмотренный (DDD бизнес-метод)

        Обновляет статус и timestamp просмотра.
        """
        if not self.is_viewed:
            self.is_viewed = True
            self.viewed_at = datetime.utcnow()
            # Здесь можно добавить Domain Event
            # self.add_domain_event(CommentViewedEvent(self.id))

    def mark_as_processed(self) -> None:
        """
        Отмечает комментарий как обработанный (DDD бизнес-метод)

        Обновляет статус и timestamp обработки.
        """
        if not self.is_processed:
            self.is_processed = True
            self.processed_at = datetime.utcnow()
            # Здесь можно добавить Domain Event
            # self.add_domain_event(CommentProcessedEvent(self.id))

    def archive(self) -> None:
        """
        Архивирует комментарий (DDD бизнес-метод)

        Перемещает комментарий в архив.
        """
        if not self.is_archived:
            self.is_archived = True
            self.archived_at = datetime.utcnow()
            # Здесь можно добавить Domain Event
            # self.add_domain_event(CommentArchivedEvent(self.id))

    def unarchive(self) -> None:
        """
        Разархивирует комментарий (DDD бизнес-метод)

        Возвращает комментарий из архива.
        """
        if self.is_archived:
            self.is_archived = False
            self.archived_at = None

    def add_keyword_match(
        self, keyword_word: str, match_position: int = 0
    ) -> None:
        """
        Добавляет совпадение с ключевым словом (DDD бизнес-метод)

        Args:
            keyword_word: Найденное ключевое слово
            match_position: Позиция совпадения в тексте
        """
        # Обновляем счетчик
        self.matched_keywords_count += 1

        # Здесь можно добавить логику создания связи с ключевым словом
        # через CommentKeywordMatch

    def get_processing_status(self) -> str:
        """
        Получает текстовый статус обработки комментария (DDD бизнес-метод)

        Returns:
            Статус обработки: 'new', 'viewed', 'processed', 'archived'
        """
        if self.is_archived:
            return "archived"
        elif self.is_processed:
            return "processed"
        elif self.is_viewed:
            return "viewed"
        else:
            return "new"

    def can_be_edited(self) -> bool:
        """
        Проверяет, можно ли редактировать комментарий (DDD бизнес-правило)

        Returns:
            True если комментарий можно редактировать
        """
        # Бизнес-правило: нельзя редактировать обработанные или архивированные комментарии
        return not (self.is_processed or self.is_archived)

    def calculate_relevance_score(self, keywords: List[str] = None) -> float:
        """
        Вычисляет релевантность комментария (DDD бизнес-логика)

        Args:
            keywords: Список ключевых слов для оценки

        Returns:
            Оценка релевантности от 0.0 до 1.0
        """
        score = 0.0
        max_score = 1.0

        # Фактор ключевых слов
        if keywords and self.contains_keywords(keywords):
            score += 0.4

        # Фактор длины текста (предпочитаем средние комментарии)
        text_length = len(self.text)
        if 50 <= text_length <= 500:
            score += 0.3
        elif text_length < 50:
            score += 0.1

        # Фактор наличия автора
        if self.author_name:
            score += 0.1

        # Фактор количества лайков
        if self.likes_count > 0:
            like_score = min(self.likes_count / 100.0, 0.2)
            score += like_score

        return min(score, max_score)

    # Domain Events Support - Поддержка событий домена
    _domain_events: List[dict] = []

    def add_domain_event(self, event_data: dict) -> None:
        """
        Добавляет Domain Event (DDD паттерн)

        Args:
            event_data: Данные события
        """
        event = {
            "event_type": event_data.get("event_type", "unknown"),
            "aggregate_id": self.id,
            "occurred_at": datetime.utcnow().isoformat(),
            "event_data": event_data,
        }
        self._domain_events.append(event)

    @property
    def domain_events(self) -> List[dict]:
        """
        Получает список Domain Events (DDD паттерн)

        Returns:
            Список событий домена
        """
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """
        Очищает список Domain Events (DDD паттерн)

        Вызывается после успешного сохранения агрегата.
        """
        self._domain_events.clear()

    def __repr__(self):
        return f"<VKComment(vk_id={self.vk_id}, post_id={self.post_id}, matches={self.matched_keywords_count}, status={self.get_processing_status()})>"
