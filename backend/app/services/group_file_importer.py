"""
GroupFileImporter - сервис для импорта групп из файлов

Принципы SOLID:
- Single Responsibility: только импорт групп из файлов
- Open/Closed: легко добавлять новые форматы файлов
- Liskov Substitution: можно заменить на другую реализацию импорта
- Interface Segregation: чистый интерфейс для импорта
- Dependency Inversion: зависит от GroupManager и GroupValidator
"""

import csv
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.vk_group import VKGroupCreate, VKGroupUploadResponse
from app.services.group_manager import GroupManager
from app.services.group_validator import GroupValidator

logger = logging.getLogger(__name__)


class GroupFileImporter:
    """
    Сервис для импорта групп из файлов.

    Поддерживает форматы:
    - CSV файлы
    - Текстовые файлы с screen_name по одному на строку
    - JSON файлы (в будущем)

    Предоставляет высокоуровневый интерфейс для:
    - Загрузки групп из CSV файлов
    - Загрузки групп из текстовых файлов
    - Валидации данных перед импортом
    - Обработки ошибок импорта
    """

    def __init__(
        self, group_manager: GroupManager, group_validator: GroupValidator
    ):
        """
        Инициализация импортера групп.

        Args:
            group_manager: Сервис для управления группами
            group_validator: Сервис для валидации групп
        """
        self.group_manager = group_manager
        self.group_validator = group_validator
        self.logger = logging.getLogger(__name__)

    async def import_from_csv(
        self, db: AsyncSession, file: UploadFile, validate_groups: bool = True
    ) -> VKGroupUploadResponse:
        """
        Импорт групп из CSV файла.

        Ожидаемый формат CSV:
        screen_name,name,description
        test_group,Тестовая группа,Описание группы

        Args:
            db: Сессия базы данных
            file: Загруженный CSV файл
            validate_groups: Проверять существование групп через VK API

        Returns:
            Результат импорта
        """
        try:
            # Читаем содержимое файла
            content = await self._read_file_content(file)
            if not content:
                return VKGroupUploadResponse(
                    status="error",
                    message="Файл пустой или не удалось прочитать",
                    total_processed=0,
                    created=0,
                    skipped=0,
                    failed=0,
                    errors=[],
                )

            # Парсим CSV
            groups_data = self._parse_csv_content(content)

            if not groups_data:
                return VKGroupUploadResponse(
                    status="error",
                    message="Не найдено данных для импорта",
                    total_processed=0,
                    created=0,
                    skipped=0,
                    failed=0,
                    errors=[],
                )

            # Импортируем группы
            return await self._import_groups_data(
                db, groups_data, validate_groups
            )

        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return VKGroupUploadResponse(
                status="error",
                message=f"Ошибка импорта: {str(e)}",
                total_processed=0,
                skipped=0,
                errors=[str(e)],
            )

    async def import_from_text(
        self, db: AsyncSession, file: UploadFile, validate_groups: bool = True
    ) -> VKGroupUploadResponse:
        """
        Импорт групп из текстового файла.

        Ожидаемый формат:
        Одна строка = один screen_name
        test_group
        another_group
        third_group

        Args:
            db: Сессия базы данных
            file: Загруженный текстовый файл
            validate_groups: Проверять существование групп через VK API

        Returns:
            Результат импорта
        """
        try:
            # Читаем содержимое файла
            content = await self._read_file_content(file)
            if not content:
                return VKGroupUploadResponse(
                    status="error",
                    message="Файл пустой или не удалось прочитать",
                    total_processed=0,
                    created=0,
                    skipped=0,
                    failed=0,
                    errors=[],
                )

            # Парсим текстовый файл
            screen_names = self._parse_text_content(content)

            if not screen_names:
                return VKGroupUploadResponse(
                    status="error",
                    message="Не найдено screen_name для импорта",
                    total_processed=0,
                    created=0,
                    skipped=0,
                    failed=0,
                    errors=[],
                )

            # Создаем данные для групп
            groups_data = [
                {"screen_name": screen_name, "name": "", "description": ""}
                for screen_name in screen_names
            ]

            # Импортируем группы
            return await self._import_groups_data(
                db, groups_data, validate_groups
            )

        except Exception as e:
            logger.error(f"Error importing from text file: {e}")
            return VKGroupUploadResponse(
                status="error",
                message=f"Ошибка импорта: {str(e)}",
                total_processed=0,
                created=0,
                skipped=0,
                failed=1,
                errors=[str(e)],
            )

    async def _import_groups_data(
        self,
        db: AsyncSession,
        groups_data: List[Dict],
        validate_groups: bool = True,
    ) -> VKGroupUploadResponse:
        """
        Импорт данных групп в базу данных.

        Args:
            db: Сессия базы данных
            groups_data: Список данных групп для импорта
            validate_groups: Проверять существование групп

        Returns:
            Результат импорта
        """
        imported = 0
        skipped = 0
        errors = []

        for i, group_data in enumerate(groups_data):
            try:
                # Проверяем screen_name
                screen_name = group_data.get("screen_name", "").strip()
                if not screen_name:
                    skipped += 1
                    errors.append(f"Строка {i+1}: пустой screen_name")
                    continue

                # Проверяем существование в БД
                existing = await self.group_manager.get_by_screen_name(
                    db, screen_name
                )
                if existing:
                    skipped += 1
                    errors.append(
                        f"Строка {i+1}: группа '{screen_name}' уже существует"
                    )
                    continue

                # Валидируем через VK API если нужно
                if validate_groups:
                    is_valid = await self.group_validator.validate_screen_name(
                        screen_name
                    )
                    if not is_valid:
                        skipped += 1
                        errors.append(
                            f"Строка {i+1}: группа '{screen_name}' не найдена в VK"
                        )
                        continue

                # Получаем данные из VK API для создания полной группы
                vk_data = await self.group_validator.get_group_data_from_vk(
                    screen_name
                )
                if not vk_data:
                    skipped += 1
                    errors.append(
                        f"Строка {i+1}: не удалось получить данные из VK для '{screen_name}'"
                    )
                    continue

                # Создаем группу
                create_data = VKGroupCreate(
                    vk_id_or_screen_name=vk_data.get(
                        "screen_name", screen_name
                    ),
                    name=vk_data.get("name", group_data.get("name", "")),
                    description=group_data.get("description", ""),
                )

                await self.group_manager.create_group(db, create_data)
                imported += 1

                if imported % 10 == 0:  # Логируем каждые 10 групп
                    logger.info(f"Imported {imported} groups so far")

            except Exception as e:
                skipped += 1
                errors.append(
                    f"Строка {i+1}: ошибка при импорте '{screen_name}': {str(e)}"
                )
                continue

        # Формируем результат
        # Импорт успешен, если обработали хотя бы одну строку (даже если ничего не импортировали)
        success = (imported + skipped + len(errors)) > 0
        message = f"Импорт завершен: {imported} импортировано, {skipped} пропущено, {len(errors)} ошибок"

        logger.info(message)

        return VKGroupUploadResponse(
            status="success" if success else "error",
            message=message,
            total_processed=imported + skipped + len(errors),
            created=imported,
            skipped=skipped,
            failed=len(errors),
            errors=errors[:100],  # Ограничиваем количество ошибок
        )

    async def _read_file_content(self, file: UploadFile) -> str:
        """
        Прочитать содержимое файла.

        Args:
            file: Загруженный файл

        Returns:
            Содержимое файла как строка
        """
        try:
            content = await file.read()

            # Проверяем размер файла (максимум 10MB)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Файл слишком большой (максимум 10MB)",
                )

            # Декодируем содержимое
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                # Пробуем другие кодировки
                for encoding in ["windows-1251", "cp1251", "iso-8859-1"]:
                    try:
                        return content.decode(encoding)
                    except UnicodeDecodeError:
                        continue

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось декодировать файл. Используйте UTF-8 или Windows-1251",
                )

        except Exception as e:
            logger.error(f"Error reading file content: {e}")
            raise

    def _parse_csv_content(self, content: str) -> List[Dict]:
        """
        Парсинг содержимого CSV файла.

        Args:
            content: Содержимое CSV файла

        Returns:
            Список словарей с данными групп
        """
        try:
            groups_data = []
            reader = csv.DictReader(
                io.StringIO(content),
                fieldnames=["screen_name", "name", "description"],
            )

            for row in reader:
                # Пропускаем заголовок если он есть
                if row["screen_name"] and row["screen_name"].lower() not in [
                    "screen_name",
                    "screen name",
                ]:
                    groups_data.append(
                        {
                            "screen_name": row["screen_name"].strip(),
                            "name": row.get("name", "").strip(),
                            "description": row.get("description", "").strip(),
                        }
                    )

            logger.info(f"Parsed {len(groups_data)} groups from CSV")
            return groups_data

        except Exception as e:
            logger.error(f"Error parsing CSV content: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка парсинга CSV: {str(e)}",
            )

    def _parse_text_content(self, content: str) -> List[str]:
        """
        Парсинг содержимого текстового файла.

        Args:
            content: Содержимое текстового файла

        Returns:
            Список screen_name
        """
        try:
            screen_names = []

            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line or line.startswith("#"):
                    continue

                # Извлекаем screen_name из URL если нужно
                if "vk.com/" in line:
                    # Извлекаем screen_name из URL
                    import re

                    match = re.search(r"vk\.com/([^/?#]+)", line)
                    if match:
                        screen_name = match.group(1)
                    else:
                        continue
                else:
                    screen_name = line

                # Очищаем screen_name
                screen_name = screen_name.strip()
                if screen_name and not screen_name.isdigit():
                    screen_names.append(screen_name)

            logger.info(
                f"Parsed {len(screen_names)} screen names from text file"
            )
            return screen_names

        except Exception as e:
            logger.error(f"Error parsing text content: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка парсинга текстового файла: {str(e)}",
            )

    async def validate_import_data(self, groups_data: List[Dict]) -> Dict:
        """
        Валидировать данные для импорта перед загрузкой.

        Args:
            groups_data: Данные групп для валидации

        Returns:
            Результат валидации
        """
        try:
            total = len(groups_data)
            valid = 0
            invalid = 0
            errors = []

            for i, group_data in enumerate(groups_data):
                screen_name = group_data.get("screen_name", "").strip()

                if not screen_name:
                    invalid += 1
                    errors.append(f"Строка {i+1}: пустой screen_name")
                    continue

                # Проверяем существование в VK
                is_valid = await self.group_validator.validate_screen_name(
                    screen_name
                )
                if is_valid:
                    valid += 1
                else:
                    invalid += 1
                    errors.append(
                        f"Строка {i+1}: группа '{screen_name}' не найдена в VK"
                    )

            return {
                "total": total,
                "valid": valid,
                "invalid": invalid,
                "errors": errors[:50],  # Ограничиваем количество ошибок
            }

        except Exception as e:
            logger.error(f"Error validating import data: {e}")
            return {
                "total": len(groups_data),
                "valid": 0,
                "invalid": len(groups_data),
                "errors": [f"Ошибка валидации: {str(e)}"],
            }
