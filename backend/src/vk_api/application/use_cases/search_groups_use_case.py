"""
Use Case для поиска групп
"""

from typing import List
from pydantic import ValidationError

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.application.dto.vk_api_dto import VKGroupDTO, VKSearchGroupsRequestDTO
from vk_api.shared.domain.exceptions import ValidationError as DomainValidationError


class SearchGroupsUseCase:
    """Use Case для поиска групп"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
    
    async def execute(self, request: VKSearchGroupsRequestDTO) -> List[VKGroupDTO]:
        """
        Поиск групп по запросу
        
        Args:
            request: Параметры поиска
            
        Returns:
            Список найденных групп
            
        Raises:
            DomainValidationError: При невалидных параметрах поиска
        """
        try:
            # Валидация запроса
            if not request.query or len(request.query.strip()) < 2:
                raise DomainValidationError("Query must be at least 2 characters long")
            
            if request.count <= 0 or request.count > 1000:
                raise DomainValidationError("Count must be between 1 and 1000")
            
            if request.offset < 0:
                raise DomainValidationError("Offset must be non-negative")
            
            # Поиск групп
            groups = await self.repository.search_groups(
                query=request.query.strip(),
                count=request.count,
                offset=request.offset
            )
            
            return [VKGroupDTO.model_validate(group.to_dict()) for group in groups]
            
        except ValidationError as e:
            raise DomainValidationError(f"Validation error: {e}")
        except Exception as e:
            raise DomainValidationError(f"Search failed: {e}")
