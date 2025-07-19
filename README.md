# Fullstack Parser

Полнофункциональное приложение для парсинга и мониторинга контента VK с FastAPI backend и Next.js frontend.

## Быстрый старт

### Переключение между режимами

Проект поддерживает два режима работы:

#### Development Mode (HTTP)
```bash
# Запуск в режиме разработки (только HTTP)
./scripts/switch-env.sh dev

# Доступ: http://localhost
```

#### Production Mode (HTTPS с редиректом)
```bash
# Запуск в продакшен режиме (HTTP → HTTPS редирект)
./scripts/switch-env.sh prod

# Доступ: https://localhost (HTTP автоматически редиректится)
```

#### Проверка статуса
```bash
# Проверить текущий статус окружения
./scripts/switch-env.sh status
```

### Ручной запуск

#### Development
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Production
```bash
docker-compose up -d
```

## Архитектура

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Redis
- **Frontend**: Next.js 14 + TypeScript + TailwindCSS
- **Infrastructure**: Docker + Nginx + Docker Compose
- **CI/CD**: GitHub Actions + автоматическое развертывание

## Документация

Подробная документация находится в папке [docs/](docs/):

- [Environment Switching Guide](docs/ENVIRONMENT_SWITCHING.md) - Подробное руководство по переключению режимов
- [Getting Started](docs/GETTING_STARTED.md) - Начало работы
- [Production Setup](docs/PRODUCTION_SETUP.md) - Настройка продакшена
- [Deployment Guide](docs/GITHUB_ACTIONS_DEPLOYMENT.md) - Руководство по развертыванию

## Особенности

### Development Mode
- HTTP только (порт 80)
- Горячая перезагрузка для разработки
- Отладочная информация
- Менее строгие security headers

### Production Mode
- HTTP автоматически редиректится на HTTPS
- SSL/TLS сертификаты
- Строгие security headers
- HSTS включен
- Rate limiting
- Оптимизированная производительность

## Структура проекта

```
├── backend/           # FastAPI приложение
├── frontend/          # Next.js приложение
├── nginx/            # Nginx конфигурации
├── scripts/          # Скрипты развертывания
├── docs/             # Документация
├── docker-compose.yml           # Production конфигурация
├── docker-compose.dev.yml       # Development конфигурация
└── env.example       # Шаблон переменных окружения
```

## Переменные окружения

Скопируйте `env.example` в `.env.prod` и настройте переменные:

```bash
cp env.example .env.prod
# Отредактируйте .env.prod с вашими настройками
```

## Мониторинг

### Health Checks
- **Development**: http://localhost/health
- **Production**: https://localhost/health

### Логи
```bash
# Логи nginx
docker logs fullstack_dev_nginx

# Логи frontend
docker logs fullstack_dev_frontend

# Логи backend
docker logs fullstack_dev_backend
```

## Безопасность

- Все секреты хранятся в переменных окружения
- SSL/TLS в продакшене
- Rate limiting для API
- CORS настройки
- Security headers

## Поддержка

Для получения помощи обратитесь к документации в папке [docs/](docs/) или создайте issue в репозитории.
