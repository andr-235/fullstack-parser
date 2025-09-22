# Go Backend API - Docker Setup

## 🐳 Docker Configuration

Этот проект настроен для работы с Docker и Docker Compose для удобной разработки и развертывания.

## 📁 Структура файлов

```
backend/
├── Dockerfile                 # Multi-stage Dockerfile для Go приложения
├── .dockerignore             # Исключения для Docker build context
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
├── nginx.conf                # Nginx configuration
└── README.Docker.md          # Этот файл
```

## 🚀 Быстрый старт

### Development

```bash
# Клонировать репозиторий
git clone <repository-url>
cd backend

# Запустить development environment
make up

# Или напрямую через docker-compose
docker-compose up -d
```

### Production

```bash
# Запустить production environment
make prod-up

# Или напрямую через docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🛠 Доступные команды

### Основные команды

```bash
make help          # Показать все доступные команды
make up            # Запустить development environment
make down          # Остановить все сервисы
make restart       # Перезапустить все сервисы
make build         # Собрать Docker образы
```

### Мониторинг

```bash
make logs          # Просмотр логов всех сервисов
make logs-api      # Просмотр логов только API
make logs-db       # Просмотр логов базы данных
make status        # Статус сервисов
make health        # Проверка здоровья сервисов
```

### База данных

```bash
make migrate       # Запустить миграции
make backup        # Создать резервную копию БД
make backup-list   # Список резервных копий
make shell-db      # Подключиться к PostgreSQL
```

### Тестирование

```bash
make test          # Запустить тесты
make test-coverage # Запустить тесты с покрытием
```

## 🌐 Доступные сервисы

### Development

- **API**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost:80

### Production

- **API**: http://localhost:8080 (через Nginx)
- **Health Check**: http://localhost/health
- **PostgreSQL**: Внутренняя сеть
- **Redis**: Внутренняя сеть
- **Nginx**: http://localhost:80

## 🔧 Конфигурация

### Environment Variables

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Основные переменные:

- `POSTGRES_DB` - имя базы данных
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `REDIS_URL` - URL Redis
- `JWT_SECRET` - секретный ключ для JWT
- `GIN_MODE` - режим Gin (debug/release)
- `LOG_LEVEL` - уровень логирования

### Dockerfile

Использует multi-stage build:

1. **Builder stage** - компиляция Go приложения
2. **Test stage** - запуск тестов
3. **Final stage** - минимальный runtime образ

### Nginx

Настроен как reverse proxy с:
- Rate limiting
- Security headers
- Health check endpoint
- Load balancing (для production)

## 🔒 Безопасность

### Production настройки

- Приложение запускается от непривилегированного пользователя
- Минимальный Alpine образ для runtime
- Security headers в Nginx
- Rate limiting
- Health checks для всех сервисов

### Сканирование безопасности

```bash
make security-scan  # Сканирование образов на уязвимости (требует Trivy)
```

## 📊 Мониторинг

### Логи

```bash
# Все сервисы
make logs

# Конкретный сервис
make logs-api
make logs-db
make logs-nginx
```

### Health Checks

```bash
# Проверка здоровья
make health

# Статус сервисов
make status
```

## 🗄 База данных

### Миграции

```bash
make migrate  # Запустить миграции
```

### Резервное копирование

```bash
make backup           # Создать backup
make backup-list      # Список backups
make backup-restore   # Восстановить из backup
```

## 🧪 Тестирование

### Запуск тестов

```bash
# В контейнере
make test

# Локально (требует Go)
go test ./...
```

### Покрытие кода

```bash
make test-coverage
```

## 🚀 Развертывание

### Development

```bash
make up
```

### Production

```bash
make prod-up
```

### Zero-downtime deployment

```bash
make deploy
```

## 🧹 Очистка

```bash
make clean-docker     # Очистить Docker ресурсы
make clean           # Очистить проект
make clean-all       # Полная очистка
```

## 📝 Troubleshooting

### Проблемы с подключением к БД

```bash
# Проверить статус PostgreSQL
make logs-db

# Подключиться к БД
make shell-db
```

### Проблемы с Redis

```bash
# Проверить статус Redis
make logs-nginx

# Подключиться к Redis
make shell-redis
```

### Проблемы с API

```bash
# Проверить логи API
make logs-api

# Подключиться к контейнеру API
make shell-api
```

## 🔄 Обновление

```bash
# Обновить образы
docker-compose pull

# Пересобрать и перезапустить
make build
make restart
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Go Docker Best Practices](https://docs.docker.com/language/golang/)
- [Nginx Configuration](https://nginx.org/en/docs/)
