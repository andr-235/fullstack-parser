# Multi-stage Dockerfile для VK Comments Parser
FROM python:3.11-slim as base

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Python настройки
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Development stage
FROM base as development

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Expose port
EXPOSE 8000

# Development команда
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Создаем non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY --chown=appuser:appuser . .

# Переключаемся на non-root пользователя
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production команда
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 