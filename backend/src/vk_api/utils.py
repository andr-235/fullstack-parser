"""
Утилиты для VK API
"""

from typing import Tuple
from datetime import datetime


def validate_vk_id(id_value: str, id_type: str = "group") -> Tuple[bool, str]:
    """Валидировать ID VK"""
    if not id_value or not id_value.strip():
        return False, f"ID {id_type} не может быть пустым"
    
    try:
        id_num = int(id_value.strip())
        if id_num <= 0:
            return False, f"ID {id_type} должен быть положительным числом"
    except ValueError:
        return False, f"ID {id_type} должен быть числом"
    
    return True, ""


def convert_group_id_to_owner_id(group_id: int) -> int:
    """Преобразовать ID группы в owner_id для VK API"""
    return -abs(group_id)


def parse_vk_datetime(timestamp: int) -> datetime:
    """Преобразовать timestamp VK в datetime"""
    return datetime.fromtimestamp(timestamp)


__all__ = [
    "validate_vk_id",
    "convert_group_id_to_owner_id",
    "parse_vk_datetime",
]