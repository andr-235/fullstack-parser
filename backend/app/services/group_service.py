"""
Сервис для работы с моделью VKGroup
"""

import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.vk_group import VKGroup
from app.schemas.error_report import ErrorContext, ErrorSeverity, ErrorType
from app.schemas.vk_group import (
    VKGroupCreate,
    VKGroupRead,
    VKGroupStats,
    VKGroupUpdate,
    VKGroupUploadResponse,
)
from app.services.base import BaseService
from app.services.error_reporting_service import error_reporting_service
from app.services.vk_api_service import VKAPIService

# Типы для улучшения читаемости
GroupData = Dict[str, Any]  # Данные группы от VK API
UploadResult = Dict[str, Any]  # Результат загрузки


class GroupService(BaseService[VKGroup, VKGroupCreate, VKGroupUpdate]):
    """
    Сервис для управления VK группами

    Основные возможности:
    - Создание и обновление групп
    - Загрузка групп из файлов
    - Получение статистики
    - Валидация через VK API
    """

    def __init__(self):
        super().__init__(VKGroup)
        self.logger = structlog.get_logger(__name__)

    async def get_by_screen_name(
        self, db: AsyncSession, *, screen_name: str
    ) -> Optional[VKGroup]:
        """Получить группу по ее короткому имени"""
        result = await db.execute(
            select(self.model).filter(self.model.screen_name == screen_name)
        )
        return result.scalar_one_or_none()

    async def get_by_vk_id(
        self, db: AsyncSession, *, vk_id: int
    ) -> Optional[VKGroup]:
        """Получить группу по ее VK ID"""
        result = await db.execute(
            select(self.model).filter(self.model.vk_id == vk_id)
        )
        return result.scalar_one_or_none()

    async def create_group_with_vk(
        self, db: AsyncSession, group_data: VKGroupCreate
    ) -> VKGroup:
        """
        Создать группу через VK API с полной валидацией и фильтрацией

        Args:
            db: Сессия базы данных
            group_data: Данные для создания группы

        Returns:
            Созданная группа

        Raises:
            HTTPException: Если группа не найдена в VK или уже существует
        """
        screen_name = self._extract_screen_name(
            group_data.vk_id_or_screen_name
        )
        if not screen_name:
            error_entry = error_reporting_service.create_error_entry(
                error_type=ErrorType.VALIDATION,
                severity=ErrorSeverity.HIGH,
                message="Не указан ID или короткое имя группы",
                context=ErrorContext(
                    screen_name=group_data.vk_id_or_screen_name,
                    operation="create_group",
                ),
            )
            error_reporting_service.log_error_report(
                error_reporting_service.create_error_report(
                    operation="create_group", errors=[error_entry]
                )
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан ID или короткое имя группы.",
            )

        # Получаем данные группы из VK API
        vk_group_data = await self._fetch_group_from_vk(screen_name)

        # Проверяем существование в БД
        await self._check_group_exists(db, screen_name)

        # Создаем группу
        new_group = await self._create_group_from_vk_data(
            db, vk_group_data, group_data
        )

        self.logger.info(
            "Группа создана успешно",
            group_id=new_group.id,
            vk_id=new_group.vk_id,
            name=new_group.name,
            screen_name=new_group.screen_name,
        )

        return new_group

    async def update_group(
        self, db: AsyncSession, group_id: int, group_update: VKGroupUpdate
    ) -> VKGroup:
        """
        Обновляет группу

        Args:
            db: Сессия базы данных
            group_id: ID группы
            group_update: Данные для обновления

        Returns:
            Обновленная группа

        Raises:
            HTTPException: Если группа не найдена
        """
        group = await db.get(VKGroup, group_id)
        if not group:
            self.logger.warning("Группа не найдена", group_id=group_id)
            raise HTTPException(status_code=404, detail="Группа не найдена")

        update_data = group_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)

        await db.commit()
        await db.refresh(group)

        self.logger.info(
            "Группа обновлена", group_id=group_id, updates=update_data
        )
        return group

    async def refresh_group_from_vk(
        self, db: AsyncSession, group_id: int
    ) -> VKGroup:
        """
        Обновляет информацию о группе из VK API

        Args:
            db: Сессия базы данных
            group_id: ID группы

        Returns:
            Обновленная группа

        Raises:
            HTTPException: Если группа не найдена или ошибка VK API
        """
        group = await db.get(VKGroup, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")

        try:
            # Получаем актуальную информацию из VK API
            vk_service = VKAPIService(
                token=settings.vk.access_token,
                api_version=settings.vk.api_version,
            )

            vk_group_data = await vk_service.get_group_info(group.screen_name)
            if not vk_group_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Группа не найдена в VK API",
                )

            # Обновляем поля из VK API
            vk_group_fields = {c.name for c in VKGroup.__table__.columns}
            for key, value in vk_group_data.items():
                if key in vk_group_fields and key not in [
                    "id",
                    "created_at",
                    "updated_at",
                ]:
                    setattr(group, key, value)

            await db.commit()
            await db.refresh(group)

            self.logger.info(
                "Информация о группе обновлена из VK API",
                group_id=group_id,
                screen_name=group.screen_name,
                members_count=group.members_count,
            )
            return group

        except Exception as e:
            self.logger.error(
                "Ошибка обновления информации о группе из VK API",
                group_id=group_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обновления информации о группе: {str(e)}",
            )

    async def delete_group(self, db: AsyncSession, group_id: int) -> None:
        """
        Удаляет группу

        Args:
            db: Сессия базы данных
            group_id: ID группы

        Raises:
            HTTPException: Если группа не найдена
        """
        group = await db.get(VKGroup, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")

        await db.delete(group)
        await db.commit()

        self.logger.info("Группа удалена", group_id=group_id, name=group.name)

    async def get_group_stats(
        self, db: AsyncSession, group_id: int
    ) -> VKGroupStats:
        """
        Получить статистику по группе

        Args:
            db: Сессия базы данных
            group_id: ID группы

        Returns:
            Статистика группы

        Raises:
            HTTPException: Если группа не найдена
        """
        from sqlalchemy import func, select

        from app.models.comment_keyword_match import CommentKeywordMatch
        from app.models.keyword import Keyword
        from app.models.vk_comment import VKComment
        from app.models.vk_post import VKPost

        group = await db.get(VKGroup, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа не найдена",
            )

        # Подсчитываем комментарии с ключевыми словами
        comments_with_keywords_query = (
            select(func.count(VKComment.id))
            .select_from(VKComment)
            .join(VKPost, VKComment.post_id == VKPost.id)
            .where(VKPost.group_id == group_id)
            .where(VKComment.matched_keywords_count > 0)
        )
        comments_with_keywords = (
            await db.scalar(comments_with_keywords_query) or 0
        )

        # Получаем топ ключевых слов
        top_keywords_query = (
            select(
                Keyword.text,
                func.count(CommentKeywordMatch.id).label("match_count"),
            )
            .select_from(CommentKeywordMatch)
            .join(VKComment, CommentKeywordMatch.comment_id == VKComment.id)
            .join(VKPost, VKComment.post_id == VKPost.id)
            .join(Keyword, CommentKeywordMatch.keyword_id == Keyword.id)
            .where(VKPost.group_id == group_id)
            .group_by(Keyword.text)
            .order_by(func.count(CommentKeywordMatch.id).desc())
            .limit(10)
        )

        top_keywords_result = await db.execute(top_keywords_query)
        top_keywords = [
            {"keyword": row.text, "count": row.match_count}
            for row in top_keywords_result.all()
        ]

        return VKGroupStats(
            group_id=group.vk_id,
            total_posts=group.total_posts_parsed,
            total_comments=group.total_comments_found,
            comments_with_keywords=comments_with_keywords,
            last_activity=group.last_parsed_at,
            top_keywords=top_keywords,
        )

    async def upload_groups_from_file(
        self,
        db: AsyncSession,
        file: UploadFile,
        is_active: bool = True,
        max_posts_to_check: int = 100,
    ) -> VKGroupUploadResponse:
        """
        Загружает группы из файла (CSV или TXT)

        Поддерживаемые форматы:
        - CSV: screen_name,name,description
        - TXT: одно screen_name на строку

        Args:
            db: Сессия базы данных
            file: Файл для загрузки
            is_active: Активны ли загружаемые группы
            max_posts_to_check: Максимум постов для проверки

        Returns:
            Результат загрузки с подробным отчетом об ошибках

        Raises:
            HTTPException: При ошибках валидации файла
        """
        import time

        start_time = time.time()

        # Устанавливаем сессию базы данных для сервиса отчетов об ошибках
        error_reporting_service.set_db(db)

        errors = []

        try:
            # Валидируем файл
            self._validate_upload_file(file)
        except HTTPException as e:
            error_entry = error_reporting_service.create_error_entry(
                error_type=ErrorType.VALIDATION,
                severity=ErrorSeverity.HIGH,
                message=f"Ошибка валидации файла: {e.detail}",
                context=ErrorContext(
                    operation="upload_groups_from_file",
                    additional_data={"filename": file.filename},
                ),
                exception=e,
            )
            errors.append(error_entry)
            raise

        try:
            # Читаем содержимое файла
            content_str = await self._read_file_content(file)
        except HTTPException as e:
            error_entry = error_reporting_service.create_error_entry(
                error_type=ErrorType.VALIDATION,
                severity=ErrorSeverity.HIGH,
                message=f"Ошибка чтения файла: {e.detail}",
                context=ErrorContext(
                    operation="upload_groups_from_file",
                    additional_data={"filename": file.filename},
                ),
                exception=e,
            )
            errors.append(error_entry)
            raise

        try:
            # Парсим данные в зависимости от формата
            groups_data = await self._parse_file_content(
                content_str,
                file.filename or "unknown.txt",
                is_active,
                max_posts_to_check,
            )
        except HTTPException as e:
            error_entry = error_reporting_service.create_error_entry(
                error_type=ErrorType.VALIDATION,
                severity=ErrorSeverity.HIGH,
                message=f"Ошибка парсинга файла: {e.detail}",
                context=ErrorContext(
                    operation="upload_groups_from_file",
                    additional_data={"filename": file.filename},
                ),
                exception=e,
            )
            errors.append(error_entry)
            raise

        # Создаем группы с детальным отслеживанием ошибок
        result = await self._create_groups_from_data_with_errors(
            db, groups_data, errors
        )

        processing_time = time.time() - start_time

        # Создаем подробный отчет об ошибках
        if errors:
            error_report = (
                error_reporting_service.create_group_load_error_report(
                    errors=errors,
                    groups_processed=result["total_processed"],
                    groups_successful=result["created"],
                    groups_failed=result.get("failed", 0),
                    groups_skipped=result["skipped"],
                    processing_time_seconds=processing_time,
                )
            )
            error_reporting_service.log_error_report(error_report)

            # Добавляем отчет в результат
            result["error_report"] = error_report

        return VKGroupUploadResponse(**result)

    # Вспомогательные методы

    def _extract_screen_name(self, url_or_name: str) -> Optional[str]:
        """
        Извлекает screen_name из URL или возвращает само значение

        Args:
            url_or_name: URL или screen_name группы

        Returns:
            Извлеченный screen_name или None
        """
        if not url_or_name:
            return None

        # Если это URL, извлекаем screen_name
        if "vk.com/" in url_or_name:
            match = re.search(r"vk\.com/([^/?]+)", url_or_name)
            if match:
                screen_name = match.group(1)
                # Убираем префикс "club" если есть
                if screen_name.startswith("club"):
                    return screen_name[4:]  # Убираем "club"
                return screen_name

        # Если это уже screen_name, убираем префикс "club" если есть
        if url_or_name.startswith("club"):
            return url_or_name[4:]  # Убираем "club"

        return url_or_name

    async def _fetch_group_from_vk(self, screen_name: str) -> GroupData:
        """
        Получает данные группы из VK API

        Args:
            screen_name: Короткое имя группы

        Returns:
            Данные группы от VK API

        Raises:
            HTTPException: Если группа не найдена в VK
        """
        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

        vk_group_data = await vk_service.get_group_info(screen_name)
        if not vk_group_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Группа ВКонтакте не найдена.",
            )

        # Дополнительно получаем количество участников
        try:
            members_count = await vk_service.get_group_members_count(
                screen_name
            )
            if members_count is not None:
                vk_group_data["members_count"] = members_count
        except Exception as e:
            self.logger.warning(
                "Не удалось получить количество участников группы",
                screen_name=screen_name,
                error=str(e),
            )

        return vk_group_data

    async def _check_group_exists(
        self, db: AsyncSession, screen_name: str
    ) -> None:
        """
        Проверяет существование группы в БД

        Args:
            db: Сессия базы данных
            screen_name: Короткое имя группы

        Raises:
            HTTPException: Если группа уже существует
        """
        existing_group_result = await db.execute(
            select(VKGroup).where(
                or_(
                    func.lower(VKGroup.screen_name) == screen_name.lower(),
                    VKGroup.screen_name == screen_name,  # Точное совпадение
                )
            )
        )
        existing_group = existing_group_result.scalar_one_or_none()

        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Группа '{existing_group.name}' ({screen_name}) уже существует в системе.",
            )

    async def _create_group_from_vk_data(
        self,
        db: AsyncSession,
        vk_group_data: GroupData,
        group_data: VKGroupCreate,
    ) -> VKGroup:
        """
        Создает группу из данных VK API

        Args:
            db: Сессия базы данных
            vk_group_data: Данные от VK API
            group_data: Пользовательские данные

        Returns:
            Созданная группа
        """
        # Маппинг полей VK API в поля модели
        mapped_data = {}

        # Основные поля из VK API (приоритет VK API над пользовательскими данными)
        if "id" in vk_group_data:
            mapped_data["vk_id"] = vk_group_data["id"]

        # Название группы берем из VK API, а не из пользовательских данных
        if "name" in vk_group_data:
            mapped_data["name"] = vk_group_data["name"]
        elif group_data.name:
            mapped_data["name"] = group_data.name

        # Описание берем из VK API, если есть, иначе из пользовательских данных
        if "description" in vk_group_data and vk_group_data["description"]:
            mapped_data["description"] = vk_group_data["description"]
        elif group_data.description:
            mapped_data["description"] = group_data.description

        # Screen name из пользовательских данных
        if group_data.vk_id_or_screen_name:
            screen_name = self._extract_screen_name(
                group_data.vk_id_or_screen_name
            )
            if screen_name:
                mapped_data["screen_name"] = screen_name

        # Остальные поля из VK API
        if "members_count" in vk_group_data:
            mapped_data["members_count"] = vk_group_data["members_count"]

        if "is_closed" in vk_group_data:
            # Преобразуем числовое значение в boolean
            is_closed_value = vk_group_data["is_closed"]
            if isinstance(is_closed_value, int):
                mapped_data["is_closed"] = is_closed_value in [
                    1,
                    2,
                ]  # 1 - закрытая, 2 - частная
            else:
                mapped_data["is_closed"] = bool(is_closed_value)

        # Фото группы
        for photo_field in ["photo_200", "photo_100", "photo_50"]:
            if photo_field in vk_group_data and vk_group_data[photo_field]:
                mapped_data["photo_url"] = vk_group_data[photo_field]
                break

        # Пользовательские настройки
        mapped_data["is_active"] = group_data.is_active
        mapped_data["max_posts_to_check"] = group_data.max_posts_to_check

        # Создаем группу
        group = VKGroup(**mapped_data)
        db.add(group)
        await db.commit()
        await db.refresh(group)

        return group

    def _validate_upload_file(self, file: UploadFile) -> None:
        """
        Валидирует файл для загрузки

        Args:
            file: Файл для проверки

        Raises:
            HTTPException: При ошибках валидации
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не выбран",
            )

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in [".csv", ".txt"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только файлы CSV и TXT",
            )

    async def _read_file_content(self, file: UploadFile) -> str:
        """
        Читает содержимое файла

        Args:
            file: Файл для чтения

        Returns:
            Содержимое файла как строка

        Raises:
            HTTPException: При ошибках чтения
        """
        try:
            content = await file.read()
            return content.decode("utf-8")
        except UnicodeDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в кодировке UTF-8",
            ) from err

    async def _parse_file_content(
        self,
        content_str: str,
        filename: str,
        is_active: bool,
        max_posts_to_check: int,
    ) -> List[VKGroupCreate]:
        """
        Парсит содержимое файла в список данных групп

        Args:
            content_str: Содержимое файла
            filename: Имя файла
            is_active: Активны ли группы
            max_posts_to_check: Максимум постов для проверки

        Returns:
            Список данных для создания групп
        """
        file_extension = Path(filename).suffix.lower()
        groups_data = []

        if file_extension == ".csv":
            groups_data = self._parse_csv_content(
                content_str, is_active, max_posts_to_check
            )
        elif file_extension == ".txt":
            groups_data = self._parse_txt_content(
                content_str, is_active, max_posts_to_check
            )

        if not groups_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не содержит валидных групп",
            )

        return groups_data

    def _parse_csv_content(
        self, content_str: str, is_active: bool, max_posts_to_check: int
    ) -> List[VKGroupCreate]:
        """Парсит CSV содержимое"""
        groups_data = []

        try:
            csv_reader = csv.reader(io.StringIO(content_str))
            for row_num, row in enumerate(csv_reader, 1):
                if not row or not row[0].strip():
                    continue  # Пропускаем пустые строки

                # Пропускаем заголовки (первая строка)
                if row_num == 1 and (
                    row[0].lower()
                    in [
                        "screen_name",
                        "name",
                        "description",
                        "vk_id",
                        "vk_id_or_screen_name",
                    ]
                    or any(
                        header.lower()
                        in [
                            "screen_name",
                            "name",
                            "description",
                            "vk_id",
                            "vk_id_or_screen_name",
                        ]
                        for header in row
                    )
                ):
                    continue

                try:
                    screen_name = row[0].strip()
                    name = (
                        row[1].strip()
                        if len(row) > 1 and row[1].strip()
                        else screen_name
                    )
                    description = (
                        row[2].strip()
                        if len(row) > 2 and row[2].strip()
                        else None
                    )

                    if not screen_name:
                        continue

                    groups_data.append(
                        VKGroupCreate(
                            vk_id_or_screen_name=screen_name,
                            name=name,
                            description=description,
                            is_active=is_active,
                            max_posts_to_check=max_posts_to_check,
                        )
                    )
                except Exception as e:
                    self.logger.error(
                        "Ошибка парсинга строки CSV",
                        row_num=row_num,
                        error=str(e),
                    )
                    continue

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка чтения CSV файла: {str(e)}",
            ) from e

        return groups_data

    def _parse_txt_content(
        self, content_str: str, is_active: bool, max_posts_to_check: int
    ) -> List[VKGroupCreate]:
        """Парсит TXT содержимое"""
        groups_data = []
        lines = content_str.split("\n")

        for line_num, line in enumerate(lines, 1):
            screen_name = line.strip()
            if not screen_name or screen_name.startswith("#"):
                continue  # Пропускаем пустые строки и комментарии

            groups_data.append(
                VKGroupCreate(
                    vk_id_or_screen_name=screen_name,
                    name=screen_name,
                    description=None,
                    is_active=is_active,
                    max_posts_to_check=max_posts_to_check,
                )
            )

        return groups_data

    async def _create_groups_from_data(
        self, db: AsyncSession, groups_data: List[VKGroupCreate]
    ) -> UploadResult:
        """Создает группы из данных (устаревший метод)"""
        return await self._create_groups_from_data_with_errors(
            db, groups_data, []
        )

    async def _create_groups_from_data_with_errors(
        self,
        db: AsyncSession,
        groups_data: List[VKGroupCreate],
        existing_errors: List,
    ) -> UploadResult:
        """
        Создает группы из списка данных с детальным отслеживанием ошибок

        Args:
            db: Сессия базы данных
            groups_data: Список данных групп
            existing_errors: Существующие ошибки

        Returns:
            Результат загрузки
        """
        created_groups = []
        skipped_count = 0
        failed_count = 0
        total_processed = len(groups_data)
        all_errors = existing_errors.copy()

        for group_data in groups_data:
            try:
                # Проверяем существование
                screen_name = self._extract_screen_name(
                    group_data.vk_id_or_screen_name
                )
                if not screen_name:
                    error_entry = error_reporting_service.create_error_entry(
                        error_type=ErrorType.VALIDATION,
                        severity=ErrorSeverity.MEDIUM,
                        message=f"Не удалось извлечь screen_name из '{group_data.vk_id_or_screen_name}'",
                        context=ErrorContext(
                            screen_name=group_data.vk_id_or_screen_name,
                            operation="create_group_from_data",
                        ),
                    )
                    all_errors.append(error_entry)
                    failed_count += 1
                    continue

                # Проверяем существование группы по screen_name и vk_id
                existing_query = select(VKGroup).where(
                    or_(
                        func.lower(VKGroup.screen_name) == screen_name.lower(),
                        VKGroup.screen_name
                        == screen_name,  # Точное совпадение
                    )
                )
                existing = await db.execute(existing_query)
                existing_group = existing.scalar_one_or_none()

                if existing_group:
                    self.logger.info(
                        "Группа уже существует, пропускаем",
                        screen_name=screen_name,
                        existing_vk_id=existing_group.vk_id,
                        existing_name=existing_group.name,
                    )
                    skipped_count += 1
                    continue

                # Создаем группу через VK API
                try:
                    new_group = await self.create_group_with_vk(db, group_data)
                    created_groups.append(new_group)
                except HTTPException as e:
                    # Если группа уже существует по vk_id, пропускаем её
                    if "уже существует" in e.detail:
                        self.logger.info(
                            "Группа уже существует по vk_id, пропускаем",
                            screen_name=screen_name,
                            error_detail=e.detail,
                        )
                        skipped_count += 1
                        continue
                    else:
                        raise

            except HTTPException as e:
                error_entry = error_reporting_service.create_error_entry(
                    error_type=ErrorType.VALIDATION,
                    severity=ErrorSeverity.HIGH,
                    message=f"Ошибка создания группы '{group_data.vk_id_or_screen_name}': {e.detail}",
                    context=ErrorContext(
                        screen_name=group_data.vk_id_or_screen_name,
                        operation="create_group_from_data",
                    ),
                    exception=e,
                )
                all_errors.append(error_entry)
                failed_count += 1
            except Exception as e:
                error_entry = error_reporting_service.create_error_entry(
                    error_type=ErrorType.UNKNOWN,
                    severity=ErrorSeverity.HIGH,
                    message=f"Неожиданная ошибка создания группы '{group_data.vk_id_or_screen_name}': {str(e)}",
                    context=ErrorContext(
                        screen_name=group_data.vk_id_or_screen_name,
                        operation="create_group_from_data",
                    ),
                    exception=e,
                )
                all_errors.append(error_entry)
                failed_count += 1

        return {
            "status": "success" if failed_count == 0 else "partial_success",
            "message": f"Загружено {len(created_groups)} групп из {total_processed} строк",
            "total_processed": total_processed,
            "created": len(created_groups),
            "skipped": skipped_count,
            "failed": failed_count,
            "errors": [error.message for error in all_errors],
            "created_groups": [
                VKGroupRead.model_validate(group) for group in created_groups
            ],
        }


group_service = GroupService()
