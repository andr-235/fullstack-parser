#!/bin/bash

# Celery Flower Monitoring Startup Script
# Best practices 2025 для запуска Flower

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Проверка переменных окружения
check_env() {
    log "Checking environment variables..."
    
    if [ -z "$CELERY_BROKER_URL" ]; then
        warn "CELERY_BROKER_URL not set, using default: redis://redis:6379/0"
        export CELERY_BROKER_URL="redis://redis:6379/0"
    fi
    
    if [ -z "$FLOWER_PORT" ]; then
        warn "FLOWER_PORT not set, using default: 5555"
        export FLOWER_PORT=5555
    fi
    
    if [ -z "$FLOWER_HOST" ]; then
        warn "FLOWER_HOST not set, using default: 0.0.0.0"
        export FLOWER_HOST="0.0.0.0"
    fi
    
    if [ -z "$FLOWER_BASIC_AUTH" ]; then
        warn "FLOWER_BASIC_AUTH not set, using default: admin:admin"
        export FLOWER_BASIC_AUTH="admin:admin"
    fi
}

# Проверка подключения к Redis
check_redis() {
    log "Checking Redis connection..."
    
    python3 -c "
import redis
import sys
try:
    r = redis.from_url('$CELERY_BROKER_URL')
    r.ping()
    print('Redis connection: OK')
except Exception as e:
    print(f'Redis connection failed: {e}')
    sys.exit(1)
" || {
        error "Cannot connect to Redis at $CELERY_BROKER_URL"
        exit 1
    }
}

# Проверка установки Flower
check_flower() {
    log "Checking Flower installation..."
    
    python3 -c "
import flower
print('Flower version:', flower.__version__)
" || {
        error "Flower is not installed. Install with: pip install flower"
        exit 1
    }
}

# Создание директорий для логов
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p /var/log/celery
    mkdir -p /var/run/celery
    
    # Устанавливаем права доступа
    chmod 755 /var/log/celery
    chmod 755 /var/run/celery
}

# Запуск Flower
start_flower() {
    log "Starting Flower monitoring..."
    
    # Параметры запуска
    FLOWER_ARGS=(
        --app=src.celery_app
        --broker=$CELERY_BROKER_URL
        --port=$FLOWER_PORT
        --address=$FLOWER_HOST
        --basic_auth=$FLOWER_BASIC_AUTH
        --logfile=/var/log/celery/flower.log
        --pidfile=/var/run/celery/flower.pid
        --persistent=True
        --db=/var/lib/celery/flower.db
        --max_tasks=10000
        --auto_refresh=True
        --enable_events=True
    )
    
    # Дополнительные параметры для production
    if [ "$ENVIRONMENT" = "production" ]; then
        FLOWER_ARGS+=(
            --url_prefix=/flower
            --max_workers=500
            --purge_offline_workers=3600
        )
    fi
    
    # Запуск Flower
    exec celery flower "${FLOWER_ARGS[@]}"
}

# Обработка сигналов
cleanup() {
    log "Shutting down Flower..."
    
    # Удаляем PID файл
    rm -f /var/run/celery/flower.pid
    
    log "Flower stopped"
}

# Установка обработчиков сигналов
trap cleanup SIGTERM SIGINT

# Основная функция
main() {
    log "Starting VK Parser Celery Flower Monitoring"
    log "Environment: ${ENVIRONMENT:-development}"
    log "Flower URL: http://${FLOWER_HOST:-0.0.0.0}:${FLOWER_PORT:-5555}"
    
    # Проверки
    check_env
    check_redis
    check_flower
    setup_directories
    
    # Создаем директорию для БД Flower
    mkdir -p /var/lib/celery
    
    # Запускаем Flower
    start_flower
}

# Запуск
main "$@"
