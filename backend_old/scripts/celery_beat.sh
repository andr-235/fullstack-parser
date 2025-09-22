#!/bin/bash

# Celery Beat Scheduler Startup Script
# Best practices 2025 для запуска Celery Beat

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
    
    if [ -z "$CELERY_RESULT_BACKEND" ]; then
        warn "CELERY_RESULT_BACKEND not set, using default: redis://redis:6379/0"
        export CELERY_RESULT_BACKEND="redis://redis:6379/0"
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

# Создание директорий для логов и БД
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p /var/log/celery
    mkdir -p /var/lib/celery
    mkdir -p /var/run/celery
    
    # Устанавливаем права доступа
    chmod 755 /var/log/celery
    chmod 755 /var/lib/celery
    chmod 755 /var/run/celery
}

# Инициализация базы данных Beat
init_beat_db() {
    log "Initializing Beat database..."
    
    # Создаем пустую базу данных если её нет
    if [ ! -f /var/lib/celery/celerybeat-schedule ]; then
        touch /var/lib/celery/celerybeat-schedule
        chmod 644 /var/lib/celery/celerybeat-schedule
    fi
}

# Запуск Celery Beat
start_beat() {
    log "Starting Celery Beat scheduler..."
    
    # Параметры запуска
    BEAT_ARGS=(
        --app=src.celery_app
        --loglevel=info
        --schedule=/var/lib/celery/celerybeat-schedule
        --pidfile=/var/run/celery/beat.pid
        --logfile=/var/log/celery/beat.log
    )
    
    # Дополнительные параметры для production
    if [ "$ENVIRONMENT" = "production" ]; then
        BEAT_ARGS+=(
            --max-interval=300
        )
    fi
    
    # Запуск Beat
    exec celery beat "${BEAT_ARGS[@]}"
}

# Обработка сигналов
cleanup() {
    log "Shutting down Celery Beat..."
    
    # Удаляем PID файл
    rm -f /var/run/celery/beat.pid
    
    log "Celery Beat stopped"
}

# Установка обработчиков сигналов
trap cleanup SIGTERM SIGINT

# Основная функция
main() {
    log "Starting VK Parser Celery Beat Scheduler"
    log "Environment: ${ENVIRONMENT:-development}"
    
    # Проверки
    check_env
    check_redis
    setup_directories
    init_beat_db
    
    # Запускаем Beat
    start_beat
}

# Запуск
main "$@"
