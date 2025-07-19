---
title: Development Mode Guide
description: Полное руководство по работе в режиме разработки
date: 2025-01-15
tags: [development, docker, hot-reload]
---

# 🚀 Development Mode Guide

## Обзор

Development режим настроен для максимального удобства разработки с автоматическим hot reload для frontend и backend.

## 🎯 Основные возможности

- **Hot Reload**: Автоматическая перезагрузка при изменении кода
- **Volume Mounting**: Монтирование исходного кода в контейнеры
- **Health Checks**: Автоматическая проверка состояния сервисов
- **Logs**: Централизованное логирование
- **Database**: Локальная PostgreSQL с Redis

## 🚀 Быстрый старт

### 1. Запуск dev режима

```bash
# Основная команда
make dev

# Или напрямую
./scripts/dev.sh
```

### 2. Остановка dev режима

```bash
make dev-stop
# Или
./scripts/dev-stop.sh
```

### 3. Просмотр логов

```bash
# Все сервисы
make dev-logs

# Конкретный сервис
./scripts/dev-logs.sh backend
./scripts/dev-logs.sh frontend
```

## 📁 Структура файлов

```
├── docker-compose.dev.yml    # Конфигурация dev окружения
├── backend/
│   ├── Dockerfile.dev        # Dev Dockerfile для backend
│   └── Dockerfile           # Production Dockerfile
├── frontend/
│   └── Dockerfile.dev       # Dev Dockerfile для frontend
├── nginx/
│   ├── Dockerfile.dev       # Dev Dockerfile для nginx
│   └── nginx.dev.conf       # Dev конфигурация nginx
├── scripts/
│   ├── dev.sh              # Скрипт запуска
│   ├── dev-stop.sh         # Скрипт остановки
│   └── dev-logs.sh         # Скрипт просмотра логов
└── .env.dev                # Переменные окружения для dev
```

## 🔧 Конфигурация

### Environment Variables (.env.dev)

```bash
# Основные настройки
ENV=development
NODE_ENV=development

# База данных
DB_NAME=vk_parser
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# CORS (для разработки)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:80,http://127.0.0.1:80,http://localhost,http://127.0.0.1

# Hot Reload настройки
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true
PYTHONUNBUFFERED=1
```

### Volumes для Hot Reload

```yaml
# Backend
volumes:
  - ./backend:/app
  - /app/__pycache__
  - /app/.pytest_cache

# Frontend
volumes:
  - ./frontend:/app
  - /app/node_modules
  - /app/.next
```

## 🌐 Доступные URL

После запуска dev режима:

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1/
- **Health Check**: http://localhost/health
- **Swagger Docs**: http://localhost/api/v1/docs

## 🔄 Hot Reload

### Backend (FastAPI)

- Использует `uvicorn --reload`
- Автоматически перезагружается при изменении Python файлов
- Монтирует весь код backend в контейнер

### Frontend (Next.js)

- Использует `pnpm dev --hostname 0.0.0.0`
- Автоматически перезагружается при изменении React компонентов
- Поддерживает Fast Refresh для React компонентов

### Настройки для Linux

```bash
# В .env.dev
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true
```

## 🐛 Отладка

### Просмотр логов

```bash
# Все сервисы
make dev-logs

# Конкретный сервис
./scripts/dev-logs.sh backend
./scripts/dev-logs.sh frontend
./scripts/dev-logs.sh nginx
```

### Проверка состояния

```bash
# Статус контейнеров
docker-compose -f docker-compose.dev.yml ps

# Health checks
docker-compose -f docker-compose.dev.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Перезапуск сервиса

```bash
# Перезапуск backend
docker-compose -f docker-compose.dev.yml restart backend

# Перезапуск frontend
docker-compose -f docker-compose.dev.yml restart frontend
```

## 🧹 Очистка

### Остановка с очисткой

```bash
make dev-stop
# Выберите опции очистки при запросе
```

### Полная очистка

```bash
# Остановка всех контейнеров
docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans

# Удаление образов
docker image prune -f

# Очистка системы
docker system prune -f
```

## ⚡ Производительность

### Оптимизации

1. **Volume Mounting**: Исходный код монтируется напрямую
2. **Node Modules**: Кешируются в отдельном volume
3. **Python Cache**: Исключается из монтирования
4. **Health Checks**: Оптимизированы для быстрой проверки

### Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Логи с метриками
docker-compose -f docker-compose.dev.yml logs --timestamps
```

## 🔒 Безопасность

### Dev-специфичные настройки

- CORS разрешает все локальные адреса
- Отладочные логи включены
- Секреты для разработки (не для production)
- Отключена SSL для упрощения

### Рекомендации

1. Не используйте dev конфигурацию в production
2. Регулярно обновляйте зависимости
3. Проверяйте логи на наличие ошибок
4. Используйте .env.dev только для разработки

## 🚨 Troubleshooting

### Частые проблемы

#### 1. Hot reload не работает

```bash
# Проверьте настройки в .env.dev
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true

# Перезапустите frontend
docker-compose -f docker-compose.dev.yml restart frontend
```

#### 2. Backend не перезагружается

```bash
# Проверьте volume mounting
docker-compose -f docker-compose.dev.yml exec backend ls -la /app

# Перезапустите backend
docker-compose -f docker-compose.dev.yml restart backend
```

#### 3. Проблемы с базой данных

```bash
# Проверьте подключение
docker-compose -f docker-compose.dev.yml exec backend python -c "import psycopg2; print('DB OK')"

# Пересоздайте базу
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

#### 4. Проблемы с портами

```bash
# Проверьте занятые порты
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Остановите конфликтующие сервисы
sudo systemctl stop apache2 nginx
```

## 📚 Полезные команды

```bash
# Быстрый доступ к контейнерам
docker-compose -f docker-compose.dev.yml exec backend bash
docker-compose -f docker-compose.dev.yml exec frontend sh
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres

# Просмотр файлов в контейнере
docker-compose -f docker-compose.dev.yml exec backend ls -la /app
docker-compose -f docker-compose.dev.yml exec frontend ls -la /app

# Проверка переменных окружения
docker-compose -f docker-compose.dev.yml exec backend env | grep DB
docker-compose -f docker-compose.dev.yml exec frontend env | grep NEXT
```

## 🎯 Best Practices

1. **Регулярные коммиты**: Делайте коммиты после каждого значимого изменения
2. **Тестирование**: Запускайте тесты перед коммитом
3. **Логирование**: Следите за логами при разработке
4. **Очистка**: Регулярно очищайте неиспользуемые ресурсы
5. **Документация**: Обновляйте документацию при изменении конфигурации

## 🔗 Связанные документы

- [Project Architecture](./PROJECT_ARCHITECTURE.md)
- [Docker Deployment](./DOCKER_DEPLOYMENT.md)
- [Testing Standards](./TESTING_STANDARDS.md)
- [Security Guidelines](./SECURITY_GUIDELINES.md) 