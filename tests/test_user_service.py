import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.mark.asyncio
def test_create_user(monkeypatch):
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    user_service = UserService()
    user_in = UserCreate(
        email="test@example.com",
        full_name="Test User",
        password="123456",
        is_active=True,
        is_superuser=False,
    )
    # Мокаем get_password_hash
    monkeypatch.setattr("app.core.hashing.get_password_hash", lambda pwd: "hashed")
    user = (
        pytest.run(asyncio.run(user_service.create(db, obj_in=user_in)))
        if hasattr(pytest, "run")
        else None
    )
    db.add.assert_called()
    db.commit.assert_awaited()
    db.refresh.assert_awaited()
