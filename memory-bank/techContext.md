# Tech Context

## Backend

- **Framework**: FastAPI
- **Language**: Python 3.11
- **Dependency Management**: Poetry 1.8.2. Проект был мигрирован с
equirements.txt.
- **Dockerfile**: Многостадийный, с отдельными целями для разработки и продакшена. Production-образ использует non-root пользователя и health checks.

## Frontend

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Dependency Management**: **pnpm**. Dockerfile использует `pnpm install --frozen-lockfile` для установки зависимостей.
- **Dockerfile**: Многостадийный, использует `output: 'standalone'` в Next.js для создания минимального production-образа. Сборка фронтенда происходит с помощью `pnpm`.

## Infrastructure

- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (в production)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
