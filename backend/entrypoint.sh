#!/bin/bash
set -e

# Применяем миграции Alembic
alembic upgrade head

# Запускаем FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
