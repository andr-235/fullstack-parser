"""
VK Group Entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field, field_validator

from shared.domain.base_entity import BaseEntity
from vk_api.domain.value_objects.group_id import VKGroupID


class VKGroup(BaseEntity):
    """VK Group Entity"""
    
    id: VKGroupID = Field(..., description="Group ID")
    name: str = Field(..., min_length=1, description="Group name")
    screen_name: Optional[str] = Field(None, description="Group screen name")
    description: Optional[str] = Field(None, description="Group description")
    type: str = Field(..., description="Group type")
    is_closed: bool = Field(default=False, description="Is group closed")
    is_verified: bool = Field(default=False, description="Is group verified")
    members_count: Optional[int] = Field(None, ge=0, description="Members count")
    photo_50: Optional[str] = Field(None, description="Photo URL 50px")
    photo_100: Optional[str] = Field(None, description="Photo URL 100px")
    photo_200: Optional[str] = Field(None, description="Photo URL 200px")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Валидация типа группы"""
        valid_types = ['group', 'page', 'event']
        if v not in valid_types:
            raise ValueError(f"Invalid group type: {v}. Must be one of {valid_types}")
        return v
    
    @property
    def is_public(self) -> bool:
        """Публичная ли группа"""
        return not self.is_closed
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя группы"""
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'id': int(self.id),
            'name': self.name,
            'screen_name': self.screen_name,
            'description': self.description,
            'type': self.type,
            'is_closed': self.is_closed,
            'is_verified': self.is_verified,
            'members_count': self.members_count,
            'photo_50': self.photo_50,
            'photo_100': self.photo_100,
            'photo_200': self.photo_200,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_vk_response(cls, data: Dict[str, Any]) -> "VKGroup":
        """Создать из ответа VK API"""
        return cls(
            id=VKGroupID(data['id']),
            name=data['name'],
            screen_name=data.get('screen_name'),
            description=data.get('description'),
            type=data['type'],
            is_closed=data.get('is_closed', False),
            is_verified=data.get('verified', False),
            members_count=data.get('members_count'),
            photo_50=data.get('photo_50'),
            photo_100=data.get('photo_100'),
            photo_200=data.get('photo_200'),
            created_at=datetime.fromtimestamp(data['created']) if data.get('created') else None,
        )
