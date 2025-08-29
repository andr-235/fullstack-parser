"""
API endpoints для управления VK группами
"""

import asyncio
import re
import uuid
from typing import Dict, List, Optional, TypedDict

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import VKGroup
from app.schemas.base import PaginatedResponse
from app.schemas.vk_group import (
    VKGroupCreate,
    VKGroupRead,
    VKGroupStats,
    VKGroupUpdate,
    VKGroupUploadResponse,
)

# Импорт новых сервисов после рефакторинга
from app.services.group_manager import GroupManager
from app.services.group_validator import GroupValidator
from app.services.group_file_importer import GroupFileImporter
from app.services.group_stats_service import GroupStatsService
from app.services.vk_api_service import VKAPIService

# Инициализация новых сервисов
group_manager = GroupManager()
group_stats_service = GroupStatsService()
vk_service = VKAPIService(
    token=settings.vk.access_token, api_version=settings.vk.api_version
)
group_validator = GroupValidator(vk_service)
group_file_importer = GroupFileImporter(group_manager, group_validator)

router = APIRouter(tags=["Groups"])


class UploadProgress(TypedDict):
    status: str
    progress: int
    current_group: str
    total_groups: int
    processed_groups: int
    created: int
    skipped: int
    errors: List[str]


# Хранилище для отслеживания прогресса загрузки
upload_progress: Dict[str, UploadProgress] = {}


@router.post("/upload", response_model=VKGroupUploadResponse)
async def upload_groups_from_file(
    file: UploadFile,
    is_active: bool = Form(True, description="Активны ли группы"),
    max_posts_to_check: int = Form(
        100, description="Максимум постов для проверки"
    ),
    db: AsyncSession = Depends(get_db),
) -> VKGroupUploadResponse:
    """
    Загружает группы из файла

    Поддерживаемые форматы:
    - CSV: screen_name,name,description
    - TXT: одно screen_name на строку

    Параметры:
    - file: Файл с группами (CSV или TXT)
    - is_active: Активны ли загружаемые группы
    - max_posts_to_check: Максимум постов для проверки
    """
    return await group_file_importer.import_from_csv(
        db=db, file=file, validate_groups=True
    )


@router.post("/upload-with-progress/")
async def upload_groups_with_progress(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    is_active: bool = Form(True, description="Активны ли группы"),
    max_posts_to_check: int = Form(
        100, description="Максимум постов для проверки"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Загружает группы из файла с отслеживанием прогресса
    """
    upload_id = str(uuid.uuid4())

    # Инициализируем прогресс
    upload_progress[upload_id] = {
        "status": "starting",
        "progress": 0,
        "current_group": "Инициализация...",
        "total_groups": 0,
        "processed_groups": 0,
        "created": 0,
        "skipped": 0,
        "errors": [],
    }

    file_content = await file.read()
    background_tasks.add_task(
        process_upload_background,
        upload_id=upload_id,
        file_content=file_content,
        is_active=is_active,
        max_posts_to_check=max_posts_to_check,
        db=db,
    )

    return {"upload_id": upload_id, "status": "started"}


async def create_group_from_screen_name(
    screen_name: str,
    is_active: bool,
    max_posts_to_check: int,
    db: AsyncSession,
) -> Optional[str]:
    """Создает группу из screen_name, возвращает имя группы или None при ошибке"""
    try:
        # Извлекаем screen_name
        clean_screen_name = _extract_screen_name(screen_name)
        if not clean_screen_name:
            return None

        # Проверяем существование группы в БД
        existing_group_result = await db.execute(
            select(VKGroup).where(
                func.lower(VKGroup.screen_name) == clean_screen_name.lower()
            )
        )
        existing_group = existing_group_result.scalar_one_or_none()
        if existing_group:
            return None  # Группа уже существует

        # Получаем данные из VK API
        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )
        vk_group_data = await vk_service.get_group_info(clean_screen_name)

        if not vk_group_data:
            return None  # Группа не найдена в VK

        # Получаем количество участников
        members_count = await vk_service.get_group_members_count(
            clean_screen_name
        )
        if members_count is not None:
            vk_group_data["members_count"] = members_count

        # Проверяем по vk_id
        vk_id = vk_group_data.get("id")
        if vk_id:
            existing_group_result = await db.execute(
                select(VKGroup).where(VKGroup.vk_id == vk_id)
            )
            existing_group = existing_group_result.scalar_one_or_none()
            if existing_group:
                return None  # Группа с таким VK ID уже существует

        # Подготавливаем данные для создания
        vk_group_fields = {c.name for c in VKGroup.__table__.columns}
        vk_group_fields.discard("id")
        filtered_data = {
            k: v for k, v in vk_group_data.items() if k in vk_group_fields
        }

        # Маппинг id -> vk_id
        if "id" in vk_group_data:
            filtered_data["vk_id"] = vk_group_data["id"]
            filtered_data.pop("id", None)

        # Добавляем пользовательские настройки
        filtered_data.update(
            {
                "screen_name": clean_screen_name,
                "is_active": is_active,
                "max_posts_to_check": max_posts_to_check,
            }
        )

        # Убеждаемся, что id не попадает в данные
        filtered_data.pop("id", None)

        # Создаем группу
        new_group = VKGroup(**filtered_data)
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group)

        return new_group.name

    except Exception as e:
        await db.rollback()
        raise e


async def process_upload_background(
    upload_id: str,
    file_content: bytes,
    is_active: bool,
    max_posts_to_check: int,
    db: AsyncSession,
):
    """Фоновая обработка загрузки файла"""
    try:
        # Небольшая задержка чтобы фронтенд успел получить начальный статус
        await asyncio.sleep(0.5)

        # Читаем файл для подсчета групп и сохраняем содержимое
        content_str = file_content.decode("utf-8")
        lines = [
            line.strip() for line in content_str.split("\n") if line.strip()
        ]

        upload_progress[upload_id]["total_groups"] = len(lines)
        upload_progress[upload_id]["status"] = "processing"

        created_count = 0
        skipped_count = 0

        # Обрабатываем каждую группу
        for i, line in enumerate(lines):
            try:
                upload_progress[upload_id][
                    "current_group"
                ] = f"Обработка группы {i+1}/{len(lines)}: {line}"
                upload_progress[upload_id]["processed_groups"] = i + 1
                upload_progress[upload_id]["progress"] = int(
                    (i + 1) / len(lines) * 100
                )

                # Пытаемся создать группу
                try:
                    group_name = await create_group_from_screen_name(
                        screen_name=line,
                        is_active=is_active,
                        max_posts_to_check=max_posts_to_check,
                        db=db,
                    )

                    if group_name:
                        created_count += 1
                        upload_progress[upload_id][
                            "current_group"
                        ] = f"Создана группа: {group_name}"
                    else:
                        skipped_count += 1
                        upload_progress[upload_id][
                            "current_group"
                        ] = f"Пропущена группа: {line} (уже существует или не найдена)"

                    # Небольшая задержка для реалистичности
                    await asyncio.sleep(0.2)

                except Exception as group_error:
                    upload_progress[upload_id]["errors"].append(
                        f"Ошибка обработки группы '{line}': {str(group_error)}"
                    )
                    skipped_count += 1

            except Exception as e:
                upload_progress[upload_id]["errors"].append(
                    f"Ошибка обработки строки {i+1}: {str(e)}"
                )
                skipped_count += 1

        # Завершение
        upload_progress[upload_id]["status"] = "completed"
        upload_progress[upload_id]["current_group"] = "Завершено"
        upload_progress[upload_id]["progress"] = 100
        upload_progress[upload_id]["created"] = created_count
        upload_progress[upload_id]["skipped"] = skipped_count

    except Exception as e:
        upload_progress[upload_id]["status"] = "error"
        upload_progress[upload_id]["errors"].append(str(e))
    finally:
        # Очищаем прогресс через 5 минут
        await asyncio.sleep(300)
        if upload_id in upload_progress:
            del upload_progress[upload_id]


@router.get("/upload-progress/{upload_id}")
async def get_upload_progress(upload_id: str):
    """Получить текущий прогресс загрузки"""
    if upload_id not in upload_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Прогресс загрузки не найден",
        )

    return upload_progress[upload_id]


def _extract_screen_name(url_or_name: str) -> Optional[str]:
    """Извлекает screen_name из URL или возвращает само значение."""
    if not url_or_name:
        return None

    # Паттерн для поиска screen_name в URL.
    # Используем [\w.-]+ для предотвращения ReDoS-уязвимости.
    match = re.search(r"(?:vk\.com/)?([\w.-]+)$", url_or_name)
    return match.group(1) if match else url_or_name


@router.post(
    "/", response_model=VKGroupRead, status_code=status.HTTP_201_CREATED
)
async def create_group(
    group_data: VKGroupCreate,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """

    Добавить новую VK группу для мониторинга
    """
    screen_name = _extract_screen_name(group_data.vk_id_or_screen_name)
    if not screen_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не указан ID или короткое имя группы.",
        )

    vk_service = VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    vk_group_data = await vk_service.get_group_info(screen_name)

    if not vk_group_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа ВКонтакте не найдена.",
        )

    # Получаем количество участников
    members_count = await vk_service.get_group_members_count(screen_name)
    if members_count is not None:
        vk_group_data["members_count"] = members_count

    # Отладочная информация
    import structlog

    logger = structlog.get_logger()
    logger.info(
        "Получены данные группы из VK API",
        screen_name=screen_name,
        vk_group_data=vk_group_data,
        has_name="name" in vk_group_data,
        name_value=vk_group_data.get("name"),
        members_count=members_count,
    )

    # Проверка на существование группы в БД по screen_name и vk_id
    vk_id = vk_group_data.get("id")

    # Проверяем по screen_name
    existing_group_result = await db.execute(
        select(VKGroup).where(
            func.lower(VKGroup.screen_name) == screen_name.lower()
        )
    )
    existing_group = existing_group_result.scalar_one_or_none()
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Группа '{existing_group.name}' ({screen_name}) уже существует в системе.",
        )

    # Проверяем по vk_id
    if vk_id:
        existing_group_result = await db.execute(
            select(VKGroup).where(VKGroup.vk_id == vk_id)
        )
        existing_group = existing_group_result.scalar_one_or_none()
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Группа с VK ID {vk_id} уже существует в системе как '{existing_group.name}' ({existing_group.screen_name}).",
            )

    # Создаем объект группы, объединяя данные из VK API и пользовательские настройки
    vk_group_fields = {c.name for c in VKGroup.__table__.columns}
    # Исключаем поле 'id' из VK API, так как оно конфликтует с автоинкрементным id в БД
    vk_group_fields.discard("id")
    filtered_data = {
        k: v for k, v in vk_group_data.items() if k in vk_group_fields
    }

    # Маппинг id -> vk_id (исключаем id из filtered_data)
    if "id" in vk_group_data:
        filtered_data["vk_id"] = vk_group_data["id"]
        # Убеждаемся, что id не попадает в filtered_data
        filtered_data.pop("id", None)

    # Переопределяем поля пользовательскими данными (только если они переданы)
    update_data = {
        "screen_name": screen_name,
        "is_active": group_data.is_active,
        "max_posts_to_check": group_data.max_posts_to_check,
    }

    # Добавляем опциональные поля только если они переданы
    if group_data.name is not None:
        update_data["name"] = group_data.name
    if group_data.screen_name is not None:
        update_data["screen_name"] = group_data.screen_name
    if group_data.description is not None:
        update_data["description"] = group_data.description

    filtered_data.update(update_data)

    # Убеждаемся, что id не попадает в данные для создания модели
    filtered_data.pop("id", None)

    # Отладочная информация
    import structlog

    logger = structlog.get_logger()
    logger.info(
        "Создание группы",
        filtered_data_keys=list(filtered_data.keys()),
        has_id="id" in filtered_data,
        vk_group_data_keys=list(vk_group_data.keys()),
    )

    new_group = VKGroup(**filtered_data)
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return VKGroupRead.model_validate(new_group)


@router.get("/", response_model=PaginatedResponse[VKGroupRead])
async def get_groups(
    active_only: bool = True,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VKGroupRead]:
    """Получить список VK групп"""
    query = select(VKGroup)

    # Фильтр по активности
    if active_only:
        query = query.filter(VKGroup.is_active.is_(True))

    # Поиск по названию или screen_name
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(VKGroup.name).like(search_term),
                func.lower(VKGroup.screen_name).like(search_term),
            )
        )

    # Получаем все группы без пагинации
    result = await db.execute(query)
    groups = result.scalars().all()

    return PaginatedResponse(
        total=len(groups),
        page=1,
        size=len(groups),
        items=[VKGroupRead.model_validate(group) for group in groups],
    )


@router.get("", response_model=PaginatedResponse[VKGroupRead])
async def get_groups_no_slash(
    active_only: bool = True,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VKGroupRead]:
    """Получить список VK групп (без trailing slash) - алиас для основного endpoint"""
    return await get_groups(active_only=active_only, search=search, db=db)


@router.get("/{group_id}", response_model=VKGroupRead)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Получить информацию о конкретной группе"""
    group = await db.get(VKGroup, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    return VKGroupRead.model_validate(group)


@router.put("/{group_id}", response_model=VKGroupRead)
async def update_group(
    group_id: int,
    group_update: VKGroupUpdate,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Обновить настройки группы"""
    group = await group_manager.update_group(db, group_id, group_update)
    return VKGroupRead.model_validate(group)


@router.post("/{group_id}/refresh", response_model=VKGroupRead)
async def refresh_group_info(
    group_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKGroupRead:
    """Обновить информацию о группе из VK API"""
    group = await group_validator.refresh_group_from_vk(db, group_id)
    return VKGroupRead.model_validate(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить группу"""
    await group_manager.delete_group(db, group_id)
    return


@router.get("/{group_id}/stats", response_model=VKGroupStats)
async def get_group_stats(
    group_id: int, db: AsyncSession = Depends(get_db)
) -> VKGroupStats:
    """
    Получить статистику по группе
    """
    return await group_stats_service.get_group_stats(db, group_id)
