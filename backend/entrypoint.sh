#!/bin/bash
set -e

# Применяем миграции Alembic
poetry run alembic upgrade head

# Запускаем FastAPI
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
