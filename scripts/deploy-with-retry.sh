#!/bin/bash

# Скрипт для деплоя с retry логикой и увеличенными таймаутами
# Использование: ./scripts/deploy-with-retry.sh [service_name]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Проверяем наличие docker-compose файла
if [ ! -f "docker-compose.prod.ip.yml" ]; then
    error "Файл docker-compose.prod.ip.yml не найден!"
    exit 1
fi

# Проверяем наличие .env.prod
if [ ! -f ".env.prod" ]; then
    error "Файл .env.prod не найден!"
    exit 1
fi

# Функция для деплоя с retry
deploy_with_retry() {
    local service=$1
    local max_retries=3
    local retry_count=0

    log "Начинаем деплой сервиса: $service"

    while [ $retry_count -lt $max_retries ]; do
        log "Попытка $((retry_count + 1)) из $max_retries"

        if docker-compose -f docker-compose.prod.ip.yml up -d --build $service; then
            log "✅ Деплой сервиса $service успешно завершён!"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                warn "Деплой не удался. Ожидание перед повторной попыткой..."
                sleep 30
            fi
        fi
    done

    error "❌ Деплой сервиса $service не удался после $max_retries попыток"
    return 1
}

# Функция для проверки здоровья сервиса
check_service_health() {
    local service=$1
    local max_attempts=10
    local attempt=0

    log "Проверяем здоровье сервиса: $service"

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.prod.ip.yml ps $service | grep -q "Up"; then
            log "✅ Сервис $service запущен"
            return 0
        fi

        attempt=$((attempt + 1))
        if [ $attempt -lt $max_attempts ]; then
            warn "Сервис $service ещё не готов. Ожидание..."
            sleep 10
        fi
    done

    error "❌ Сервис $service не запустился в течение ожидаемого времени"
    return 1
}

# Основная логика
main() {
    log "🚀 Начинаем деплой с retry логикой"

    # Останавливаем все сервисы
    log "Останавливаем существующие сервисы..."
    docker-compose -f docker-compose.prod.ip.yml down --remove-orphans

    # Очищаем неиспользуемые образы и контейнеры
    log "Очищаем неиспользуемые ресурсы..."
    docker system prune -f

    # Если указан конкретный сервис
    if [ -n "$1" ]; then
        deploy_with_retry "$1"
        check_service_health "$1"
    else
        # Деплоим все сервисы по порядку
        log "Деплоим все сервисы..."

        # Сначала база данных и Redis
        deploy_with_retry "postgres"
        check_service_health "postgres"

        deploy_with_retry "redis"
        check_service_health "redis"

        # Затем backend и worker
        deploy_with_retry "backend"
        check_service_health "backend"

        deploy_with_retry "arq-worker"
        check_service_health "arq-worker"

        # Затем frontend
        deploy_with_retry "frontend"
        check_service_health "frontend"

        # И наконец nginx
        deploy_with_retry "nginx"
        check_service_health "nginx"
    fi

    log "🎉 Деплой завершён!"

    # Показываем статус всех сервисов
    log "Статус сервисов:"
    docker-compose -f docker-compose.prod.ip.yml ps
}

# Запускаем основную функцию
main "$@"
