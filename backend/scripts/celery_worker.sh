#!/bin/bash

# Celery Worker Startup Script
# Best practices 2025: безопасный запуск воркера с мониторингом

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

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Проверка переменных окружения
check_env() {
    log "Проверка переменных окружения..."
    
    if [ -z "$CELERY_BROKER_URL" ]; then
        error "CELERY_BROKER_URL не установлена"
        exit 1
    fi
    
    if [ -z "$CELERY_RESULT_BACKEND" ]; then
        error "CELERY_RESULT_BACKEND не установлена"
        exit 1
    fi
    
    log "Переменные окружения проверены ✓"
}

# Проверка подключения к Redis
check_redis() {
    log "Проверка подключения к Redis..."
    
    # Простая проверка через redis-cli если доступен
    if command -v redis-cli &> /dev/null; then
        if ! redis-cli -u "$CELERY_BROKER_URL" ping &> /dev/null; then
            error "Не удается подключиться к Redis: $CELERY_BROKER_URL"
            exit 1
        fi
        log "Redis подключение проверено ✓"
    else
        warn "redis-cli не найден, пропускаем проверку Redis"
    fi
}

# Настройка параметров воркера
setup_worker_params() {
    # Базовые параметры
    WORKER_PARAMS=(
        "--app=src.shared.infrastructure.task_queue.celery_app:app"
        "--loglevel=info"
        "--concurrency=4"
        "--max-tasks-per-child=100"
        "--time-limit=300"
        "--soft-time-limit=240"
        "--without-gossip"
        "--without-mingle"
        "--without-heartbeat"
    )
    
    # Дополнительные параметры для продакшена
    if [ "${ENVIRONMENT:-development}" = "production" ]; then
        WORKER_PARAMS+=(
            "--optimization=fair"
            "--prefetch-multiplier=1"
            "--task-acks-late"
            "--worker-disable-rate-limits"
        )
        log "Настроены параметры для продакшена"
    else
        WORKER_PARAMS+=(
            "--reload"
            "--debug"
        )
        log "Настроены параметры для разработки"
    fi
    
    # Очереди
    if [ -n "$CELERY_QUEUES" ]; then
        WORKER_PARAMS+=("--queues=$CELERY_QUEUES")
    else
        WORKER_PARAMS+=("--queues=vk_parser")
    fi
    
    log "Параметры воркера: ${WORKER_PARAMS[*]}"
}

# Обработка сигналов для graceful shutdown
setup_signal_handlers() {
    trap 'log "Получен сигнал завершения, останавливаем воркер..."; exit 0' SIGTERM SIGINT
}

# Основная функция
main() {
    log "Запуск Celery Worker (Best Practices 2025)"
    log "=========================================="
    
    # Проверки
    check_env
    check_redis
    setup_worker_params
    setup_signal_handlers
    
    # Переход в директорию проекта
    cd "$(dirname "$0")/.."
    
    log "Запуск воркера с параметрами: ${WORKER_PARAMS[*]}"
    
    # Запуск воркера
    exec celery worker "${WORKER_PARAMS[@]}"
}

# Запуск
main "$@"