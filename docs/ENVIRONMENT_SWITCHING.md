---
title: "Environment Switching Guide"
description: "How to switch between development and production environments"
date: "2025-01-15"
tags: ["deployment", "docker", "nginx", "ssl"]
---

# Переключение между окружениями

## Обзор

Проект поддерживает несколько окружений:
- **Development** - для локальной разработки
- **Production** - для продакшн развертывания
- **Staging** - для тестирования перед продакшном

## Файлы конфигурации

### Development (.env.dev)
```bash
# Основные настройки для разработки
ENV=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:80,http://127.0.0.1:80
NEXT_PUBLIC_API_URL=http://localhost
LOG_LEVEL=DEBUG
```

### Production (.env.prod)
```bash
# Настройки для продакшена
ENV=production
CORS_ORIGINS=["https://parser.mysite.ru"]
NEXT_PUBLIC_API_URL=https://parser.mysite.ru
LOG_LEVEL=INFO
```

## Быстрое переключение

### В режим разработки
```bash
# Используя скрипт
./scripts/switch-to-dev.sh

# Или с очисткой
./scripts/switch-to-dev.sh --clean
```

### В режим продакшена
```bash
# Используя существующий скрипт
./scripts/deploy-production.sh
```

## Ручное переключение

### Development Mode
```bash
# Остановить текущие контейнеры
docker-compose down

# Запустить в режиме разработки
docker-compose -f docker-compose.dev.yml up -d
```

### Production Mode
```bash
# Остановить контейнеры разработки
docker-compose -f docker-compose.dev.yml down

# Запустить продакшн
docker-compose up -d
```

## Проверка текущего режима

### Проверка переменных окружения
```bash
# В контейнере backend
docker exec fullstack_dev_backend env | grep ENV
docker exec fullstack_dev_backend env | grep CORS_ORIGINS
```

### Проверка логов
```bash
# Логи backend
docker logs fullstack_dev_backend | grep "ENV\|CORS"

# Логи frontend
docker logs fullstack_dev_frontend | grep "NODE_ENV"
```

## Особенности каждого режима

### Development
- CORS разрешен для всех локальных адресов
- Отладочная информация включена
- Горячая перезагрузка
- Менее строгие security headers

### Production
- Строгие security headers
- HSTS включен
- CORS ограничен доменами
- Rate limiting включен
- SSL/TLS 1.2+ только

## Устранение проблем

### CORS ошибки
Если видите CORS ошибки в консоли браузера:

1. Проверьте текущий режим:
```bash
docker exec fullstack_dev_backend env | grep CORS_ORIGINS
```

2. Убедитесь что используется правильный .env файл:
```bash
# Для разработки должен быть .env.dev
# Для продакшена должен быть .env.prod
```

3. Перезапустите сервисы:
```bash
docker-compose -f docker-compose.dev.yml restart backend frontend
```

### Проблемы с базой данных
```bash
# Проверьте подключение к БД
docker exec fullstack_dev_backend python -c "
from app.core.database import get_db
import asyncio
async def test():
    async for db in get_db():
        await db.execute('SELECT 1')
        print('DB connection OK')
        break
asyncio.run(test())
"
```

### Проблемы с Redis
```bash
# Проверьте подключение к Redis
docker exec fullstack_dev_redis redis-cli ping
```

## Создание новых окружений

### Создание .env.dev
```bash
# Скопируйте шаблон
cp env.example .env.dev

# Отредактируйте настройки
nano .env.dev
```

### Создание .env.staging
```bash
# Скопируйте продакшн конфигурацию
cp .env.prod .env.staging

# Измените настройки для staging
nano .env.staging
```

## Безопасность

- Никогда не коммитьте .env файлы в git
- Используйте разные секреты для разных окружений
- Регулярно ротируйте секреты
- Проверяйте права доступа к файлам конфигурации 