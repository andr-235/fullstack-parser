"""
Модели данных VK API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class VKGroup(BaseModel):
    """Группа VK"""

    id: int
    name: str
    screen_name: str
    description: Optional[str] = None
    members_count: Optional[int] = None
    is_closed: Optional[bool] = None
    type: Optional[str] = None
    photo_50: Optional[str] = None
    photo_100: Optional[str] = None
    photo_200: Optional[str] = None


class VKPost(BaseModel):
    """Пост VK"""

    id: int
    owner_id: int
    from_id: Optional[int] = None
    text: str
    date: datetime
    likes: Optional[Dict[str, Any]] = None
    comments: Optional[Dict[str, Any]] = None
    reposts: Optional[Dict[str, Any]] = None
    views: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class VKComment(BaseModel):
    """Комментарий VK"""

    id: int
    from_id: int
    post_id: int
    text: str
    date: datetime
    likes: Optional[Dict[str, Any]] = None
    reply_to_user: Optional[int] = None
    reply_to_comment: Optional[int] = None


class VKUser(BaseModel):
    """Пользователь VK"""

    id: int
    first_name: str
    last_name: str
    photo_50: Optional[str] = None
    photo_100: Optional[str] = None
    photo_200: Optional[str] = None
    is_closed: Optional[bool] = None
    can_access_closed: Optional[bool] = None


__all__ = [
    "VKGroup",
    "VKPost",
    "VKComment",
    "VKUser",
]
