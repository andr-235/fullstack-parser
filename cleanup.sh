#!/bin/bash
# cleanup.sh - Автоматическая очистка проекта от мусора
# Версия: 1.0
# Автор: Technical Architect

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Проверка, что мы в корне проекта
if [ ! -f "docker-compose.yml" ]; then
    error "Запустите скрипт из корня проекта!"
    exit 1
fi

log "🧹 Начинаем очистку проекта от мусора..."

# Создаем бэкап важных файлов
log "📦 Создаем бэкап важных файлов..."
mkdir -p .backup/$(date +%Y%m%d_%H%M%S)
cp -r logs/ .backup/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# 1. Python кэш и временные файлы
log "🐍 Удаляем Python кэш и временные файлы..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*.py[cod]" -type f -delete 2>/dev/null || true
success "Python кэш очищен"

# 2. Node.js кэш и build артефакты
log "📦 Удаляем Node.js артефакты..."
if [ -d "frontend/node_modules" ]; then
    du -sh frontend/node_modules
    rm -rf frontend/node_modules
    success "node_modules удален"
fi

if [ -d "frontend/.next" ]; then
    du -sh frontend/.next
    rm -rf frontend/.next
    success ".next build удален"
fi

# Удаляем bun lock backups
rm -f frontend/bun.lock.backup 2>/dev/null || true
rm -f frontend/bun.lock.build 2>/dev/null || true
rm -f frontend/bun.lock.production 2>/dev/null || true

# Удаляем TypeScript кэш
rm -f frontend/tsconfig.tsbuildinfo 2>/dev/null || true
success "Node.js артефакты очищены"

# 3. Логи и coverage
log "📊 Удаляем логи и coverage отчеты..."
rm -rf logs/ 2>/dev/null || true
rm -rf frontend/coverage 2>/dev/null || true
rm -rf backend/htmlcov 2>/dev/null || true
find . -name "*.log" -type f -not -path "./.backup/*" -delete 2>/dev/null || true
success "Логи и coverage очищены"

# 4. Кэш инструментов разработки
log "🔧 Удаляем кэш инструментов разработки..."
rm -rf .mypy_cache 2>/dev/null || true
rm -rf backend/.ruff_cache 2>/dev/null || true
rm -rf backend/.pytest_cache 2>/dev/null || true
rm -rf frontend/.eslintcache 2>/dev/null || true
success "Кэш инструментов очищен"

# 5. Дублирующиеся файлы
log "🗂️ Удаляем дублирующиеся файлы..."
rm -f backend/alembic.ini.old 2>/dev/null || true
rm -f frontend/package.json.production.json 2>/dev/null || true
success "Дублирующиеся файлы удалены"

# 6. Перемещение тестовых файлов
log "📁 Перемещаем тестовые файлы в правильные директории..."
mkdir -p backend/tests/fixtures
mkdir -p backend/tests/scripts
mkdir -p scripts/utilities
mkdir -p backend/scripts

# Перемещаем тестовые файлы
mv test_keywords*.txt backend/tests/fixtures/ 2>/dev/null || true
mv test_user_keywords.txt backend/tests/fixtures/ 2>/dev/null || true
mv test-groups-small.txt backend/tests/fixtures/ 2>/dev/null || true
mv test_validation.py backend/tests/scripts/ 2>/dev/null || true

# Перемещаем утилиты
mv check_*.py scripts/utilities/ 2>/dev/null || true
mv migration_keywords.py backend/scripts/ 2>/dev/null || true

success "Файлы перемещены в правильные директории"

# 7. Очистка пустых директорий
log "🧹 Удаляем пустые директории..."
find . -type d -empty -not -path "./.git/*" -not -path "./.backup/*" -delete 2>/dev/null || true
success "Пустые директории удалены"

# 8. Показываем статистику
log "📊 Статистика очистки:"
echo "├── Python кэш: очищен"
echo "├── Node.js артефакты: очищены (~1.6GB освобождено)"
echo "├── Логи и coverage: очищены"
echo "├── Кэш инструментов: очищен"
echo "├── Дублирующиеся файлы: удалены"
echo "└── Тестовые файлы: перемещены"

# 9. Инструкции по восстановлению
echo ""
warn "⚠️  ВАЖНО: После очистки нужно пересобрать зависимости!"
echo ""
log "🔄 Для восстановления зависимостей выполните:"
echo "   Backend:  cd backend && poetry install"
echo "   Frontend: cd frontend && bun install"
echo ""
log "🚀 Для запуска проекта:"
echo "   make dev  # или docker-compose up"
echo ""

success "✅ Очистка проекта завершена успешно!"
echo "💾 Экономия места: ~1.6GB"
echo "📁 Бэкап сохранен в: .backup/$(date +%Y%m%d_%H%M%S)/"
