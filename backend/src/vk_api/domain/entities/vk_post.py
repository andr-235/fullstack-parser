"""
VK Post Entity
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, field_validator

from shared.domain.base_entity import BaseEntity
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID


class VKPost(BaseEntity):
    """VK Post Entity"""
    
    id: VKPostID = Field(..., description="Post ID")
    owner_id: int = Field(..., description="Owner ID (group or user)")
    from_id: Optional[int] = Field(None, description="Author ID")
    text: str = Field(default="", description="Post text")
    date: datetime = Field(..., description="Post date")
    post_type: str = Field(default="post", description="Post type")
    is_pinned: bool = Field(default=False, description="Is post pinned")
    marked_as_ads: bool = Field(default=False, description="Is marked as ads")
    likes_count: int = Field(default=0, ge=0, description="Likes count")
    reposts_count: int = Field(default=0, ge=0, description="Reposts count")
    comments_count: int = Field(default=0, ge=0, description="Comments count")
    views_count: Optional[int] = Field(None, ge=0, description="Views count")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Post attachments")
    copy_history: List[Dict[str, Any]] = Field(default_factory=list, description="Repost history")
    
    @field_validator('post_type')
    @classmethod
    def validate_post_type(cls, v: str) -> str:
        """Валидация типа поста"""
        valid_types = ['post', 'copy', 'reply', 'postpone', 'suggest']
        if v not in valid_types:
            raise ValueError(f"Invalid post type: {v}. Must be one of {valid_types}")
        return v
    
    @property
    def is_group_post(self) -> bool:
        """Пост группы"""
        return self.owner_id < 0
    
    @property
    def is_user_post(self) -> bool:
        """Пост пользователя"""
        return self.owner_id > 0
    
    @property
    def group_id(self) -> Optional[VKGroupID]:
        """ID группы, если это пост группы"""
        if self.is_group_post:
            return VKGroupID(abs(self.owner_id))
        return None
    
    @property
    def author_id(self) -> Optional[VKUserID]:
        """ID автора поста"""
        if self.from_id:
            return VKUserID(self.from_id)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'id': int(self.id),
            'owner_id': self.owner_id,
            'from_id': self.from_id,
            'text': self.text,
            'date': self.date.isoformat(),
            'post_type': self.post_type,
            'is_pinned': self.is_pinned,
            'marked_as_ads': self.marked_as_ads,
            'likes_count': self.likes_count,
            'reposts_count': self.reposts_count,
            'comments_count': self.comments_count,
            'views_count': self.views_count,
            'attachments': self.attachments,
            'copy_history': self.copy_history,
        }
    
    @classmethod
    def from_vk_response(cls, data: Dict[str, Any]) -> "VKPost":
        """Создать из ответа VK API"""
        return cls(
            id=VKPostID(data['id']),
            owner_id=data['owner_id'],
            from_id=data.get('from_id'),
            text=data.get('text', ''),
            date=datetime.fromtimestamp(data['date']),
            post_type=data.get('post_type', 'post'),
            is_pinned=data.get('is_pinned', False),
            marked_as_ads=data.get('marked_as_ads', False),
            likes_count=data.get('likes', {}).get('count', 0),
            reposts_count=data.get('reposts', {}).get('count', 0),
            comments_count=data.get('comments', {}).get('count', 0),
            views_count=data.get('views', {}).get('count') if data.get('views') else None,
            attachments=data.get('attachments', []),
            copy_history=data.get('copy_history', []),
        )
