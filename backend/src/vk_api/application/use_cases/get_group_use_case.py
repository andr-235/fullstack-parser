"""
Use Case для получения группы
"""

from typing import Optional
from pydantic import ValidationError

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.application.dto.vk_api_dto import VKGroupDTO
from vk_api.shared.domain.exceptions import EntityNotFoundError, ValidationError as DomainValidationError


class GetGroupUseCase:
    """Use Case для получения группы по ID"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
    
    async def execute(self, group_id: int) -> Optional[VKGroupDTO]:
        """
        Получить группу по ID
        
        Args:
            group_id: ID группы
            
        Returns:
            VKGroupDTO или None если группа не найдена
            
        Raises:
            DomainValidationError: При невалидном ID группы
        """
        try:
            vk_group_id = VKGroupID(group_id)
        except ValueError as e:
            raise DomainValidationError(f"Invalid group ID: {e}")
        
        group = await self.repository.get_group_by_id(vk_group_id)
        
        if not group:
            return None
        
        return VKGroupDTO.model_validate(group.to_dict())
