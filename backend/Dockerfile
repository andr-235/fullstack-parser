# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
# По умолчанию ставим все зависимости (и dev, и main)
ARG INSTALL_DEV=true
RUN poetry config virtualenvs.create false && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        poetry install --no-root; \
    else \
        poetry install --only=main --no-root; \
    fi

COPY . .

# Stage 2: Development
FROM python:3.13-slim AS dev
WORKDIR /app


COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

USER root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM python:3.13-slim AS production
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
