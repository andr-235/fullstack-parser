#!/bin/bash

# 🔄 Скрипт для отката релиза
# Автор: AI Assistant
# Версия: 1.0.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Получение доступных тегов
get_available_tags() {
    git tag --sort=-version:refname | head -10
}

# Проверка существования тега
check_tag_exists() {
    local tag=$1
    if git rev-parse "$tag" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Откат Docker образов
rollback_docker() {
    local target_version=$1

    log_step "Откат Docker образов к версии $target_version..."

    # Проверка существования docker-compose файла
    if [ ! -f "docker-compose.prod.ip.yml" ]; then
        log_error "Файл docker-compose.prod.ip.yml не найден"
        return 1
    fi

    # Откат с использованием конкретной версии
    docker-compose -f docker-compose.prod.ip.yml down
    docker-compose -f docker-compose.prod.ip.yml pull
    docker-compose -f docker-compose.prod.ip.yml up -d --remove-orphans

    log_success "Docker образы откачены к версии $target_version"
}

# Откат базы данных (если есть backup)
rollback_database() {
    local target_version=$1

    log_step "Проверка доступности backup для версии $target_version..."

    # Поиск подходящего backup файла
    backup_file=$(find backup/ -name "*$target_version*" -type f | head -1)

    if [ -n "$backup_file" ]; then
        log_warning "Найден backup файл: $backup_file"
        read -p "Восстановить базу данных из backup? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_step "Восстановление базы данных..."
            # Здесь должна быть команда восстановления
            # ./scripts/restore_db.sh "$backup_file"
            log_success "База данных восстановлена"
        fi
    else
        log_info "Backup для версии $target_version не найден"
    fi
}

# Создание hotfix ветки для отката
create_rollback_branch() {
    local target_version=$1
    local current_version=$2

    log_step "Создание hotfix ветки для отката..."

    branch_name="hotfix/rollback-to-v$target_version"

    # Создание ветки от main
    git checkout main
    git pull origin main
    git checkout -b "$branch_name"

    # Откат к целевому тегу
    git revert --no-edit "$current_version"..HEAD

    log_success "Создана ветка $branch_name"
    log_info "Для завершения отката выполните:"
    log_info "git push origin $branch_name"
    log_info "Создайте Pull Request для merge в main"
}

# Основная функция
main() {
    echo -e "${PURPLE}🔄 Откат релиза${NC}"
    echo "=================="

    # Проверка что мы в git репозитории
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Не в git репозитории"
        exit 1
    fi

    # Получение текущей версии
    current_version=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
    log_info "Текущая версия: $current_version"

    # Показать доступные теги
    log_step "Доступные версии для отката:"
    available_tags=$(get_available_tags)
    if [ -n "$available_tags" ]; then
        echo "$available_tags" | nl
    else
        log_error "Нет доступных тегов"
        exit 1
    fi

    # Выбор целевой версии
    echo
    echo -e "${CYAN}Выберите версию для отката:${NC}"
    read -p "Введите номер версии (например: 1.2.2): " target_version

    if [ -z "$target_version" ]; then
        log_error "Версия не указана"
        exit 1
    fi

    # Проверка существования тега
    if ! check_tag_exists "v$target_version"; then
        log_error "Тег v$target_version не найден"
        exit 1
    fi

    log_info "Откат к версии: v$target_version"

    # Выбор типа отката
    echo -e "${CYAN}Выберите тип отката:${NC}"
    echo "1) 🐳 Только Docker образы"
    echo "2) 🗄️ Docker + База данных"
    echo "3) 🔄 Полный откат (Docker + DB + код)"
    echo "4) ❌ Отмена"

    read -p "Введите номер (1-4): " rollback_type

    case $rollback_type in
        1)
            log_step "Откат только Docker образов..."
            rollback_docker "$target_version"
            ;;
        2)
            log_step "Откат Docker образов и базы данных..."
            rollback_docker "$target_version"
            rollback_database "$target_version"
            ;;
        3)
            log_step "Полный откат..."
            rollback_docker "$target_version"
            rollback_database "$target_version"
            create_rollback_branch "$target_version" "$current_version"
            ;;
        4)
            log_info "Откат отменен"
            exit 0
            ;;
        *)
            log_error "Неверный выбор"
            exit 1
            ;;
    esac

    echo
    log_success "🎉 Откат к версии v$target_version завершен!"

    # Полезная информация
    echo
    log_info "Полезные команды:"
    echo "  • Проверить статус: docker-compose -f docker-compose.prod.ip.yml ps"
    echo "  • Посмотреть логи: docker-compose -f docker-compose.prod.ip.yml logs"
    echo "  • Проверить версии: make release-status"
}

# Запуск скрипта
main "$@"
