#!/bin/bash

# 🚀 Скрипт для создания релизов
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

# Проверка зависимостей
check_dependencies() {
    log_step "Проверка зависимостей..."

    if ! command -v git &> /dev/null; then
        log_error "Git не установлен"
        exit 1
    fi

    if ! command -v gh &> /dev/null; then
        log_warning "Git CLI не установлен. Установите Git CLI"
        log_info "Можно создать релиз вручную через Git UI"
    fi

    log_success "Зависимости проверены"
}

# Получение текущей версии
get_current_version() {
    # Пытаемся получить версию из backend
    if [ -f "backend/pyproject.toml" ]; then
        grep -E "^version = " backend/pyproject.toml | sed 's/version = "\(.*\)"/\1/'
    elif [ -f "frontend/package.json" ]; then
        grep -E '"version":' frontend/package.json | sed 's/.*"version": "\(.*\)".*/\1/'
    else
        echo "0.1.0"
    fi
}

# Определение типа релиза
get_release_type() {
    echo -e "${CYAN}Выберите тип релиза:${NC}"
    echo "1) 🚀 Major (x.0.0) - Критические изменения, несовместимые с предыдущими версиями"
    echo "2) ✨ Minor (0.x.0) - Новые функции, обратная совместимость"
    echo "3) 🐛 Patch (0.0.x) - Исправления багов, мелкие улучшения"
    echo "4) 🧪 Pre-release (beta/rc) - Тестовые версии"
    echo "5) ❌ Отмена"

    read -p "Введите номер (1-5): " choice

    case $choice in
        1) echo "major" ;;
        2) echo "minor" ;;
        3) echo "patch" ;;
        4) echo "prerelease" ;;
        5) log_info "Отменено пользователем"; exit 0 ;;
        *) log_error "Неверный выбор"; exit 1 ;;
    esac
}

# Получение описания релиза
get_release_description() {
    echo -e "${CYAN}Введите описание релиза (или нажмите Enter для автоматического):${NC}"
    read -r description

    if [ -z "$description" ]; then
        # Автоматическое описание на основе коммитов
        log_info "Генерируем автоматическое описание..."
        description=$(git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD | head -10 | sed 's/^/- /')
    fi

    echo "$description"
}

# Создание новой версии
create_new_version() {
    local current_version=$1
    local release_type=$2

    log_step "Создание новой версии..."

    # Парсинг текущей версии
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    major=${VERSION_PARTS[0]}
    minor=${VERSION_PARTS[1]}
    patch=${VERSION_PARTS[2]}

    case $release_type in
        "major")
            new_version="$((major + 1)).0.0"
            ;;
        "minor")
            new_version="${major}.$((minor + 1)).0"
            ;;
        "patch")
            new_version="${major}.${minor}.$((patch + 1))"
            ;;
        "prerelease")
            echo -e "${CYAN}Выберите тип pre-release:${NC}"
            echo "1) beta"
            echo "2) rc (release candidate)"
            read -p "Введите номер (1-2): " prerelease_choice

            case $prerelease_choice in
                1) prerelease_type="beta" ;;
                2) prerelease_type="rc" ;;
                *) log_error "Неверный выбор"; exit 1 ;;
            esa

            # Увеличиваем patch для pre-release
            new_version="${major}.${minor}.$((patch + 1))-${prerelease_type}.1"
            ;;
    esa

    echo "$new_version"
}

# Обновление версий в файлах
update_versions() {
    local new_version=$1

    log_step "Обновление версий в файлах..."

    # Обновление backend версии
    if [ -f "backend/pyproject.toml" ]; then
        sed -i "s/^version = \".*\"/version = \"${new_version}\"/" backend/pyproject.toml
        log_success "Обновлена версия в backend/pyproject.toml"
    fi

    # Обновление frontend версии
    if [ -f "frontend/package.json" ]; then
        sed -i "s/\"version\": \".*\"/\"version\": \"${new_version}\"/" frontend/package.json
        log_success "Обновлена версия в frontend/package.json"
    fi
}

# Проверка состояния репозитория
check_repository_status() {
    log_step "Проверка состояния репозитория..."

    # Проверка на несохраненные изменения
    if ! git diff-index --quiet HEAD --; then
        log_warning "Обнаружены несохраненные изменения"
        git status --short
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Отменено пользователем"
            exit 0
        fi
    fi

    # Проверка на uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "Обнаружены uncommitted изменения"
        git status --short
        read -p "Создать коммит? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "chore: подготовка к релизу $new_version"
        fi
    fi

    log_success "Репозиторий готов к релизу"
}

# Создание тега и push
create_tag_and_push() {
    local new_version=$1
    local description=$2

    log_step "Создание тега и push..."

    # Создание тега
    git tag -a "v${new_version}" -m "Release v${new_version}

${description}"

    # Push тега
    git push origin "v${new_version}"

    log_success "Тег v${new_version} создан и отправлен"
}

# Создание Git Release
create_git_release() {
    local new_version=$1
    local description=$2

    if command -v gh &> /dev/null; then
        log_step "Создание Git Release..."

        # Определение типа релиза
        if [[ $new_version == *"-"* ]]; then
            prerelease_flag="--prerelease"
        else
            prerelease_flag=""
        fi

        # Создание релиза через Git CLI
        gh release create "v${new_version}" \
            --title "Release v${new_version}" \
            --notes "${description}" \
            ${prerelease_flag}

        log_success "Git Release создан"
    else
        log_warning "Git CLI не установлен. Создайте релиз вручную"
    fi
}

# Основная функция
main() {
    echo -e "${PURPLE}🚀 Создание релиза${NC}"
    echo "=================="

    # Проверка зависимостей
    check_dependencies

    # Получение текущей версии
    current_version=$(get_current_version)
    log_info "Текущая версия: $current_version"

    # Определение типа релиза
    release_type=$(get_release_type)
    log_info "Тип релиза: $release_type"

    # Создание новой версии
    new_version=$(create_new_version "$current_version" "$release_type")
    log_info "Новая версия: $new_version"

    # Получение описания
    description=$(get_release_description)

    # Проверка состояния репозитория
    check_repository_status

    # Обновление версий
    update_versions "$new_version"

    # Создание коммита с обновленными версиями
    git add .
    git commit -m "chore: bump version to $new_version"

    # Создание тега и push
    create_tag_and_push "$new_version" "$description"

    # Создание Git Release
    create_git_release "$new_version" "$description"

    echo
    log_success "🎉 Релиз v${new_version} успешно создан!"
    log_info "CI/CD pipeline запустит автоматический процесс деплоя"
    log_info "Отслеживайте прогресс в CI/CD pipeline"
}

# Запуск скрипта
main "$@"
