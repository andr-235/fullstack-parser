"""
Тесты для GroupFileImporter - сервиса импорта групп из файлов

Тестируемые возможности:
- Импорт из CSV файлов
- Импорт из текстовых файлов
- Парсинг содержимого файлов
- Валидация данных перед импортом
- Обработка ошибок импорта
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from io import BytesIO

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.group_file_importer import GroupFileImporter
from app.services.group_manager import GroupManager
from app.services.group_validator import GroupValidator
from app.schemas.vk_group import VKGroupUploadResponse


class TestGroupFileImporter:
    """Тесты для GroupFileImporter"""

    @pytest.fixture
    def mock_group_manager(self):
        """Мок для GroupManager"""
        return AsyncMock(spec=GroupManager)

    @pytest.fixture
    def mock_group_validator(self):
        """Мок для GroupValidator"""
        return AsyncMock(spec=GroupValidator)

    @pytest.fixture
    def mock_db(self):
        """Мок для базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def file_importer(self, mock_group_manager, mock_group_validator):
        """Экземпляр GroupFileImporter для тестирования"""
        return GroupFileImporter(mock_group_manager, mock_group_validator)

    # Тесты для _read_file_content

    @pytest.mark.asyncio
    async def test_read_file_content_success(self, file_importer):
        """Тест успешного чтения содержимого файла"""
        # Создание тестового файла
        content = "test content"
        file = MagicMock(spec=UploadFile)
        file.read.return_value = content.encode("utf-8")

        # Выполнение
        result = await file_importer._read_file_content(file)

        # Проверки
        assert result == content
        file.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_file_content_utf8(self, file_importer):
        """Тест чтения файла в кодировке UTF-8"""
        # Создание тестового файла с UTF-8
        content = "тестовый контент"
        file = MagicMock(spec=UploadFile)
        file.read.return_value = content.encode("utf-8")

        # Выполнение
        result = await file_importer._read_file_content(file)

        # Проверки
        assert result == content
        file.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_file_content_windows1251(self, file_importer):
        """Тест чтения файла в кодировке Windows-1251"""
        # Создание тестового файла с Windows-1251
        content = "тестовый контент"
        file = MagicMock(spec=UploadFile)
        file.read.return_value = content.encode("windows-1251")

        # Выполнение
        result = await file_importer._read_file_content(file)

        # Проверки
        assert result == content
        file.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_file_content_too_large(self, file_importer):
        """Тест чтения слишком большого файла"""
        # Создание большого файла (11MB)
        large_content = "x" * (11 * 1024 * 1024)
        file = MagicMock(spec=UploadFile)
        file.read.return_value = large_content.encode("utf-8")

        # Выполнение и проверка исключения
        with pytest.raises(Exception):  # HTTPException
            await file_importer._read_file_content(file)

    # Тесты для _parse_csv_content

    def test_parse_csv_content_success(self, file_importer):
        """Тест успешного парсинга CSV содержимого"""
        # CSV содержимое
        csv_content = """screen_name,name,description
test_group,Тестовая группа,Описание группы
another_group,Другая группа,Еще одно описание"""

        # Выполнение
        result = file_importer._parse_csv_content(csv_content)

        # Проверки
        assert len(result) == 2
        assert result[0]["screen_name"] == "test_group"
        assert result[0]["name"] == "Тестовая группа"
        assert result[0]["description"] == "Описание группы"
        assert result[1]["screen_name"] == "another_group"

    def test_parse_csv_content_with_header(self, file_importer):
        """Тест парсинга CSV с заголовком screen_name"""
        # CSV с заголовком в данных
        csv_content = """screen_name,name,description
screen name,Название,Описание
test_group,Тестовая группа,Описание группы"""

        # Выполнение
        result = file_importer._parse_csv_content(csv_content)

        # Проверки
        assert len(result) == 2
        assert result[0]["screen_name"] == "screen name"
        assert result[1]["screen_name"] == "test_group"

    def test_parse_csv_content_empty(self, file_importer):
        """Тест парсинга пустого CSV"""
        # Выполнение
        result = file_importer._parse_csv_content("")

        # Проверки
        assert result == []

    def test_parse_csv_content_only_header(self, file_importer):
        """Тест парсинга CSV только с заголовками"""
        # CSV только с заголовками
        csv_content = "screen_name,name,description"

        # Выполнение
        result = file_importer._parse_csv_content(csv_content)

        # Проверки
        assert result == []

    # Тесты для _parse_text_content

    def test_parse_text_content_success(self, file_importer):
        """Тест успешного парсинга текстового содержимого"""
        # Текстовое содержимое
        text_content = """test_group
another_group
third_group"""

        # Выполнение
        result = file_importer._parse_text_content(text_content)

        # Проверки
        assert len(result) == 3
        assert result == ["test_group", "another_group", "third_group"]

    def test_parse_text_content_with_urls(
        self, file_importer, mock_group_validator
    ):
        """Тест парсинга текста с URL"""
        # Текстовое содержимое с URL
        text_content = """https://vk.com/test_group
another_group
https://vk.com/third_group?w=wall"""

        # Выполнение
        result = file_importer._parse_text_content(text_content)

        # Проверки
        assert len(result) == 3
        assert "test_group" in result
        assert "another_group" in result
        assert "third_group" in result

    def test_parse_text_content_with_comments(self, file_importer):
        """Тест парсинга текста с комментариями"""
        # Текстовое содержимое с комментариями
        text_content = """# Это комментарий
test_group
# Еще один комментарий
another_group"""

        # Выполнение
        result = file_importer._parse_text_content(text_content)

        # Проверки
        assert len(result) == 2
        assert result == ["test_group", "another_group"]

    def test_parse_text_content_empty_lines(self, file_importer):
        """Тест парсинга текста с пустыми строками"""
        # Текстовое содержимое с пустыми строками
        text_content = """
test_group

another_group


"""

        # Выполнение
        result = file_importer._parse_text_content(text_content)

        # Проверки
        assert len(result) == 2
        assert result == ["test_group", "another_group"]

    def test_parse_text_content_numeric_only(self, file_importer):
        """Тест парсинга текста с числовыми screen_name"""
        # Текстовое содержимое с числами
        text_content = """test_group
123456789
another_group"""

        # Выполнение
        result = file_importer._parse_text_content(text_content)

        # Проверки
        assert len(result) == 2
        assert result == ["test_group", "another_group"]
        assert "123456789" not in result

    # Тесты для import_from_csv

    @pytest.mark.asyncio
    async def test_import_from_csv_success(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест успешного импорта из CSV"""
        # Настройка моков
        mock_group_manager.get_by_screen_name.return_value = (
            None  # Группа не существует
        )
        mock_group_validator.validate_screen_name.return_value = (
            True  # Группа существует в VK
        )
        mock_group_validator.get_group_data_from_vk.return_value = {
            "id": 123456789,
            "screen_name": "test_group",
            "name": "Тестовая группа",
        }
        mock_group_manager.create_group.return_value = MagicMock()

        # Создание CSV файла
        csv_content = (
            "screen_name,name,description\ntest_group,Тестовая группа,Описание"
        )
        file = MagicMock(spec=UploadFile)
        file.read.return_value = csv_content.encode("utf-8")

        # Выполнение
        result = await file_importer.import_from_csv(mock_db, file)

        # Проверки
        assert isinstance(result, VKGroupUploadResponse)
        assert result.success is True
        assert result.imported == 1
        assert result.skipped == 0
        mock_group_manager.create_group.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_from_csv_with_duplicates(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест импорта CSV с дубликатами в БД"""
        # Настройка моков
        existing_group = MagicMock()
        mock_group_manager.get_by_screen_name.return_value = (
            existing_group  # Группа уже существует
        )

        # Создание CSV файла
        csv_content = (
            "screen_name,name,description\ntest_group,Тестовая группа,Описание"
        )
        file = MagicMock(spec=UploadFile)
        file.read.return_value = csv_content.encode("utf-8")

        # Выполнение
        result = await file_importer.import_from_csv(mock_db, file)

        # Проверки
        assert result.success is True
        assert result.imported == 0
        assert result.skipped == 1
        assert len(result.errors) == 1
        mock_group_manager.create_group.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_from_csv_validation_failed(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест импорта CSV с проваленной валидацией VK"""
        # Настройка моков
        mock_group_manager.get_by_screen_name.return_value = (
            None  # Группа не существует в БД
        )
        mock_group_validator.validate_screen_name.return_value = (
            False  # Группа не существует в VK
        )

        # Создание CSV файла
        csv_content = (
            "screen_name,name,description\ntest_group,Тестовая группа,Описание"
        )
        file = MagicMock(spec=UploadFile)
        file.read.return_value = csv_content.encode("utf-8")

        # Выполнение
        result = await file_importer.import_from_csv(mock_db, file)

        # Проверки
        assert result.success is True
        assert result.imported == 0
        assert result.skipped == 1
        assert len(result.errors) == 1
        mock_group_manager.create_group.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_from_csv_without_validation(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест импорта CSV без валидации"""
        # Настройка моков
        mock_group_manager.get_by_screen_name.return_value = (
            None  # Группа не существует
        )
        mock_group_manager.create_group.return_value = MagicMock()

        # Создание CSV файла
        csv_content = (
            "screen_name,name,description\ntest_group,Тестовая группа,Описание"
        )
        file = MagicMock(spec=UploadFile)
        file.read.return_value = csv_content.encode("utf-8")

        # Выполнение без валидации
        result = await file_importer.import_from_csv(
            mock_db, file, validate_groups=False
        )

        # Проверки
        assert result.success is True
        assert result.imported == 1
        mock_group_validator.validate_screen_name.assert_not_called()
        mock_group_manager.create_group.assert_called_once()

    # Тесты для import_from_text

    @pytest.mark.asyncio
    async def test_import_from_text_success(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест успешного импорта из текстового файла"""
        # Настройка моков
        mock_group_manager.get_by_screen_name.return_value = (
            None  # Группа не существует
        )
        mock_group_validator.validate_screen_name.return_value = (
            True  # Группа существует в VK
        )
        mock_group_validator.get_group_data_from_vk.return_value = {
            "id": 123456789,
            "screen_name": "test_group",
            "name": "Тестовая группа",
        }
        mock_group_manager.create_group.return_value = MagicMock()

        # Создание текстового файла
        text_content = "test_group\nanother_group"
        file = MagicMock(spec=UploadFile)
        file.read.return_value = text_content.encode("utf-8")

        # Выполнение
        result = await file_importer.import_from_text(mock_db, file)

        # Проверки
        assert isinstance(result, VKGroupUploadResponse)
        assert result.success is True
        assert result.imported == 2
        assert result.skipped == 0
        assert mock_group_manager.create_group.call_count == 2

    @pytest.mark.asyncio
    async def test_import_from_text_empty_file(self, file_importer, mock_db):
        """Тест импорта пустого текстового файла"""
        # Создание пустого файла
        file = MagicMock(spec=UploadFile)
        file.read.return_value = b""

        # Выполнение
        result = await file_importer.import_from_text(mock_db, file)

        # Проверки
        assert result.success is False
        assert result.imported == 0
        assert "пустой" in result.message.lower()

    @pytest.mark.asyncio
    async def test_import_from_text_with_urls(
        self, file_importer, mock_db, mock_group_manager, mock_group_validator
    ):
        """Тест импорта текста с URL групп"""
        # Настройка моков
        mock_group_manager.get_by_screen_name.return_value = None
        mock_group_validator.validate_screen_name.return_value = True
        mock_group_validator.get_group_data_from_vk.return_value = {
            "id": 123456789,
            "screen_name": "test_group",
            "name": "Тестовая группа",
        }
        mock_group_manager.create_group.return_value = MagicMock()

        # Создание файла с URL
        text_content = "https://vk.com/test_group"
        file = MagicMock(spec=UploadFile)
        file.read.return_value = text_content.encode("utf-8")

        # Выполнение
        result = await file_importer.import_from_text(mock_db, file)

        # Проверки
        assert result.success is True
        assert result.imported == 1
        mock_group_manager.create_group.assert_called_once()

    # Тесты для validate_import_data

    @pytest.mark.asyncio
    async def test_validate_import_data_success(
        self, file_importer, mock_group_validator
    ):
        """Тест успешной валидации данных для импорта"""
        # Тестовые данные
        groups_data = [
            {"screen_name": "group1", "name": "Группа 1"},
            {"screen_name": "group2", "name": "Группа 2"},
        ]

        # Настройка мока
        mock_group_validator.validate_screen_name.return_value = True

        # Выполнение
        result = await file_importer.validate_import_data(groups_data)

        # Проверки
        assert result["total"] == 2
        assert result["valid"] == 2
        assert result["invalid"] == 0
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_import_data_mixed(
        self, file_importer, mock_group_validator
    ):
        """Тест валидации данных с разными результатами"""
        # Тестовые данные
        groups_data = [
            {"screen_name": "valid_group", "name": "Валидная группа"},
            {"screen_name": "invalid_group", "name": "Невалидная группа"},
        ]

        # Настройка мока для разных результатов
        mock_group_validator.validate_screen_name.side_effect = [True, False]

        # Выполнение
        result = await file_importer.validate_import_data(groups_data)

        # Проверки
        assert result["total"] == 2
        assert result["valid"] == 1
        assert result["invalid"] == 1
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_validate_import_data_empty_screen_name(
        self, file_importer, mock_group_validator
    ):
        """Тест валидации данных с пустым screen_name"""
        # Тестовые данные
        groups_data = [
            {"screen_name": "", "name": "Группа без screen_name"},
            {"screen_name": "valid_group", "name": "Валидная группа"},
        ]

        # Настройка мока
        mock_group_validator.validate_screen_name.return_value = True

        # Выполнение
        result = await file_importer.validate_import_data(groups_data)

        # Проверки
        assert result["total"] == 2
        assert result["valid"] == 1
        assert result["invalid"] == 1
        assert len(result["errors"]) == 1
        assert "пустой screen_name" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_validate_import_data_error(
        self, file_importer, mock_group_validator
    ):
        """Тест обработки ошибки при валидации"""
        # Тестовые данные
        groups_data = [
            {"screen_name": "test_group", "name": "Тестовая группа"}
        ]

        # Настройка мока для ошибки
        mock_group_validator.validate_screen_name.side_effect = Exception(
            "Validation error"
        )

        # Выполнение
        result = await file_importer.validate_import_data(groups_data)

        # Проверки
        assert result["total"] == 1
        assert result["valid"] == 0
        assert result["invalid"] == 1
        assert len(result["errors"]) == 1
