"""
Domain сущности для системы настроек (DDD)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .base import Entity, ValueObject


class SettingsSection(ValueObject):
    """Секция настроек"""

    def __init__(
        self,
        name: str,
        values: Dict[str, Any],
        description: Optional[str] = None,
    ):
        self.name = name
        self.values = values
        self.description = description


class SystemSettings(Entity):
    """Доменная сущность системных настроек"""

    def __init__(
        self,
        id: Optional[str] = None,
        sections: Optional[Dict[str, SettingsSection]] = None,
    ):
        super().__init__(id or "system_settings")
        self.sections = sections or {}

    def get_section(self, section_name: str) -> Optional[SettingsSection]:
        """Получить секцию настроек"""
        return self.sections.get(section_name)

    def update_section(self, section: SettingsSection) -> None:
        """Обновить секцию настроек"""
        self.sections[section.name] = section
        self.update()

    def get_value(self, section_name: str, key: str) -> Any:
        """Получить значение из секции"""
        section = self.get_section(section_name)
        if section:
            return section.values.get(key)
        return None

    def set_value(self, section_name: str, key: str, value: Any) -> None:
        """Установить значение в секции"""
        if section_name not in self.sections:
            self.sections[section_name] = SettingsSection(section_name, {})

        self.sections[section_name].values[key] = value
        self.update()

    def validate_settings(self) -> Dict[str, Any]:
        """Валидация настроек"""
        issues = {}

        # Проверки для каждой секции
        for section_name, section in self.sections.items():
            section_issues = self._validate_section(section_name, section)
            if section_issues:
                issues[section_name] = section_issues

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_sections": len(self.sections),
            "sections_with_issues": len(issues),
        }

    def _validate_section(
        self, section_name: str, section: SettingsSection
    ) -> Dict[str, str]:
        """Валидация секции настроек"""
        issues = {}

        # Пример валидации для разных секций
        if section_name == "database":
            if not section.values.get("url"):
                issues["url"] = "Database URL is required"
            if not section.values.get("pool_size"):
                issues["pool_size"] = "Pool size is required"

        elif section_name == "vk_api":
            if not section.values.get("access_token"):
                issues["access_token"] = "VK access token is required"
            if not section.values.get("api_version"):
                issues["api_version"] = "API version is required"

        elif section_name == "redis":
            if not section.values.get("url"):
                issues["url"] = "Redis URL is required"

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "sections": {
                name: {
                    "name": section.name,
                    "values": section.values,
                    "description": section.description,
                }
                for name, section in self.sections.items()
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "version": self.version,
            },
        }
