"""
Use Case для получения постов группы
"""

from typing import List, Optional
from datetime import datetime
from pydantic import ValidationError

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.entities.vk_post import VKPost
from vk_api.application.dto.vk_api_dto import VKPostDTO, VKGetGroupPostsRequestDTO
from vk_api.shared.domain.exceptions import ValidationError as DomainValidationError


class GetGroupPostsUseCase:
    """Use Case для получения постов группы"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
    
    async def execute(self, request: VKGetGroupPostsRequestDTO) -> List[VKPostDTO]:
        """
        Получить посты группы
        
        Args:
            request: Параметры запроса
            
        Returns:
            Список постов группы
            
        Raises:
            DomainValidationError: При невалидных параметрах
        """
        try:
            # Валидация параметров
            if request.count <= 0 or request.count > 100:
                raise DomainValidationError("Count must be between 1 and 100")
            
            if request.offset < 0:
                raise DomainValidationError("Offset must be non-negative")
            
            # Валидация дат
            if request.start_date and request.end_date:
                if request.start_date >= request.end_date:
                    raise DomainValidationError("Start date must be before end date")
            
            vk_group_id = VKGroupID(request.group_id)
            
            # Получение постов
            posts = await self.repository.get_group_posts(
                group_id=vk_group_id,
                count=request.count,
                offset=request.offset,
                start_date=request.start_date,
                end_date=request.end_date
            )
            
            return [VKPostDTO.model_validate(post.to_dict()) for post in posts]
            
        except ValueError as e:
            raise DomainValidationError(f"Invalid group ID: {e}")
        except ValidationError as e:
            raise DomainValidationError(f"Validation error: {e}")
        except Exception as e:
            raise DomainValidationError(f"Failed to get group posts: {e}")
