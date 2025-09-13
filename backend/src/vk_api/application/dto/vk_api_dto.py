"""
DTO для VK API модуля
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from shared.presentation.responses.base_responses import PaginatedResponse


class VKGroupDTO(BaseModel):
    """DTO для VK группы"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    screen_name: Optional[str] = Field(None, description="Group screen name")
    description: Optional[str] = Field(None, description="Group description")
    type: str = Field(..., description="Group type")
    is_closed: bool = Field(..., description="Is group closed")
    is_verified: bool = Field(..., description="Is group verified")
    members_count: Optional[int] = Field(None, description="Members count")
    photo_50: Optional[str] = Field(None, description="Photo URL 50px")
    photo_100: Optional[str] = Field(None, description="Photo URL 100px")
    photo_200: Optional[str] = Field(None, description="Photo URL 200px")
    created_at: Optional[datetime] = Field(None, description="Creation date")


class VKPostDTO(BaseModel):
    """DTO для VK поста"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Post ID")
    owner_id: int = Field(..., description="Owner ID")
    from_id: Optional[int] = Field(None, description="Author ID")
    text: str = Field(..., description="Post text")
    date: datetime = Field(..., description="Post date")
    post_type: str = Field(..., description="Post type")
    is_pinned: bool = Field(..., description="Is post pinned")
    marked_as_ads: bool = Field(..., description="Is marked as ads")
    likes_count: int = Field(..., description="Likes count")
    reposts_count: int = Field(..., description="Reposts count")
    comments_count: int = Field(..., description="Comments count")
    views_count: Optional[int] = Field(None, description="Views count")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Post attachments")


class VKCommentDTO(BaseModel):
    """DTO для VK комментария"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Comment ID")
    post_id: int = Field(..., description="Post ID")
    from_id: int = Field(..., description="Comment author ID")
    text: str = Field(..., description="Comment text")
    date: datetime = Field(..., description="Comment date")
    reply_to_user: Optional[int] = Field(None, description="Reply to user ID")
    reply_to_comment: Optional[int] = Field(None, description="Reply to comment ID")
    likes_count: int = Field(..., description="Likes count")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Comment attachments")


class VKUserDTO(BaseModel):
    """DTO для VK пользователя"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="User ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    screen_name: Optional[str] = Field(None, description="Screen name")
    photo_50: Optional[str] = Field(None, description="Photo URL 50px")
    photo_100: Optional[str] = Field(None, description="Photo URL 100px")
    photo_200: Optional[str] = Field(None, description="Photo URL 200px")
    is_verified: bool = Field(default=False, description="Is verified")
    is_closed: bool = Field(default=False, description="Is closed")


class VKGroupWithPostsDTO(BaseModel):
    """DTO для группы с постами"""
    
    model_config = ConfigDict(from_attributes=True)
    
    group: VKGroupDTO = Field(..., description="Group info")
    posts: List[VKPostDTO] = Field(..., description="Group posts")
    posts_count: int = Field(..., description="Posts count")


class VKPostWithCommentsDTO(BaseModel):
    """DTO для поста с комментариями"""
    
    model_config = ConfigDict(from_attributes=True)
    
    post: VKPostDTO = Field(..., description="Post info")
    comments: List[VKCommentDTO] = Field(..., description="Post comments")
    comments_count: int = Field(..., description="Comments count")


class VKGroupAnalyticsDTO(BaseModel):
    """DTO для аналитики группы"""
    
    model_config = ConfigDict(from_attributes=True)
    
    group: VKGroupDTO = Field(..., description="Group info")
    period_days: int = Field(..., description="Analytics period in days")
    posts_count: int = Field(..., description="Posts count in period")
    total_likes: int = Field(..., description="Total likes")
    total_reposts: int = Field(..., description="Total reposts")
    total_comments: int = Field(..., description="Total comments")
    avg_engagement: float = Field(..., description="Average engagement rate")


class VKSearchGroupsRequestDTO(BaseModel):
    """DTO для запроса поиска групп"""
    
    query: str = Field(..., min_length=2, max_length=100, description="Search query")
    count: int = Field(default=20, ge=1, le=1000, description="Results count")
    offset: int = Field(default=0, ge=0, description="Offset")


class VKGetGroupPostsRequestDTO(BaseModel):
    """DTO для запроса постов группы"""
    
    group_id: int = Field(..., gt=0, description="Group ID")
    count: int = Field(default=100, ge=1, le=100, description="Posts count")
    offset: int = Field(default=0, ge=0, description="Offset")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


class VKGetPostCommentsRequestDTO(BaseModel):
    """DTO для запроса комментариев поста"""
    
    group_id: int = Field(..., gt=0, description="Group ID")
    post_id: int = Field(..., gt=0, description="Post ID")
    count: int = Field(default=100, ge=1, le=100, description="Comments count")
    offset: int = Field(default=0, ge=0, description="Offset")
    sort: str = Field(default="asc", description="Sort order")
    thread_items_count: int = Field(default=0, ge=0, description="Thread items count")


# Response DTOs
class VKGroupsResponseDTO(PaginatedResponse[VKGroupDTO]):
    """Ответ со списком групп"""
    pass


class VKPostsResponseDTO(PaginatedResponse[VKPostDTO]):
    """Ответ со списком постов"""
    pass


class VKCommentsResponseDTO(PaginatedResponse[VKCommentDTO]):
    """Ответ со списком комментариев"""
    pass
