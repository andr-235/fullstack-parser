#!/usr/bin/env python3
"""
Тест новой валидации Pydantic V2
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "src"))

from parser.schemas import (
    ParseRequest,
    ParseStatus,
    VKGroupInfo,
    VKPostInfo,
    VKCommentInfo,
)
from parser.models import TaskStatus, TaskPriority
from pydantic import ValidationError
from datetime import datetime


def test_parse_request_validation():
    """Тест валидации ParseRequest"""
    print("=== Тест ParseRequest ===")

    # Валидный запрос
    try:
        valid_request = ParseRequest(
            group_ids=[-123456789, -987654321], max_posts=100, max_comments_per_post=50
        )
        print("✅ Валидный запрос прошел валидацию")
    except ValidationError as e:
        print(f"❌ Ошибка валидации валидного запроса: {e}")

    # Невалидный запрос - пустой список групп
    try:
        invalid_request = ParseRequest(
            group_ids=[], max_posts=100, max_comments_per_post=50
        )
        print("❌ Невалидный запрос прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Пустой список групп корректно отклонен")

    # Невалидный запрос - дубликаты в группах
    try:
        invalid_request = ParseRequest(
            group_ids=[-123456789, -123456789], max_posts=100, max_comments_per_post=50
        )
        print("❌ Невалидный запрос прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Дубликаты в группах корректно отклонены")

    # Невалидный запрос - превышение лимитов
    try:
        invalid_request = ParseRequest(
            group_ids=[-123456789],
            max_posts=2000,  # Превышает лимит 1000
            max_comments_per_post=50,
        )
        print("❌ Невалидный запрос прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Превышение лимитов корректно отклонено")


def test_parse_status_validation():
    """Тест валидации ParseStatus"""
    print("\n=== Тест ParseStatus ===")

    # Валидный статус
    try:
        valid_status = ParseStatus(
            task_id="test-task-123",
            status=TaskStatus.RUNNING,
            progress=50.0,
            groups_completed=5,
            groups_total=10,
            priority=TaskPriority.NORMAL,
        )
        print("✅ Валидный статус прошел валидацию")
    except ValidationError as e:
        print(f"❌ Ошибка валидации валидного статуса: {e}")

    # Невалидный статус - прогресс вне диапазона
    try:
        invalid_status = ParseStatus(
            task_id="test-task-123",
            status=TaskStatus.RUNNING,
            progress=150.0,  # Превышает 100
            groups_completed=5,
            groups_total=10,
            priority=TaskPriority.NORMAL,
        )
        print("❌ Невалидный статус прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Прогресс вне диапазона корректно отклонен")

    # Невалидный статус - завершенных групп больше общего количества
    try:
        invalid_status = ParseStatus(
            task_id="test-task-123",
            status=TaskStatus.RUNNING,
            progress=50.0,
            groups_completed=15,  # Больше groups_total
            groups_total=10,
            priority=TaskPriority.NORMAL,
        )
        print("❌ Невалидный статус прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Превышение завершенных групп корректно отклонено")


def test_vk_group_info_validation():
    """Тест валидации VKGroupInfo"""
    print("\n=== Тест VKGroupInfo ===")

    # Валидная группа
    try:
        valid_group = VKGroupInfo(
            id=123456789,
            name="Test Group",
            screen_name="test_group",
            description="Test description",
            members_count=1000,
            is_closed=False,
        )
        print("✅ Валидная группа прошла валидацию")
    except ValidationError as e:
        print(f"❌ Ошибка валидации валидной группы: {e}")

    # Невалидная группа - неправильный screen_name
    try:
        invalid_group = VKGroupInfo(
            id=123456789,
            name="Test Group",
            screen_name="test group!",  # Содержит недопустимые символы
            description="Test description",
            members_count=1000,
            is_closed=False,
        )
        print("❌ Невалидная группа прошла валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Неправильный screen_name корректно отклонен")


def test_vk_post_info_validation():
    """Тест валидации VKPostInfo"""
    print("\n=== Тест VKPostInfo ===")

    # Валидный пост
    try:
        valid_post = VKPostInfo(
            id=123456789,
            text="Test post content",
            date=datetime.now(),
            likes_count=10,
            comments_count=5,
            author_id=987654321,
        )
        print("✅ Валидный пост прошел валидацию")
    except ValidationError as e:
        print(f"❌ Ошибка валидации валидного поста: {e}")

    # Невалидный пост - пустой текст
    try:
        invalid_post = VKPostInfo(
            id=123456789,
            text="",  # Пустой текст
            date=datetime.now(),
            likes_count=10,
            comments_count=5,
            author_id=987654321,
        )
        print("❌ Невалидный пост прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Пустой текст поста корректно отклонен")


def test_vk_comment_info_validation():
    """Тест валидации VKCommentInfo"""
    print("\n=== Тест VKCommentInfo ===")

    # Валидный комментарий
    try:
        valid_comment = VKCommentInfo(
            id=123456789,
            post_id=987654321,
            text="Test comment content",
            date=datetime.now(),
            likes_count=5,
            author_id=111222333,
        )
        print("✅ Валидный комментарий прошел валидацию")
    except ValidationError as e:
        print(f"❌ Ошибка валидации валидного комментария: {e}")

    # Невалидный комментарий - пустой текст
    try:
        invalid_comment = VKCommentInfo(
            id=123456789,
            post_id=987654321,
            text="",  # Пустой текст
            date=datetime.now(),
            likes_count=5,
            author_id=111222333,
        )
        print("❌ Невалидный комментарий прошел валидацию (не должно было)")
    except ValidationError as e:
        print("✅ Пустой текст комментария корректно отклонен")


if __name__ == "__main__":
    print("Тестирование новой валидации Pydantic V2\n")

    test_parse_request_validation()
    test_parse_status_validation()
    test_vk_group_info_validation()
    test_vk_post_info_validation()
    test_vk_comment_info_validation()

    print("\n🎉 Тестирование завершено!")
