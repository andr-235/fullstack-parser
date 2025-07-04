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
- **Dependency Management**: **Конфликт!**
    - docker-compose.yml указывает на использование **Bun** (через том .bun).
    - frontend/Dockerfile использует **pnpm** и ссылается на удаленный pnpm-lock.yaml.
    - **Вывод**: Сборка фронтенда в Docker сломана. Требуется синхронизация Dockerfile с использованием Bun.

## Infrastructure

- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (в production)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7