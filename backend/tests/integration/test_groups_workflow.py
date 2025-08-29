"""
Интеграционные тесты для workflow работы с группами

Тестируют полный цикл:
1. Создание группы
2. Импорт групп из файла
3. Мониторинг группы
4. Получение статистики
5. Поиск комментариев
"""

import pytest
import tempfile
import csv
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.group_manager import GroupManager
from app.services.group_validator import GroupValidator
from app.services.group_file_importer import GroupFileImporter
from app.services.comment_service import CommentService
from app.services.keyword_service import KeywordService
from app.services.vk_api_service import VKAPIService


class TestGroupsWorkflow:
    """
    Интеграционные тесты для полного workflow работы с группами.
    """

    @pytest.fixture
    async def db_session(self):
        """Фикстура для сессии базы данных"""
        async with get_db_session() as session:
            yield session

    @pytest.fixture
    def vk_service(self):
        """Фикстура для VK API сервиса"""
        from app.core.config import settings

        return VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )

    @pytest.fixture
    def group_manager(self):
        """Фикстура для GroupManager"""
        return GroupManager()

    @pytest.fixture
    def group_validator(self, vk_service):
        """Фикстура для GroupValidator"""
        return GroupValidator(vk_service)

    @pytest.fixture
    def group_importer(self, group_manager, group_validator):
        """Фикстура для GroupFileImporter"""
        return GroupFileImporter(group_manager, group_validator)

    @pytest.fixture
    def comment_service(self):
        """Фикстура для CommentService"""
        return CommentService()

    @pytest.fixture
    def keyword_service(self):
        """Фикстура для KeywordService"""
        return KeywordService()

    async def test_create_group_workflow(self, db_session, group_manager):
        """Тест workflow создания группы"""
        # 1. Создаем группу
        group_data = {
            "vk_id_or_screen_name": "test_workflow_group",
            "is_active": True,
            "max_posts_to_check": 50,
        }

        group = await group_manager.create_group(db_session, group_data)
        assert group is not None
        assert group.screen_name == "test_workflow_group"
        assert group.is_active == True

        # 2. Проверяем что группа создана
        group_id = group.id
        found_group = await group_manager.get_by_id(db_session, group_id)
        assert found_group is not None
        assert found_group.id == group_id

        # 3. Обновляем группу
        update_data = {"max_posts_to_check": 100}
        updated_group = await group_manager.update_group(
            db_session, group_id, update_data
        )
        assert updated_group.max_posts_to_check == 100

        # 4. Получаем общее количество групп
        count = await group_manager.get_groups_count(db_session)
        assert count > 0

    async def test_group_import_workflow(self, db_session, group_importer):
        """Тест workflow импорта групп из CSV"""
        # 1. Создаем тестовый CSV файл
        csv_content = """screen_name,name,description
test_import_1,Test Group 1,Description 1
test_import_2,Test Group 2,Description 2
invalid_group,,Invalid description
"""

        # 2. Импортируем группы
        result = await group_importer.import_from_csv_content(
            db_session=db_session, csv_content=csv_content
        )

        # 3. Проверяем результат импорта
        assert result["status"] == "success"
        assert result["total_processed"] == 3
        assert result["created"] >= 2  # Минимум 2 группы должны создаться
        assert (
            result["skipped"] >= 1
        )  # Одна группа должна быть пропущена (invalid)

        # 4. Проверяем что группы созданы в БД
        from app.models.vk_group import VKGroup
        from sqlalchemy import select

        result = await db_session.execute(
            select(VKGroup).where(
                VKGroup.screen_name.in_(["test_import_1", "test_import_2"])
            )
        )
        groups = result.scalars().all()

        assert len(groups) >= 2
        screen_names = [g.screen_name for g in groups]
        assert "test_import_1" in screen_names
        assert "test_import_2" in screen_names

    async def test_group_validation_workflow(
        self, db_session, group_validator
    ):
        """Тест workflow валидации группы"""
        # 1. Создаем тестовую группу
        from app.models.vk_group import VKGroup

        test_group = VKGroup(
            screen_name="test_validation",
            name="Test Validation Group",
            vk_id=12345,
            is_active=True,
        )
        db_session.add(test_group)
        await db_session.commit()
        await db_session.refresh(test_group)

        # 2. Валидируем группу
        is_valid = await group_validator.validate_group(test_group)
        # Валидация может быть True или False в зависимости от VK API ответа

        # 3. Получаем данные группы из VK (mock)
        vk_data = await group_validator.refresh_group_data(test_group)
        # vk_data может быть None если VK API недоступен

        # 4. Проверяем что валидация не вызывает исключений
        assert isinstance(is_valid, bool)

    async def test_keywords_workflow(self, db_session, keyword_service):
        """Тест workflow работы с ключевыми словами"""
        # 1. Создаем ключевые слова
        keywords_data = [
            {"text": "workflow_test_1", "is_active": True, "category": "test"},
            {"text": "workflow_test_2", "is_active": True, "category": "test"},
            {
                "text": "workflow_test_3",
                "is_active": False,
                "category": "test",
            },
        ]

        # 2. Массово создаем ключевые слова
        created_keywords = []
        for kw_data in keywords_data:
            keyword = await keyword_service.create_keyword(db_session, kw_data)
            created_keywords.append(keyword)

        assert len(created_keywords) == 3

        # 3. Получаем все ключевые слова
        all_keywords = await keyword_service.get_keywords(db_session)
        assert len(all_keywords) >= 3

        # 4. Получаем только активные ключевые слова
        active_keywords = await keyword_service.get_keywords(
            db_session, active_only=True
        )
        active_count = len(
            [
                kw
                for kw in active_keywords
                if kw.text.startswith("workflow_test_")
            ]
        )
        assert active_count == 2  # Только 2 активных из 3

        # 5. Ищем ключевые слова
        search_results = await keyword_service.search_keywords(
            db_session, "workflow_test"
        )
        assert len(search_results) >= 3

    async def test_comments_workflow(
        self, db_session, comment_service, keyword_service
    ):
        """Тест workflow работы с комментариями"""
        # 1. Создаем тестовые комментарии
        from app.models.vk_comment import VKComment
        from app.models.vk_post import VKPost
        from app.models.vk_group import VKGroup
        from datetime import datetime

        # Создаем группу
        test_group = VKGroup(
            screen_name="comments_test_group",
            name="Comments Test Group",
            vk_id=54321,
            is_active=True,
        )
        db_session.add(test_group)

        # Создаем пост
        test_post = VKPost(
            group_id=1,  # Будет обновлен после создания группы
            vk_post_id=123,
            text="Test post for comments",
            published_at=datetime.utcnow(),
        )
        db_session.add(test_post)

        await db_session.commit()
        await db_session.refresh(test_group)
        await db_session.refresh(test_post)

        # Обновляем group_id в посте
        test_post.group_id = test_group.id
        await db_session.commit()

        # Создаем комментарии
        comments_data = [
            {
                "post_id": test_post.id,
                "vk_comment_id": 1,
                "text": "This is a test comment with keyword1",
                "author_name": "Test Author 1",
                "published_at": datetime.utcnow(),
                "matched_keywords_count": 1,
            },
            {
                "post_id": test_post.id,
                "vk_comment_id": 2,
                "text": "Another test comment with keyword2",
                "author_name": "Test Author 2",
                "published_at": datetime.utcnow(),
                "matched_keywords_count": 1,
            },
            {
                "post_id": test_post.id,
                "vk_comment_id": 3,
                "text": "Comment without keywords",
                "author_name": "Test Author 3",
                "published_at": datetime.utcnow(),
                "matched_keywords_count": 0,
            },
        ]

        created_comments = []
        for comment_data in comments_data:
            comment = VKComment(**comment_data)
            db_session.add(comment)
            created_comments.append(comment)

        await db_session.commit()

        # 2. Получаем комментарии
        comments = await comment_service.get_comments(db_session)
        assert len(comments) >= 3

        # 3. Ищем комментарии с ключевыми словами
        search_params = {"has_keywords": True}
        keyword_comments = await comment_service.get_comments(
            db_session, search_params=search_params
        )
        keyword_comments_count = len(
            [c for c in keyword_comments if c.matched_keywords_count > 0]
        )
        assert keyword_comments_count >= 2

        # 4. Получаем статистику комментариев
        stats = await comment_service.get_comments_stats(db_session)
        assert "total_comments" in stats
        assert "comments_with_keywords" in stats
        assert stats["total_comments"] >= 3
        assert stats["comments_with_keywords"] >= 2

    async def test_full_workflow_integration(
        self, db_session, group_manager, keyword_service, comment_service
    ):
        """Тест полной интеграции всех компонентов"""
        # 1. Создаем группу
        group = await group_manager.create_group(
            db_session,
            {
                "vk_id_or_screen_name": "full_workflow_test",
                "is_active": True,
                "max_posts_to_check": 25,
            },
        )
        assert group is not None

        # 2. Создаем ключевые слова
        keyword = await keyword_service.create_keyword(
            db_session,
            {
                "text": "integration_test",
                "is_active": True,
                "category": "integration",
            },
        )
        assert keyword is not None

        # 3. Получаем статистику
        group_count = await group_manager.get_groups_count(db_session)
        keywords_count = await keyword_service.get_keywords_count(db_session)
        comments_count = await comment_service.get_comments_count(db_session)

        # Проверяем что счетчики работают
        assert isinstance(group_count, int)
        assert isinstance(keywords_count, int)
        assert isinstance(comments_count, int)

        # 4. Проверяем что все компоненты взаимодействуют корректно
        assert group_count > 0
        assert keywords_count > 0
        # comments_count может быть 0 если нет комментариев

    async def test_error_handling_workflow(self, db_session, group_manager):
        """Тест обработки ошибок в workflow"""
        # 1. Попытка создать группу с некорректными данными
        try:
            await group_manager.create_group(
                db_session,
                {"vk_id_or_screen_name": "", "is_active": True},  # Пустое имя
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            # Ожидаем исключение
            assert "screen_name" in str(e).lower() or "name" in str(e).lower()

        # 2. Попытка получить несуществующую группу
        try:
            await group_manager.get_by_id(db_session, 99999)
            assert False, "Should have raised an exception"
        except Exception as e:
            # Ожидаем исключение
            assert (
                "not found" in str(e).lower() or "не найдена" in str(e).lower()
            )

        # 3. Попытка обновить несуществующую группу
        try:
            await group_manager.update_group(
                db_session, 99999, {"is_active": False}
            )
            assert False, "Should have raised an exception"
        except Exception as e:
            # Ожидаем исключение
            assert (
                "not found" in str(e).lower() or "не найдена" in str(e).lower()
            )

    async def test_database_transaction_workflow(
        self, db_session, group_manager
    ):
        """Тест транзакций базы данных"""
        # 1. Создаем группу в транзакции
        group_data = {
            "vk_id_or_screen_name": "transaction_test",
            "is_active": True,
        }

        # Начинаем транзакцию
        async with db_session.begin():
            group = await group_manager.create_group(db_session, group_data)
            assert group is not None

            # Проверяем что группа доступна в той же транзакции
            found_group = await group_manager.get_by_id(db_session, group.id)
            assert found_group is not None
            assert found_group.screen_name == "transaction_test"

        # После коммита транзакции группа должна быть доступна
        committed_group = await group_manager.get_by_id(db_session, group.id)
        assert committed_group is not None
        assert committed_group.screen_name == "transaction_test"
