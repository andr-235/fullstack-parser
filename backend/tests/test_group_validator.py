"""
Тесты для GroupValidator - сервиса валидации VK групп через API

Тестируемые возможности:
- Валидация screen_name через VK API
- Валидация VK ID через VK API
- Получение данных группы из VK
- Извлечение screen_name из URL
- Проверка доступа к контенту группы
- Сравнение данных с VK API
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.group_validator import GroupValidator
from app.services.vk_api_service import VKAPIService
from app.models.vk_group import VKGroup


class TestGroupValidator:
    """Тесты для GroupValidator"""

    @pytest.fixture
    def mock_vk_service(self):
        """Мок для VK API сервиса"""
        return AsyncMock(spec=VKAPIService)

    @pytest.fixture
    def group_validator(self, mock_vk_service):
        """Экземпляр GroupValidator для тестирования"""
        return GroupValidator(mock_vk_service)

    @pytest.fixture
    def sample_group(self):
        """Пример объекта группы"""
        group = MagicMock(spec=VKGroup)
        group.id = 1
        group.screen_name = "test_group"
        group.name = "Тестовая группа"
        group.vk_id = 123456789
        group.member_count = 1000
        return group

    @pytest.fixture
    def vk_group_data(self):
        """Пример данных группы из VK API"""
        return {
            "id": 123456789,
            "name": "Тестовая группа",
            "screen_name": "test_group",
            "members_count": 1000,
            "description": "Описание тестовой группы",
        }

    # Тесты для validate_screen_name

    @pytest.mark.asyncio
    async def test_validate_screen_name_success(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест успешной валидации существующего screen_name"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.validate_screen_name("test_group")

        # Проверки
        assert result is True
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    @pytest.mark.asyncio
    async def test_validate_screen_name_not_found(
        self, group_validator, mock_vk_service
    ):
        """Тест валидации несуществующего screen_name"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = None

        # Выполнение
        result = await group_validator.validate_screen_name("nonexistent")

        # Проверки
        assert result is False
        mock_vk_service.get_group_info.assert_called_once_with("nonexistent")

    @pytest.mark.asyncio
    async def test_validate_screen_name_error(
        self, group_validator, mock_vk_service
    ):
        """Тест обработки ошибки при валидации screen_name"""
        # Настройка мока для ошибки
        mock_vk_service.get_group_info.side_effect = Exception("VK API error")

        # Выполнение
        result = await group_validator.validate_screen_name("test_group")

        # Проверки
        assert result is False
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    # Тесты для validate_vk_id

    @pytest.mark.asyncio
    async def test_validate_vk_id_success(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест успешной валидации существующего VK ID"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.validate_vk_id(123456789)

        # Проверки
        assert result is True
        mock_vk_service.get_group_info.assert_called_once_with("123456789")

    @pytest.mark.asyncio
    async def test_validate_vk_id_not_found(
        self, group_validator, mock_vk_service
    ):
        """Тест валидации несуществующего VK ID"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = None

        # Выполнение
        result = await group_validator.validate_vk_id(999999999)

        # Проверки
        assert result is False
        mock_vk_service.get_group_info.assert_called_once_with("999999999")

    # Тесты для get_group_data_from_vk

    @pytest.mark.asyncio
    async def test_get_group_data_from_vk_success(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест успешного получения данных группы из VK"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.get_group_data_from_vk("test_group")

        # Проверки
        assert result == vk_group_data
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    @pytest.mark.asyncio
    async def test_get_group_data_from_vk_not_found(
        self, group_validator, mock_vk_service
    ):
        """Тест получения данных несуществующей группы из VK"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = None

        # Выполнение
        result = await group_validator.get_group_data_from_vk("nonexistent")

        # Проверки
        assert result is None
        mock_vk_service.get_group_info.assert_called_once_with("nonexistent")

    @pytest.mark.asyncio
    async def test_get_group_data_from_vk_error(
        self, group_validator, mock_vk_service
    ):
        """Тест обработки ошибки при получении данных из VK"""
        # Настройка мока для ошибки
        mock_vk_service.get_group_info.side_effect = Exception("VK API error")

        # Выполнение
        result = await group_validator.get_group_data_from_vk("test_group")

        # Проверки
        assert result is None
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    # Тесты для extract_screen_name

    @pytest.mark.asyncio
    async def test_extract_screen_name_simple(self, group_validator):
        """Тест извлечения простого screen_name"""
        result = await group_validator.extract_screen_name("test_group")
        assert result == "test_group"

    @pytest.mark.asyncio
    async def test_extract_screen_name_from_url(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест извлечения screen_name из URL"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.extract_screen_name(
            "https://vk.com/test_group"
        )

        # Проверки
        assert result == "test_group"
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    @pytest.mark.asyncio
    async def test_extract_screen_name_from_url_with_params(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест извлечения screen_name из URL с параметрами"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.extract_screen_name(
            "https://vk.com/test_group?w=wall-123456789_1"
        )

        # Проверки
        assert result == "test_group"
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    @pytest.mark.asyncio
    async def test_extract_screen_name_invalid_url(self, group_validator):
        """Тест обработки некорректного URL"""
        result = await group_validator.extract_screen_name("https://vk.com/")
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_screen_name_numeric_only(self, group_validator):
        """Тест обработки чисто числового идентификатора"""
        result = await group_validator.extract_screen_name("123456789")
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_screen_name_vk_invalid(
        self, group_validator, mock_vk_service
    ):
        """Тест обработки screen_name, которого нет в VK"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = None

        # Выполнение
        result = await group_validator.extract_screen_name("invalid_group")

        # Проверки
        assert result is None
        mock_vk_service.get_group_info.assert_called_once_with("invalid_group")

    # Тесты для validate_group_access

    @pytest.mark.asyncio
    async def test_validate_group_access_success(
        self, group_validator, mock_vk_service
    ):
        """Тест успешной проверки доступа к группе"""
        # Настройка мока
        mock_vk_service.get_group_posts.return_value = [{"id": 1}, {"id": 2}]

        # Выполнение
        result = await group_validator.validate_group_access(123456789)

        # Проверки
        assert result is True
        mock_vk_service.get_group_posts.assert_called_once_with(
            123456789, count=1
        )

    @pytest.mark.asyncio
    async def test_validate_group_access_no_access(
        self, group_validator, mock_vk_service
    ):
        """Тест проверки доступа к группе без доступа"""
        # Настройка мока
        mock_vk_service.get_group_posts.return_value = []

        # Выполнение
        result = await group_validator.validate_group_access(123456789)

        # Проверки
        assert result is False
        mock_vk_service.get_group_posts.assert_called_once_with(
            123456789, count=1
        )

    @pytest.mark.asyncio
    async def test_validate_group_access_error(
        self, group_validator, mock_vk_service
    ):
        """Тест обработки ошибки при проверке доступа"""
        # Настройка мока для ошибки
        mock_vk_service.get_group_posts.side_effect = Exception(
            "Access denied"
        )

        # Выполнение
        result = await group_validator.validate_group_access(123456789)

        # Проверки
        assert result is False
        mock_vk_service.get_group_posts.assert_called_once_with(
            123456789, count=1
        )

    # Тесты для refresh_group_data

    @pytest.mark.asyncio
    async def test_refresh_group_data_success(
        self, group_validator, mock_vk_service, sample_group, vk_group_data
    ):
        """Тест успешного обновления данных группы"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.refresh_group_data(sample_group)

        # Проверки
        assert result == vk_group_data
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    @pytest.mark.asyncio
    async def test_refresh_group_data_with_vk_id(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест обновления данных группы по VK ID (без screen_name)"""
        # Создаем группу без screen_name
        group = MagicMock(spec=VKGroup)
        group.id = 1
        group.screen_name = None
        group.vk_id = 123456789

        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.refresh_group_data(group)

        # Проверки
        assert result == vk_group_data
        mock_vk_service.get_group_info.assert_called_once_with("123456789")

    @pytest.mark.asyncio
    async def test_refresh_group_data_error(
        self, group_validator, mock_vk_service, sample_group
    ):
        """Тест обработки ошибки при обновлении данных группы"""
        # Настройка мока для ошибки
        mock_vk_service.get_group_info.side_effect = Exception("VK API error")

        # Выполнение
        result = await group_validator.refresh_group_data(sample_group)

        # Проверки
        assert result is None
        mock_vk_service.get_group_info.assert_called_once_with("test_group")

    # Тесты для compare_with_vk_data

    @pytest.mark.asyncio
    async def test_compare_with_vk_data_no_differences(
        self, group_validator, sample_group, vk_group_data
    ):
        """Тест сравнения данных без различий"""
        # Выполнение
        result = await group_validator.compare_with_vk_data(
            sample_group, vk_group_data
        )

        # Проверки
        assert result == {}
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_compare_with_vk_data_with_differences(
        self, group_validator, sample_group
    ):
        """Тест сравнения данных с различиями"""
        # Данные из VK с отличиями
        vk_data = {
            "id": 123456789,
            "name": "Новое название группы",  # Изменено
            "screen_name": "new_test_group",  # Изменено
            "members_count": 1500,  # Изменено
        }

        # Выполнение
        result = await group_validator.compare_with_vk_data(
            sample_group, vk_data
        )

        # Проверки
        assert len(result) == 3
        assert "name" in result
        assert "screen_name" in result
        assert "member_count" in result
        assert result["name"]["old"] == "Тестовая группа"
        assert result["name"]["new"] == "Новое название группы"

    @pytest.mark.asyncio
    async def test_compare_with_vk_data_missing_fields(
        self, group_validator, sample_group
    ):
        """Тест сравнения данных с отсутствующими полями"""
        # Данные из VK без некоторых полей
        vk_data = {
            "id": 123456789,
            "name": "Тестовая группа",
            # screen_name отсутствует
            # members_count отсутствует
        }

        # Выполнение
        result = await group_validator.compare_with_vk_data(
            sample_group, vk_data
        )

        # Проверки
        assert len(result) == 0  # Нет различий

    # Тесты для validate_multiple_groups

    @pytest.mark.asyncio
    async def test_validate_multiple_groups_success(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест успешной валидации нескольких групп"""
        # Настройка мока
        mock_vk_service.get_group_info.return_value = vk_group_data

        # Выполнение
        result = await group_validator.validate_multiple_groups(
            ["group1", "group2", "123456789"]
        )

        # Проверки
        assert len(result) == 3
        assert result["group1"] is True
        assert result["group2"] is True
        assert result["123456789"] is True
        assert mock_vk_service.get_group_info.call_count == 3

    @pytest.mark.asyncio
    async def test_validate_multiple_groups_mixed(
        self, group_validator, mock_vk_service, vk_group_data
    ):
        """Тест валидации нескольких групп с разными результатами"""
        # Настройка мока для разных результатов
        mock_vk_service.get_group_info.side_effect = [
            vk_group_data,  # group1 существует
            None,  # group2 не существует
            vk_group_data,  # 123456789 существует
        ]

        # Выполнение
        result = await group_validator.validate_multiple_groups(
            ["group1", "group2", "123456789"]
        )

        # Проверки
        assert len(result) == 3
        assert result["group1"] is True
        assert result["group2"] is False
        assert result["123456789"] is True

    @pytest.mark.asyncio
    async def test_validate_multiple_groups_error(
        self, group_validator, mock_vk_service
    ):
        """Тест обработки ошибки при валидации нескольких групп"""
        # Настройка мока для ошибки
        mock_vk_service.get_group_info.side_effect = Exception("VK API error")

        # Выполнение
        result = await group_validator.validate_multiple_groups(
            ["group1", "group2"]
        )

        # Проверки
        assert len(result) == 2
        assert result["group1"] is False
        assert result["group2"] is False
