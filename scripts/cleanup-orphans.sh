#!/bin/bash

# =============================================================================
# CLEANUP ORPHAN CONTAINERS SCRIPT
# =============================================================================
# Удаляет сиротские контейнеры, которые не соответствуют текущему compose файлу

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Переходим в рабочую директорию
cd /opt/app

log_info "🧹 Очистка сиротских контейнеров..."

# Получаем список всех контейнеров с именем fullstack
log_info "Поиск контейнеров с именем 'fullstack'..."
all_containers=$(docker ps -a --filter "name=fullstack" --format "{{.Names}}")

if [[ -z "$all_containers" ]]; then
    log_success "Сиротских контейнеров не найдено"
    exit 0
fi

# Получаем список контейнеров из текущего compose файла
log_info "Получение списка контейнеров из docker-compose.prod.ip.yml..."
compose_containers=$(docker compose -f docker-compose.prod.ip.yml ps --format "{{.Name}}" 2>/dev/null || echo "")

# Находим сиротские контейнеры
orphan_containers=""
for container in $all_containers; do
    if [[ ! " $compose_containers " =~ " $container " ]]; then
        orphan_containers="$orphan_containers $container"
    fi
done

if [[ -z "$orphan_containers" ]]; then
    log_success "Сиротских контейнеров не найдено"
    exit 0
fi

log_warning "Найдены сиротские контейнеры:"
for container in $orphan_containers; do
    echo "  - $container"
done

# Останавливаем и удаляем сиротские контейнеры
log_info "Остановка и удаление сиротских контейнеров..."
for container in $orphan_containers; do
    log_info "Остановка $container..."
    docker stop "$container" 2>/dev/null || true
    
    log_info "Удаление $container..."
    docker rm "$container" 2>/dev/null || true
    
    log_success "Контейнер $container удалён"
done

log_success "Очистка завершена!"

# Показываем текущий статус
log_info "Текущий статус контейнеров:"
docker compose -f docker-compose.prod.ip.yml ps 