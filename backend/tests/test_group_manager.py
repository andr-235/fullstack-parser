"""
Тесты для GroupManager - сервиса управления VK группами

Тестируемые возможности:
- Создание, обновление, удаление групп
- Поиск групп по различным критериям
- Получение статистики
- Управление статусом активности
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.group_manager import GroupManager
from app.models.vk_group import VKGroup
from app.schemas.vk_group import VKGroupCreate, VKGroupUpdate


class TestGroupManager:
    """Тесты для GroupManager"""

    @pytest.fixture
    def mock_db(self):
        """Мок для базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def group_manager(self):
        """Экземпляр GroupManager для тестирования"""
        return GroupManager()

    @pytest.fixture
    def sample_group_data(self):
        """Пример данных группы для создания"""
        return VKGroupCreate(
            screen_name="test_group",
            name="Тестовая группа",
            vk_id=123456789,
            description="Описание тестовой группы",
        )

    @pytest.fixture
    def sample_group(self):
        """Пример объекта группы"""
        group = MagicMock(spec=VKGroup)
        group.id = 1
        group.screen_name = "test_group"
        group.name = "Тестовая группа"
        group.vk_id = 123456789
        group.is_active = True
        return group

    # Тесты для get_by_screen_name

    @pytest.mark.asyncio
    async def test_get_by_screen_name_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного получения группы по screen_name"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_by_screen_name(mock_db, "test_group")

        # Проверки
        assert result == sample_group
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_screen_name_not_found(self, group_manager, mock_db):
        """Тест получения несуществующей группы по screen_name"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_by_screen_name(mock_db, "nonexistent")

        # Проверки
        assert result is None
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_screen_name_error(self, group_manager, mock_db):
        """Тест обработки ошибки при получении группы по screen_name"""
        # Настройка мока для ошибки
        mock_db.execute.side_effect = Exception("Database error")

        # Выполнение
        result = await group_manager.get_by_screen_name(mock_db, "test_group")

        # Проверки
        assert result is None
        mock_db.execute.assert_called_once()

    # Тесты для get_by_vk_id

    @pytest.mark.asyncio
    async def test_get_by_vk_id_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного получения группы по VK ID"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_by_vk_id(mock_db, 123456789)

        # Проверки
        assert result == sample_group
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_vk_id_not_found(self, group_manager, mock_db):
        """Тест получения несуществующей группы по VK ID"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_by_vk_id(mock_db, 999999999)

        # Проверки
        assert result is None
        mock_db.execute.assert_called_once()

    # Тесты для get_active_groups

    @pytest.mark.asyncio
    async def test_get_active_groups_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного получения активных групп"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_active_groups(mock_db)

        # Проверки
        assert result == [sample_group]
        assert len(result) == 1
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_groups_with_pagination(
        self, group_manager, mock_db, sample_group
    ):
        """Тест получения активных групп с пагинацией"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_active_groups(
            mock_db, limit=5, offset=10
        )

        # Проверки
        assert result == [sample_group]
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_groups_empty(self, group_manager, mock_db):
        """Тест получения пустого списка активных групп"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_active_groups(mock_db)

        # Проверки
        assert result == []
        mock_db.execute.assert_called_once()

    # Тесты для get_groups_count

    @pytest.mark.asyncio
    async def test_get_groups_count_active_only(self, group_manager, mock_db):
        """Тест получения количества активных групп"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_groups_count(
            mock_db, active_only=True
        )

        # Проверки
        assert result == 42
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_groups_count_all(self, group_manager, mock_db):
        """Тест получения общего количества групп"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 100
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.get_groups_count(
            mock_db, active_only=False
        )

        # Проверки
        assert result == 100
        mock_db.execute.assert_called_once()

    # Тесты для create_group

    @pytest.mark.asyncio
    async def test_create_group_success(
        self, group_manager, mock_db, sample_group_data
    ):
        """Тест успешного создания группы"""
        # Настройка моков
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = (
            None  # Группа не существует
        )
        mock_db.execute.return_value = mock_result

        # Мокаем создание группы
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Выполнение
        result = await group_manager.create_group(mock_db, sample_group_data)

        # Проверки
        assert result.screen_name == sample_group_data.screen_name
        assert result.name == sample_group_data.name
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_group_already_exists(
        self, group_manager, mock_db, sample_group_data, sample_group
    ):
        """Тест создания группы, которая уже существует"""
        # Настройка мока - группа уже существует
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result

        # Выполнение и проверка исключения
        with pytest.raises(ValueError, match="already exists"):
            await group_manager.create_group(mock_db, sample_group_data)

        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    # Тесты для update_group

    @pytest.mark.asyncio
    async def test_update_group_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного обновления группы"""
        # Настройка моков
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Данные для обновления
        update_data = VKGroupUpdate(name="Новое название")

        # Выполнение
        result = await group_manager.update_group(mock_db, 1, update_data)

        # Проверки
        assert result == sample_group
        assert result.name == "Новое название"  # Должно быть обновлено
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_group_not_found(self, group_manager, mock_db):
        """Тест обновления несуществующей группы"""
        # Настройка мока - группа не найдена
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Данные для обновления
        update_data = VKGroupUpdate(name="Новое название")

        # Выполнение
        result = await group_manager.update_group(mock_db, 999, update_data)

        # Проверки
        assert result is None
        mock_db.commit.assert_not_called()

    # Тесты для delete_group

    @pytest.mark.asyncio
    async def test_delete_group_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного удаления группы"""
        # Настройка моков
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        # Выполнение
        result = await group_manager.delete_group(mock_db, 1)

        # Проверки
        assert result is True
        mock_db.delete.assert_called_once_with(sample_group)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_group_not_found(self, group_manager, mock_db):
        """Тест удаления несуществующей группы"""
        # Настройка мока - группа не найдена
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.delete_group(mock_db, 999)

        # Проверки
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

    # Тесты для toggle_group_status

    @pytest.mark.asyncio
    async def test_toggle_group_status_active_to_inactive(
        self, group_manager, mock_db, sample_group
    ):
        """Тест переключения статуса активной группы на неактивную"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Группа изначально активна
        sample_group.is_active = True

        # Выполнение
        result = await group_manager.toggle_group_status(mock_db, 1)

        # Проверки
        assert result == sample_group
        assert result.is_active == False  # Должно стать неактивной
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_toggle_group_status_inactive_to_active(
        self, group_manager, mock_db, sample_group
    ):
        """Тест переключения статуса неактивной группы на активную"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_group
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # Группа изначально неактивна
        sample_group.is_active = False

        # Выполнение
        result = await group_manager.toggle_group_status(mock_db, 1)

        # Проверки
        assert result == sample_group
        assert result.is_active == True  # Должно стать активной
        mock_db.commit.assert_called_once()

    # Тесты для search_groups

    @pytest.mark.asyncio
    async def test_search_groups_success(
        self, group_manager, mock_db, sample_group
    ):
        """Тест успешного поиска групп"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1  # Общее количество
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.search_groups(mock_db, "test")

        # Проверки
        assert result == [sample_group]
        assert len(result) == 1
        mock_db.execute.assert_called()  # Вызывается дважды: для count и для данных

    @pytest.mark.asyncio
    async def test_search_groups_empty_query(
        self, group_manager, mock_db, sample_group
    ):
        """Тест поиска групп с пустым запросом"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.search_groups(mock_db, "")

        # Проверки
        assert result == [sample_group]
        mock_db.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_groups_no_results(self, group_manager, mock_db):
        """Тест поиска групп без результатов"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.search_groups(mock_db, "nonexistent")

        # Проверки
        assert result == []
        mock_db.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_groups_with_category(
        self, group_manager, mock_db, sample_group
    ):
        """Тест поиска групп по категории"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.search_groups(
            mock_db, "test", active_only=False
        )

        # Проверки
        assert result == [sample_group]
        mock_db.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_groups_with_pagination(
        self, group_manager, mock_db, sample_group
    ):
        """Тест поиска групп с пагинацией"""
        # Настройка мока
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_result.scalars.return_value.all.return_value = [sample_group]
        mock_db.execute.return_value = mock_result

        # Выполнение
        result = await group_manager.search_groups(
            mock_db, "test", limit=10, offset=5
        )

        # Проверки
        assert result == [sample_group]
        mock_db.execute.assert_called()
