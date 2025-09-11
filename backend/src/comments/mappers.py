"""
Мапперы для модуля Comments

Преобразование данных между слоями приложения
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import Comment as BaseComment


class CommentMapper:
    """Маппер для преобразования комментариев"""

    @staticmethod
    def to_response_dict(comment: BaseComment) -> Dict[str, Any]:
        """Преобразовать комментарий из БД в формат ответа API"""
        # Формируем matched_keywords
        matched_keywords = []
        if hasattr(comment, "keyword_matches") and comment.keyword_matches:
            matched_keywords = [
                match.keyword.word
                for match in comment.keyword_matches
                if hasattr(match, "keyword") and match.keyword
            ]

        return {
            "id": comment.id,
            "vk_id": str(comment.vk_id),
            "text": comment.text,
            "author": comment.author_name or str(comment.author_id),
            "author_name": comment.author_name,
            "author_screen_name": comment.author_screen_name,
            "author_photo_url": comment.author_photo_url,
            "post_id": str(comment.post_id),
            "post_vk_id": (
                str(comment.post_vk_id) if comment.post_vk_id else None
            ),
            "group_vk_id": comment.group_vk_id,
            "group_id": comment.group_vk_id or 0,
            "author_id": str(comment.author_id),
            "date": (
                comment.published_at.isoformat()
                if comment.published_at
                else ""
            ),
            "published_at": (
                comment.published_at.isoformat()
                if comment.published_at
                else None
            ),
            "is_viewed": comment.is_viewed,
            "is_archived": comment.is_archived,
            "likes_count": comment.likes_count,
            "parent_comment_id": comment.parent_comment_id,
            "matched_keywords_count": getattr(
                comment, "matched_keywords_count", 0
            ),
            "matched_keywords": matched_keywords,
            "processed_at": (
                comment.processed_at.isoformat()
                if comment.processed_at
                else None
            ),
            "created_at": (
                comment.created_at.isoformat() if comment.created_at else None
            ),
            "updated_at": (
                comment.updated_at.isoformat() if comment.updated_at else None
            ),
        }

    @staticmethod
    def to_response_dicts(comments: List[BaseComment]) -> List[Dict[str, Any]]:
        """Преобразовать список комментариев в формат ответа API"""
        return [
            CommentMapper.to_response_dict(comment) for comment in comments
        ]

    @staticmethod
    def to_create_data(comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразовать данные для создания комментария"""
        # Валидация и нормализация данных
        required_fields = [
            "vk_id",
            "post_id",
            "group_vk_id",
            "author_id",
            "author_name",
            "text",
            "published_at",
        ]

        for field in required_fields:
            if field not in comment_data or not comment_data[field]:
                raise ValueError(f"Обязательное поле '{field}' не заполнено")

        return {
            "vk_id": str(comment_data["vk_id"]),
            "post_id": str(comment_data["post_id"]),
            "group_vk_id": int(comment_data["group_vk_id"]),
            "author_id": str(comment_data["author_id"]),
            "author_name": str(comment_data["author_name"]),
            "author_screen_name": comment_data.get("author_screen_name"),
            "author_photo_url": comment_data.get("author_photo_url"),
            "text": str(comment_data["text"]),
            "likes_count": int(comment_data.get("likes_count", 0)),
            "published_at": comment_data["published_at"],
            "parent_comment_id": comment_data.get("parent_comment_id"),
            "is_viewed": bool(comment_data.get("is_viewed", False)),
            "is_archived": bool(comment_data.get("is_archived", False)),
            "matched_keywords_count": int(
                comment_data.get("matched_keywords_count", 0)
            ),
        }

    @staticmethod
    def to_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразовать данные для обновления комментария"""
        # Разрешенные поля для обновления
        allowed_fields = {
            "processed_at",
            "likes_count",
            "is_viewed",
            "is_archived",
            "matched_keywords_count",
        }

        filtered_data = {
            k: v
            for k, v in update_data.items()
            if k in allowed_fields and v is not None
        }

        # Добавляем время обновления
        filtered_data["updated_at"] = datetime.utcnow()

        return filtered_data

    @staticmethod
    def to_stats_dict(
        stats: Dict[str, Any], group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Преобразовать статистику в формат ответа"""
        result = {
            "total_comments": stats.get("total_comments", 0),
            "avg_likes_per_comment": stats.get("avg_likes_per_comment", 0.0),
        }

        if group_id:
            result["group_id"] = group_id

        return result


# Экспорт
__all__ = [
    "CommentMapper",
]
