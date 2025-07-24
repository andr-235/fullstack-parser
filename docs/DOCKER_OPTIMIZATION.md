# Docker Optimization Guide

## Обзор оптимизаций

Этот документ описывает оптимизации, примененные к Docker файлам и Docker Compose конфигурациям проекта для улучшения производительности, безопасности и удобства использования.

## Основные улучшения

### 1. Multi-stage Builds

#### Frontend (Next.js)

- **Stage 1 (deps)**: Установка зависимостей с кешированием
- **Stage 2 (builder)**: Сборка приложения с оптимизированным кешем
- **Stage 3 (runner)**: Минимальный runtime образ

#### Backend (FastAPI)

- **Stage 1 (deps)**: Установка системных и Python зависимостей
- **Stage 2 (builder)**: Копирование кода приложения
- **Stage 3 (production)**: Минимальный runtime образ

### 2. Безопасность

#### Непривилегированные пользователи

```dockerfile
# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Переключение на непривилегированного пользователя
USER nextjs
```

#### Безопасные настройки в Docker Compose

```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp:noexec,nosuid,size=100m
```

### 3. Производительность

#### Кеширование слоев

- Пиннинг версий образов с SHA256
- Оптимизированный порядок команд в Dockerfile
- Использование BuildKit для параллельной сборки

#### Оптимизация размера образов

- Удаление кеша пакетных менеджеров
- Объединение RUN команд
- Использование .dockerignore

### 4. Мониторинг и здоровье

#### Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### Логирование

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "production_status"
    env: "os,customer"
```

## Оптимизированные файлы

### Dockerfile'ы

#### Frontend (`frontend/Dockerfile`)

- ✅ Multi-stage build с 3 этапами
- ✅ Кеширование зависимостей
- ✅ Непривилегированный пользователь
- ✅ Health checks
- ✅ Оптимизированные переменные окружения
- ✅ dumb-init для правильной обработки сигналов

#### Backend (`backend/Dockerfile`)

- ✅ Multi-stage build с 3 этапами
- ✅ Оптимизированная установка Poetry
- ✅ Минимальный runtime образ
- ✅ Безопасные настройки
- ✅ Health checks
- ✅ dumb-init для правильной обработки сигналов

### Docker Compose файлы

#### Production (`docker-compose.yml`)

- ✅ Пиннинг версий образов
- ✅ Ограничения ресурсов
- ✅ Безопасные настройки
- ✅ Оптимизированные тома
- ✅ Изолированные сети
- ✅ Restart policies

#### Development (`docker-compose.dev.yml`)

- ✅ Hot reload для разработки
- ✅ Отладочные порты
- ✅ Инструменты разработки (Adminer, MailHog, Redis Commander)
- ✅ Оптимизированные тома для разработки

### Вспомогательные файлы

#### .dockerignore

- ✅ Исключение ненужных файлов
- ✅ Оптимизация контекста сборки
- ✅ Исключение кешей и временных файлов

#### Makefile

- ✅ Цветной вывод
- ✅ Команды для разработки и продакшена
- ✅ Мониторинг и диагностика
- ✅ Резервное копирование
- ✅ Оптимизация образов

#### Скрипт оптимизации (`scripts/optimize-docker.sh`)

- ✅ Анализ образов
- ✅ Сканирование уязвимостей
- ✅ Мониторинг ресурсов
- ✅ Генерация отчетов

## Команды для использования

### Быстрый старт

```bash
# Разработка
make dev

# Продакшен
make prod

# Остановка
make stop
make stop-prod
```

### Сборка

```bash
# Сборка для разработки
make build-dev

# Сборка для продакшена
make build-prod

# Сборка без кеша
make build
```

### Мониторинг

```bash
# Статус сервисов
make status
make status-prod

# Логи
make logs
make logs-prod

# Здоровье
make health
make health-prod
```

### Оптимизация

```bash
# Очистка
make clean
make prune

# Анализ образов
./scripts/optimize-docker.sh analyze

# Полная оптимизация
./scripts/optimize-docker.sh all
```

## Рекомендации по использованию

### 1. Регулярная очистка

```bash
# Еженедельно
make clean

# Ежемесячно
./scripts/optimize-docker.sh optimize
```

### 2. Мониторинг ресурсов

```bash
# Регулярно проверяйте использование ресурсов
make monitor-resources

# Или через скрипт
./scripts/optimize-docker.sh monitor
```

### 3. Сканирование уязвимостей

```bash
# Перед деплоем в продакшен
./scripts/optimize-docker.sh scan
```

### 4. Резервное копирование

```bash
# Регулярные бэкапы
make backup
make backup-prod
```

## Метрики производительности

### Ожидаемые улучшения

#### Размер образов

- **Frontend**: Уменьшение на 30-40%
- **Backend**: Уменьшение на 50-60%

#### Время сборки

- **Первая сборка**: Без изменений
- **Повторная сборка**: Ускорение на 60-80%

#### Безопасность

- ✅ Непривилегированные пользователи
- ✅ Read-only файловые системы
- ✅ Ограничения ресурсов
- ✅ Сканирование уязвимостей

#### Мониторинг

- ✅ Health checks для всех сервисов
- ✅ Структурированное логирование
- ✅ Метрики использования ресурсов

## Troubleshooting

### Проблемы с правами доступа

```bash
# Проверка прав пользователей
docker-compose exec backend id
docker-compose exec frontend id
```

### Проблемы с памятью

```bash
# Мониторинг использования памяти
make monitor-resources

# Увеличение лимитов в docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Проблемы с сетью

```bash
# Проверка сетевых настроек
docker network ls
docker network inspect prod-network
```

## Дополнительные ресурсы

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Docker Performance](https://docs.docker.com/config/containers/resource_constraints/)
- [Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/multistage-build/)

## Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs`
2. Проверьте здоровье: `make health`
3. Запустите диагностику: `./scripts/optimize-docker.sh all`
4. Создайте issue с подробным описанием проблемы
