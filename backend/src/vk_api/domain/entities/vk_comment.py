"""
VK Comment Entity
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import Field, field_validator

from shared.domain.base_entity import BaseEntity
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID


class VKComment(BaseEntity):
    """VK Comment Entity"""
    
    id: int = Field(..., gt=0, description="Comment ID")
    post_id: VKPostID = Field(..., description="Post ID")
    from_id: int = Field(..., description="Comment author ID")
    text: str = Field(default="", description="Comment text")
    date: datetime = Field(..., description="Comment date")
    reply_to_user: Optional[int] = Field(None, description="Reply to user ID")
    reply_to_comment: Optional[int] = Field(None, description="Reply to comment ID")
    likes_count: int = Field(default=0, ge=0, description="Likes count")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Comment attachments")
    thread: Optional[Dict[str, Any]] = Field(None, description="Thread info")
    
    @property
    def author_id(self) -> VKUserID:
        """ID автора комментария"""
        return VKUserID(self.from_id)
    
    @property
    def is_reply(self) -> bool:
        """Является ли ответом на другой комментарий"""
        return self.reply_to_comment is not None
    
    @property
    def is_thread_comment(self) -> bool:
        """Является ли комментарием в треде"""
        return self.thread is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'post_id': int(self.post_id),
            'from_id': self.from_id,
            'text': self.text,
            'date': self.date.isoformat(),
            'reply_to_user': self.reply_to_user,
            'reply_to_comment': self.reply_to_comment,
            'likes_count': self.likes_count,
            'attachments': self.attachments,
            'thread': self.thread,
        }
    
    @classmethod
    def from_vk_response(cls, data: Dict[str, Any], post_id: VKPostID) -> "VKComment":
        """Создать из ответа VK API"""
        return cls(
            id=data['id'],
            post_id=post_id,
            from_id=data['from_id'],
            text=data.get('text', ''),
            date=datetime.fromtimestamp(data['date']),
            reply_to_user=data.get('reply_to_user'),
            reply_to_comment=data.get('reply_to_comment'),
            likes_count=data.get('likes', {}).get('count', 0),
            attachments=data.get('attachments', []),
            thread=data.get('thread'),
        )
