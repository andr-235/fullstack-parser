"""
Упрощенный модуль Groups для небольшого проекта.

Объединяет всю функциональность в один файл без DDD/Clean Architecture.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, PositiveInt
from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from src.common.database import Base, get_db_session


# Модель группы
class Group(Base):
    """SQLAlchemy модель группы VK"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    screen_name = Column(String(255), unique=True, index=True)
    description = Column(String)
    members_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic схемы
class GroupCreate(BaseModel):
    """Схема для создания группы"""
    vk_id: PositiveInt = Field(..., description="ID группы в VK")
    screen_name: str = Field(..., min_length=1, max_length=255, description="Короткое имя группы")
    name: str = Field(..., min_length=1, max_length=255, description="Название группы")
    description: Optional[str] = Field(None, max_length=1000, description="Описание группы")


class GroupUpdate(BaseModel):
    """Схема для обновления группы"""
    name: Optional[str] = Field(None, description="Новое название группы")
    screen_name: Optional[str] = Field(None, description="Новое короткое имя")
    description: Optional[str] = Field(None, description="Новое описание")
    is_active: Optional[bool] = Field(None, description="Активировать/деактивировать группу")


class GroupResponse(BaseModel):
    """Схема ответа с информацией о группе"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID в базе данных")
    vk_id: int = Field(..., description="ID группы в VK")
    screen_name: str = Field(..., description="Короткое имя группы")
    name: str = Field(..., description="Название группы")
    description: Optional[str] = Field(None, description="Описание группы")
    is_active: bool = Field(default=True, description="Активна ли группа")
    members_count: int = Field(default=0, description="Количество участников")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время последнего обновления")


class GroupListResponse(BaseModel):
    """Схема ответа со списком групп"""
    page: int = Field(..., description="Номер страницы")
    size: int = Field(..., description="Размер страницы")
    total: int = Field(..., description="Общее количество элементов")
    pages: int = Field(..., description="Общее количество страниц")
    items: List[GroupResponse] = Field(..., description="Список групп")


class GroupBulkAction(BaseModel):
    """Массовые действия с группами"""
    group_ids: List[int] = Field(..., description="Список ID групп")
    action: str = Field(..., description="Действие: activate, deactivate")


class GroupBulkResponse(BaseModel):
    """Ответ на массовое действие"""
    success_count: int = Field(..., description="Количество успешных операций")
    error_count: int = Field(..., description="Количество ошибок")


# Сервис для работы с группами
class GroupService:
    """Упрощенный сервис для работы с группами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_group(self, group_id: int) -> Group:
        """Получить группу по ID"""
        query = select(Group).where(Group.id == group_id)
        result = await self.db.execute(query)
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail=f"Группа с ID {group_id} не найдена")
        return group

    async def get_groups(
        self,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Group]:
        """Получить список групп с фильтрацией и пагинацией"""
        query = select(Group)

        if is_active is not None:
            query = query.where(Group.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Group.name.ilike(search_filter),
                    Group.screen_name.ilike(search_filter),
                    Group.description.ilike(search_filter),
                )
            )

        query = query.order_by(desc(Group.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_group(self, group_data: dict) -> Group:
        """Создать новую группу"""
        # Валидация обязательных полей
        required_fields = ["vk_id", "screen_name", "name"]
        for field in required_fields:
            if field not in group_data or not group_data[field]:
                raise HTTPException(status_code=400, detail=f"Обязательное поле '{field}' не заполнено")

        # Проверка уникальности VK ID
        existing = await self.get_group_by_vk_id(group_data["vk_id"])
        if existing:
            raise HTTPException(status_code=400, detail="Группа с таким VK ID уже существует")

        # Проверка уникальности screen_name
        existing_screen = await self.get_group_by_screen_name(group_data["screen_name"])
        if existing_screen:
            raise HTTPException(status_code=400, detail="Группа с таким screen_name уже существует")

        group = Group(**group_data)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update_group(self, group_id: int, update_data: dict) -> Group:
        """Обновить группу"""
        group = await self.get_group(group_id)

        # Проверка уникальности screen_name при обновлении
        if "screen_name" in update_data:
            existing = await self.get_group_by_screen_name(update_data["screen_name"])
            if existing and existing.id != group_id:
                raise HTTPException(status_code=400, detail="Группа с таким screen_name уже существует")

        for key, value in update_data.items():
            if hasattr(group, key):
                setattr(group, key, value)

        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete_group(self, group_id: int) -> bool:
        """Удалить группу"""
        group = await self.get_group(group_id)
        await self.db.delete(group)
        await self.db.commit()
        return True

    async def activate_group(self, group_id: int) -> Group:
        """Активировать группу"""
        return await self.update_group(group_id, {"is_active": True})

    async def deactivate_group(self, group_id: int) -> Group:
        """Деактивировать группу"""
        return await self.update_group(group_id, {"is_active": False})

    async def get_group_by_vk_id(self, vk_id: int) -> Optional[Group]:
        """Получить группу по VK ID"""
        query = select(Group).where(Group.vk_id == vk_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_group_by_screen_name(self, screen_name: str) -> Optional[Group]:
        """Получить группу по screen_name"""
        query = select(Group).where(Group.screen_name == screen_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def bulk_activate(self, group_ids: List[int]) -> dict:
        """Массовое включение групп"""
        success_count = await self._bulk_update_active_status(group_ids, True)
        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
        }

    async def bulk_deactivate(self, group_ids: List[int]) -> dict:
        """Массовое отключение групп"""
        success_count = await self._bulk_update_active_status(group_ids, False)
        return {
            "success_count": success_count,
            "total_requested": len(group_ids),
        }

    async def _bulk_update_active_status(self, group_ids: List[int], is_active: bool) -> int:
        """Массовое обновление статуса активности групп"""
        update_data = {"is_active": is_active, "updated_at": datetime.utcnow()}
        query = update(Group).where(Group.id.in_(group_ids)).values(**update_data)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount

    async def count_groups(self, is_active: Optional[bool] = None, search: Optional[str] = None) -> int:
        """Подсчитать количество групп с фильтрами"""
        query = select(Group)

        if is_active is not None:
            query = query.where(Group.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Group.name.ilike(search_filter),
                    Group.screen_name.ilike(search_filter),
                    Group.description.ilike(search_filter),
                )
            )

        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_active_groups_count(self) -> int:
        """Получить количество активных групп"""
        query = select(Group).where(Group.is_active == True)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_groups_growth_percentage(self, days: int = 30) -> float:
        """Получить процент роста групп за период"""
        if days > 365:
            raise HTTPException(status_code=400, detail="Количество дней не может превышать 365")

        current_period = await self._get_groups_count_by_period(days)
        previous_period_start = datetime.utcnow() - timedelta(days=days * 2)
        previous_period_end = datetime.utcnow() - timedelta(days=days)
        previous_period = await self._get_groups_count_by_period_custom(previous_period_start, previous_period_end)

        if previous_period == 0:
            return 100.0 if current_period > 0 else 0.0

        return ((current_period - previous_period) / previous_period) * 100

    async def _get_groups_count_by_period(self, days: int) -> int:
        """Получить количество групп за период"""
        period_start = datetime.utcnow() - timedelta(days=days)
        query = select(Group).where(Group.created_at >= period_start)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def _get_groups_count_by_period_custom(self, start_date: datetime, end_date: datetime) -> int:
        """Получить количество групп за кастомный период"""
        query = select(Group).where(Group.created_at.between(start_date, end_date))
        result = await self.db.execute(query)
        return len(result.scalars().all())


# Зависимости
def get_group_service(db: AsyncSession = Depends(get_db_session)) -> GroupService:
    """Получить сервис групп"""
    return GroupService(db)


# Параметры пагинации
PageParam = Annotated[int, Query(ge=1, description="Номер страницы")]
SizeParam = Annotated[int, Query(ge=1, le=100, description="Размер страницы")]
SearchParam = Annotated[Optional[str], Query(description="Поисковый запрос")]


# Роутер
router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/", response_model=GroupListResponse)
async def get_groups(
    page: PageParam = 1,
    size: SizeParam = 20,
    is_active: Optional[bool] = Query(None, description="Показать только активные группы"),
    search: SearchParam = None,
    service: GroupService = Depends(get_group_service),
) -> GroupListResponse:
    """Получить список групп с фильтрацией и пагинацией"""
    limit = size
    offset = (page - 1) * size

    groups = await service.get_groups(
        is_active=is_active,
        search=search,
        limit=limit,
        offset=offset,
    )

    total = await service.count_groups(is_active=is_active, search=search)

    return GroupListResponse(
        items=[GroupResponse.model_validate(g) for g in groups],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if size > 0 else 0,
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по ID"""
    group = await service.get_group(group_id)
    return GroupResponse.model_validate(group)


@router.get("/vk/{vk_id}", response_model=GroupResponse)
async def get_group_by_vk_id(
    vk_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по VK ID"""
    group = await service.get_group_by_vk_id(vk_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Группа с VK ID {vk_id} не найдена")
    return GroupResponse.model_validate(group)


@router.get("/screen/{screen_name}", response_model=GroupResponse)
async def get_group_by_screen_name(
    screen_name: str,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Получить группу по screen_name"""
    group = await service.get_group_by_screen_name(screen_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Группа @{screen_name} не найдена")
    return GroupResponse.model_validate(group)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    group_data: GroupCreate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Создать новую группу"""
    created = await service.create_group(group_data.model_dump())
    return GroupResponse.model_validate(created)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Обновить группу"""
    updated = await service.update_group(group_id, group_data.model_dump(exclude_unset=True))
    return GroupResponse.model_validate(updated)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
):
    """Удалить группу"""
    await service.delete_group(group_id)


@router.post("/{group_id}/activate", response_model=GroupResponse)
async def activate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Активировать группу"""
    activated = await service.activate_group(group_id)
    return GroupResponse.model_validate(activated)


@router.post("/{group_id}/deactivate", response_model=GroupResponse)
async def deactivate_group(
    group_id: int,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    """Деактивировать группу"""
    deactivated = await service.deactivate_group(group_id)
    return GroupResponse.model_validate(deactivated)


@router.post("/bulk/activate", response_model=GroupBulkResponse)
async def bulk_activate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое включение групп"""
    if action_data.action != "activate":
        raise HTTPException(status_code=400, detail="Поддерживается только действие 'activate'")

    result = await service.bulk_activate(action_data.group_ids)
    return GroupBulkResponse(
        success_count=result["success_count"],
        error_count=result["total_requested"] - result["success_count"],
    )


@router.post("/bulk/deactivate", response_model=GroupBulkResponse)
async def bulk_deactivate_groups(
    action_data: GroupBulkAction,
    service: GroupService = Depends(get_group_service),
) -> GroupBulkResponse:
    """Массовое отключение групп"""
    if action_data.action != "deactivate":
        raise HTTPException(status_code=400, detail="Поддерживается только действие 'deactivate'")

    result = await service.bulk_deactivate(action_data.group_ids)
    return GroupBulkResponse(
        success_count=result["success_count"],
        error_count=result["total_requested"] - result["success_count"],
    )


@router.get("/metrics")
async def get_groups_metrics(
    service: GroupService = Depends(get_group_service)
):
    """Получить метрики групп"""
    active = await service.get_active_groups_count()
    growth = await service.get_groups_growth_percentage(30)

    return {
        "active_groups": active,
        "growth_percentage": round(growth, 1),
        "trend": "рост с прошлого месяца" if growth > 0 else "снижение с прошлого месяца"
    }


__all__ = ["router"]