# Docker Troubleshooting Guide

## Проблемы с визуалом и сетью Docker

### Быстрое исправление проблем с контейнерами:

```bash
# 1. Полная очистка
docker-compose down -v --remove-orphans
docker system prune -a -f
docker network prune -f

# 2. Пересборка с увеличенным таймаутом
COMPOSE_HTTP_TIMEOUT=300 docker-compose up -d --build --force-recreate

# 3. Проверка статуса
docker ps -a
docker-compose logs frontend --tail 20
```

### Альтернативный локальный запуск:

```bash
# Frontend (Bun)
cd frontend
bun install
bun dev

# Backend (FastAPI)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Распространенные проблемы:

1. **Network conflicts** - Выполните `docker network prune -f`
2. **Build timeouts** - Используйте `COMPOSE_HTTP_TIMEOUT=300`
3. **Volume conflicts** - Удалите volumes с `-v` флагом
4. **Cache issues** - Используйте `--no-cache` при build

### Мониторинг:

```bash
# Логи всех сервисов
docker-compose logs -f

# Использование ресурсов
docker stats

# Проверка сети
docker network ls
docker network inspect fullstack-parser_app-network
```
