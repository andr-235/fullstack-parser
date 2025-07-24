#!/bin/bash

# =============================================================================
# Docker Optimization Script
# =============================================================================

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Функция для проверки зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен"
        exit 1
    fi
    
    log "Все зависимости установлены"
}

# Функция для анализа образов
analyze_images() {
    log "Анализ Docker образов..."
    
    echo -e "\n${BLUE}Размеры образов:${NC}"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | head -10
    
    echo -e "\n${BLUE}Самые большие образы:${NC}"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -hr | head -5
    
    echo -e "\n${BLUE}Неиспользуемые образы (dangling):${NC}"
    docker images -f "dangling=true" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
}

# Функция для оптимизации образов
optimize_images() {
    log "Оптимизация Docker образов..."
    
    # Удаление dangling образов
    local dangling_count=$(docker images -f "dangling=true" -q | wc -l)
    if [ "$dangling_count" -gt 0 ]; then
        log "Удаление $dangling_count dangling образов..."
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
    fi
    
    # Удаление неиспользуемых образов
    log "Удаление неиспользуемых образов..."
    docker image prune -f
    
    # Удаление неиспользуемых томов
    log "Удаление неиспользуемых томов..."
    docker volume prune -f
    
    # Удаление неиспользуемых сетей
    log "Удаление неиспользуемых сетей..."
    docker network prune -f
    
    log "Оптимизация завершена"
}

# Функция для сканирования уязвимостей
scan_vulnerabilities() {
    log "Сканирование образов на уязвимости..."
    
    if command -v docker scout &> /dev/null; then
        for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do
            echo -e "\n${BLUE}Сканирование $image:${NC}"
            docker scout cves "$image" || warn "Не удалось просканировать $image"
        done
    else
        warn "Docker Scout недоступен. Установите Docker Scout для сканирования уязвимостей"
    fi
}

# Функция для мониторинга ресурсов
monitor_resources() {
    log "Мониторинг использования ресурсов..."
    
    echo -e "\n${BLUE}Использование CPU и памяти:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    
    echo -e "\n${BLUE}Использование диска:${NC}"
    docker system df
    
    echo -e "\n${BLUE}Информация о Docker daemon:${NC}"
    docker info --format "table {{.Name}}\t{{.Value}}" | grep -E "(Storage Driver|Logging Driver|Cgroup Driver|Kernel Version|Operating System|Architecture|Total Memory|CPUs)"
}

# Функция для оптимизации Docker daemon
optimize_daemon() {
    log "Оптимизация Docker daemon..."
    
    # Проверка конфигурации daemon
    if [ -f "/etc/docker/daemon.json" ]; then
        info "Конфигурация daemon найдена в /etc/docker/daemon.json"
        cat /etc/docker/daemon.json | jq . 2>/dev/null || cat /etc/docker/daemon.json
    else
        warn "Файл конфигурации daemon не найден"
        info "Рекомендуемая конфигурация для оптимизации:"
        cat << EOF
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Hard": 64000,
      "Name": "nofile",
      "Soft": 64000
    }
  },
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "experimental": false,
  "metrics-addr": "127.0.0.1:9323",
  "live-restore": true
}
EOF
    fi
}

# Функция для проверки здоровья контейнеров
check_health() {
    log "Проверка здоровья контейнеров..."
    
    local compose_files=("docker-compose.yml" "docker-compose.dev.yml" "docker-compose.prod.yml")
    
    for compose_file in "${compose_files[@]}"; do
        if [ -f "$compose_file" ]; then
            echo -e "\n${BLUE}Проверка $compose_file:${NC}"
            if docker-compose -f "$compose_file" ps -q | grep -q .; then
                for container in $(docker-compose -f "$compose_file" ps -q); do
                    local name=$(docker inspect --format='{{.Name}}' "$container")
                    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health-check")
                    echo "  $name: $health"
                done
            else
                info "Нет запущенных контейнеров в $compose_file"
            fi
        fi
    done
}

# Функция для создания отчета
generate_report() {
    log "Генерация отчета оптимизации..."
    
    local report_file="docker-optimization-report-$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=== ОТЧЕТ ОПТИМИЗАЦИИ DOCKER ==="
        echo "Дата: $(date)"
        echo "Система: $(uname -a)"
        echo ""
        
        echo "=== РАЗМЕРЫ ОБРАЗОВ ==="
        docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
        echo ""
        
        echo "=== ИСПОЛЬЗОВАНИЕ РЕСУРСОВ ==="
        docker system df
        echo ""
        
        echo "=== ЗДОРОВЬЕ КОНТЕЙНЕРОВ ==="
        for compose_file in docker-compose.yml docker-compose.dev.yml docker-compose.prod.yml; do
            if [ -f "$compose_file" ]; then
                echo "Файл: $compose_file"
                docker-compose -f "$compose_file" ps 2>/dev/null || echo "  Нет запущенных контейнеров"
                echo ""
            fi
        done
        
        echo "=== РЕКОМЕНДАЦИИ ==="
        echo "1. Регулярно удаляйте неиспользуемые образы: docker system prune -f"
        echo "2. Используйте multi-stage builds в Dockerfile"
        echo "3. Объединяйте RUN команды для уменьшения слоев"
        echo "4. Используйте .dockerignore для исключения ненужных файлов"
        echo "5. Сканируйте образы на уязвимости: docker scout cves"
        echo "6. Мониторьте использование ресурсов: docker stats"
        echo "7. Настройте логирование с ротацией"
        echo "8. Используйте именованные тома вместо bind mounts где возможно"
        
    } > "$report_file"
    
    log "Отчет сохранен в $report_file"
}

# Функция для показа справки
show_help() {
    echo -e "${GREEN}Docker Optimization Script${NC}"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  analyze      - Анализ Docker образов"
    echo "  optimize     - Оптимизация образов и ресурсов"
    echo "  scan         - Сканирование на уязвимости"
    echo "  monitor      - Мониторинг ресурсов"
    echo "  daemon       - Оптимизация Docker daemon"
    echo "  health       - Проверка здоровья контейнеров"
    echo "  report       - Генерация отчета"
    echo "  all          - Выполнить все операции"
    echo "  help         - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 analyze"
    echo "  $0 optimize"
    echo "  $0 all"
}

# Основная функция
main() {
    local command=${1:-help}
    
    case $command in
        analyze)
            check_dependencies
            analyze_images
            ;;
        optimize)
            check_dependencies
            optimize_images
            ;;
        scan)
            check_dependencies
            scan_vulnerabilities
            ;;
        monitor)
            check_dependencies
            monitor_resources
            ;;
        daemon)
            check_dependencies
            optimize_daemon
            ;;
        health)
            check_dependencies
            check_health
            ;;
        report)
            check_dependencies
            generate_report
            ;;
        all)
            check_dependencies
            analyze_images
            optimize_images
            scan_vulnerabilities
            monitor_resources
            optimize_daemon
            check_health
            generate_report
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Запуск скрипта
main "$@" 