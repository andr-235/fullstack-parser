"""
Use Case для получения комментариев поста
"""

from typing import List
from pydantic import ValidationError

from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.entities.vk_comment import VKComment
from vk_api.application.dto.vk_api_dto import VKCommentDTO, VKGetPostCommentsRequestDTO
from vk_api.shared.domain.exceptions import ValidationError as DomainValidationError


class GetPostCommentsUseCase:
    """Use Case для получения комментариев поста"""
    
    def __init__(self, repository: VKAPIRepositoryInterface):
        self.repository = repository
    
    async def execute(self, request: VKGetPostCommentsRequestDTO) -> List[VKCommentDTO]:
        """
        Получить комментарии к посту
        
        Args:
            request: Параметры запроса
            
        Returns:
            Список комментариев
            
        Raises:
            DomainValidationError: При невалидных параметрах
        """
        try:
            # Валидация параметров
            if request.count <= 0 or request.count > 100:
                raise DomainValidationError("Count must be between 1 and 100")
            
            if request.offset < 0:
                raise DomainValidationError("Offset must be non-negative")
            
            if request.sort not in ["asc", "desc"]:
                raise DomainValidationError("Sort must be 'asc' or 'desc'")
            
            if request.thread_items_count < 0:
                raise DomainValidationError("Thread items count must be non-negative")
            
            vk_group_id = VKGroupID(request.group_id)
            vk_post_id = VKPostID(request.post_id)
            
            # Получение комментариев
            comments = await self.repository.get_post_comments(
                group_id=vk_group_id,
                post_id=vk_post_id,
                count=request.count,
                offset=request.offset,
                sort=request.sort,
                thread_items_count=request.thread_items_count
            )
            
            return [VKCommentDTO.model_validate(comment.to_dict()) for comment in comments]
            
        except ValueError as e:
            raise DomainValidationError(f"Invalid ID: {e}")
        except ValidationError as e:
            raise DomainValidationError(f"Validation error: {e}")
        except Exception as e:
            raise DomainValidationError(f"Failed to get post comments: {e}")
