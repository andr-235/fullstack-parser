#!/bin/bash

# Docker и Docker Compose утилиты
# Автор: Андрей
# Версия: 1.0.0

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции логирования
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

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon не запущен или нет прав доступа"
        exit 1
    fi
    
    log_success "Docker доступен"
}

# Проверка наличия Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose не установлен"
        exit 1
    fi
    
    log_success "Docker Compose доступен"
}

# Очистка неиспользуемых ресурсов Docker
cleanup_docker() {
    log_info "Очистка неиспользуемых Docker ресурсов..."
    
    # Остановка и удаление неиспользуемых контейнеров
    docker container prune -f
    
    # Удаление неиспользуемых образов
    docker image prune -f
    
    # Удаление неиспользуемых томов
    docker volume prune -f
    
    # Удаление неиспользуемых сетей
    docker network prune -f
    
    # Полная очистка (включая build cache)
    docker system prune -f
    
    log_success "Очистка завершена"
}

# Проверка здоровья сервисов
check_services_health() {
    local compose_file=${1:-"docker-compose.yml"}
    
    log_info "Проверка здоровья сервисов..."
    
    if docker compose -f "$compose_file" ps | grep -q "unhealthy"; then
        log_error "Обнаружены нездоровые сервисы"
        docker compose -f "$compose_file" ps
        return 1
    fi
    
    log_success "Все сервисы здоровы"
}

# Бэкап томов
backup_volumes() {
    local backup_dir=${1:-"./backups"}
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    log_info "Создание бэкапа томов в $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    # Получение списка томов
    local volumes=$(docker volume ls --format "{{.Name}}" | grep -E "(postgres|redis|app-data)")
    
    for volume in $volumes; do
        log_info "Бэкап тома: $volume"
        docker run --rm -v "$volume":/data -v "$backup_dir":/backup alpine tar czf "/backup/${volume}_${timestamp}.tar.gz" -C /data .
    done
    
    log_success "Бэкап завершен: $backup_dir"
}

# Восстановление томов
restore_volumes() {
    local backup_dir=${1:-"./backups"}
    local volume_name=$2
    local backup_file=$3
    
    if [[ -z "$volume_name" || -z "$backup_file" ]]; then
        log_error "Использование: restore_volumes <backup_dir> <volume_name> <backup_file>"
        return 1
    fi
    
    log_info "Восстановление тома $volume_name из $backup_file..."
    
    if [[ ! -f "$backup_dir/$backup_file" ]]; then
        log_error "Файл бэкапа не найден: $backup_dir/$backup_file"
        return 1
    fi
    
    # Остановка сервисов, использующих том
    docker compose down
    
    # Удаление существующего тома
    docker volume rm "$volume_name" 2>/dev/null || true
    
    # Создание нового тома
    docker volume create "$volume_name"
    
    # Восстановление данных
    docker run --rm -v "$volume_name":/data -v "$backup_dir":/backup alpine tar xzf "/backup/$backup_file" -C /data
    
    log_success "Восстановление завершено"
}

# Мониторинг ресурсов
monitor_resources() {
    log_info "Мониторинг ресурсов Docker..."
    
    echo "=== Контейнеры ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    echo -e "\n=== Дисковое пространство ==="
    docker system df
    
    echo -e "\n=== Тома ==="
    docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Size}}"
}

# Обновление образов
update_images() {
    local compose_file=${1:-"docker-compose.yml"}
    
    log_info "Обновление образов..."
    
    # Получение списка образов из compose файла
    local images=$(docker compose -f "$compose_file" config --images)
    
    for image in $images; do
        log_info "Обновление образа: $image"
        docker pull "$image"
    done
    
    log_success "Обновление образов завершено"
}

# Проверка безопасности
security_scan() {
    log_info "Проверка безопасности образов..."
    
    # Проверка на наличие уязвимостей (требует Docker Scout)
    if command -v docker scout &> /dev/null; then
        local images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>")
        
        for image in $images; do
            log_info "Сканирование образа: $image"
            docker scout cves "$image" || true
        done
    else
        log_warning "Docker Scout не установлен. Установите для проверки уязвимостей."
    fi
    
    # Проверка контейнеров на root пользователя
    log_info "Проверка контейнеров на root пользователя..."
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | while read line; do
        if echo "$line" | grep -q "root"; then
            log_warning "Контейнер с root пользователем: $line"
        fi
    done
}

# Создание секретов
create_secrets() {
    local secrets_dir=${1:-"./secrets"}
    
    log_info "Создание секретов в $secrets_dir..."
    
    mkdir -p "$secrets_dir"
    
    # Генерация паролей
    if [[ ! -f "$secrets_dir/db_password.txt" ]]; then
        openssl rand -base64 32 > "$secrets_dir/db_password.txt"
        log_info "Создан пароль БД"
    fi
    
    if [[ ! -f "$secrets_dir/redis_password.txt" ]]; then
        openssl rand -base64 32 > "$secrets_dir/redis_password.txt"
        log_info "Создан пароль Redis"
    fi
    
    if [[ ! -f "$secrets_dir/api_key.txt" ]]; then
        openssl rand -base64 64 > "$secrets_dir/api_key.txt"
        log_info "Создан API ключ"
    fi
    
    if [[ ! -f "$secrets_dir/grafana_password.txt" ]]; then
        openssl rand -base64 32 > "$secrets_dir/grafana_password.txt"
        log_info "Создан пароль Grafana"
    fi
    
    # Установка правильных прав доступа
    chmod 600 "$secrets_dir"/*
    
    log_success "Секреты созданы"
}

# Проверка конфигурации
validate_config() {
    local compose_file=${1:-"docker-compose.yml"}
    
    log_info "Проверка конфигурации Docker Compose..."
    
    if docker compose -f "$compose_file" config > /dev/null; then
        log_success "Конфигурация валидна"
    else
        log_error "Ошибка в конфигурации"
        return 1
    fi
}

# Логи контейнеров
show_logs() {
    local service_name=${1:-""}
    local lines=${2:-"100"}
    
    if [[ -n "$service_name" ]]; then
        log_info "Логи сервиса: $service_name"
        docker compose logs --tail="$lines" -f "$service_name"
    else
        log_info "Логи всех сервисов"
        docker compose logs --tail="$lines" -f
    fi
}

# Перезапуск сервиса
restart_service() {
    local service_name=$1
    
    if [[ -z "$service_name" ]]; then
        log_error "Укажите имя сервиса"
        return 1
    fi
    
    log_info "Перезапуск сервиса: $service_name"
    docker compose restart "$service_name"
    log_success "Сервис перезапущен"
}

# Основное меню
show_help() {
    echo "Docker и Docker Compose утилиты"
    echo ""
    echo "Использование: $0 <команда> [опции]"
    echo ""
    echo "Команды:"
    echo "  check           - Проверка установки Docker и Docker Compose"
    echo "  cleanup         - Очистка неиспользуемых ресурсов"
    echo "  health          - Проверка здоровья сервисов"
    echo "  backup          - Создание бэкапа томов"
    echo "  restore         - Восстановление томов"
    echo "  monitor         - Мониторинг ресурсов"
    echo "  update          - Обновление образов"
    echo "  security        - Проверка безопасности"
    echo "  secrets         - Создание секретов"
    echo "  validate        - Проверка конфигурации"
    echo "  logs [service]  - Показать логи"
    echo "  restart <svc>   - Перезапустить сервис"
    echo "  help            - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 check"
    echo "  $0 cleanup"
    echo "  $0 health docker-compose.prod.yml"
    echo "  $0 backup ./backups"
    echo "  $0 logs app"
    echo "  $0 restart db"
}

# Основная логика
main() {
    local command=${1:-"help"}
    
    case "$command" in
        "check")
            check_docker
            check_docker_compose
            ;;
        "cleanup")
            check_docker
            cleanup_docker
            ;;
        "health")
            check_docker_compose
            check_services_health "${2:-docker-compose.yml}"
            ;;
        "backup")
            check_docker
            backup_volumes "${2:-./backups}"
            ;;
        "restore")
            check_docker
            restore_volumes "${2:-./backups}" "${3:-}" "${4:-}"
            ;;
        "monitor")
            check_docker
            monitor_resources
            ;;
        "update")
            check_docker_compose
            update_images "${2:-docker-compose.yml}"
            ;;
        "security")
            check_docker
            security_scan
            ;;
        "secrets")
            create_secrets "${2:-./secrets}"
            ;;
        "validate")
            check_docker_compose
            validate_config "${2:-docker-compose.yml}"
            ;;
        "logs")
            check_docker_compose
            show_logs "${2:-}" "${3:-100}"
            ;;
        "restart")
            check_docker_compose
            restart_service "${2:-}"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Запуск скрипта
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 