"""
Pydantic схемы для API
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class VKSearchGroupsRequest(BaseModel):
    """Запрос поиска групп"""
    
    query: str = Field(..., min_length=1, max_length=100)
    count: int = Field(20, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class VKGetGroupPostsRequest(BaseModel):
    """Запрос получения постов группы"""
    
    group_id: int = Field(..., gt=0)
    count: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class VKGetPostCommentsRequest(BaseModel):
    """Запрос получения комментариев к посту"""
    
    group_id: int = Field(..., gt=0)
    post_id: int = Field(..., gt=0)
    count: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class VKGroupResponse(BaseModel):
    """Ответ с группой"""
    
    group: Optional[dict] = None
    error: Optional[str] = None


class VKPostResponse(BaseModel):
    """Ответ с постами"""
    
    posts: List[dict] = Field(default_factory=list)
    total_count: Optional[int] = None
    error: Optional[str] = None


class VKCommentResponse(BaseModel):
    """Ответ с комментариями"""
    
    comments: List[dict] = Field(default_factory=list)
    total_count: Optional[int] = None
    error: Optional[str] = None


class VKUserResponse(BaseModel):
    """Ответ с пользователем"""
    
    user: Optional[dict] = None
    error: Optional[str] = None


__all__ = [
    "VKSearchGroupsRequest",
    "VKGetGroupPostsRequest", 
    "VKGetPostCommentsRequest",
    "VKGroupResponse",
    "VKPostResponse",
    "VKCommentResponse",
    "VKUserResponse",
]
