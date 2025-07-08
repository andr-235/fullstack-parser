# Stage 1: Build dependencies with uv
FROM python:3.13-slim AS builder
WORKDIR /app

# Системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl git libpq-dev && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv только для build
RUN pip install uv

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock* ./

# Устанавливаем poetry последней версии 2.1.3 и плагин poetry-plugin-export
RUN pip install --no-cache-dir poetry==2.1.3 poetry-plugin-export

# Экспортируем зависимости poetry в requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# Устанавливаем зависимости через uv
RUN uv pip install --system --no-deps --requirements requirements.txt

# Копируем весь проект (для миграций, alembic и т.д.)
COPY . .

# Stage 2: Production image (без poetry/uv/pip)
FROM python:3.13-slim AS production
WORKDIR /app

# Системные зависимости для рантайма
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev git curl && rm -rf /var/lib/apt/lists/*

# Создаем non-root пользователя
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Копируем установленные библиотеки из builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY --from=builder /app /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]