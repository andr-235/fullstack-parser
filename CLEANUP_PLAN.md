# План очистки проекта от мусора

## 🗑️ КРИТИЧЕСКИЙ МУСОР (удалить немедленно)

### 1. Python кэш и временные файлы
```bash
# Удалить все __pycache__ директории
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Удалить .pyc файлы
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
```

### 2. Node.js кэш и build артефакты
```bash
# Удалить node_modules (1.1GB!)
rm -rf frontend/node_modules

# Удалить .next build (547MB!)
rm -rf frontend/.next

# Удалить bun lock backups
rm -f frontend/bun.lock.backup
rm -f frontend/bun.lock.build  
rm -f frontend/bun.lock.production

# Удалить TypeScript кэш
rm -f frontend/tsconfig.tsbuildinfo
```

### 3. Логи и coverage
```bash
# Удалить логи
rm -rf logs/
rm -f frontend/node_modules/*/yarn-error.log
rm -f frontend/node_modules/*/lint.log

# Удалить coverage
rm -rf frontend/coverage
```

### 4. Кэш инструментов разработки
```bash
# Удалить кэш линтеров и типизации
rm -rf .mypy_cache
rm -rf backend/.ruff_cache
rm -rf backend/.pytest_cache
```

## 📁 ДУБЛИРУЮЩИЕСЯ ФАЙЛЫ (решить что оставить)

### 1. Alembic конфигурация
- `backend/alembic.ini` (текущая)
- `backend/alembic.ini.old` (старая) → **УДАЛИТЬ**

### 2. Package.json файлы
- `frontend/package.json` (основной)
- `frontend/package.json.production.json` (дубликат) → **УДАЛИТЬ**

### 3. Test файлы в корне
- `test_validation.py` → **ПЕРЕМЕСТИТЬ** в `backend/tests/`
- `test_keywords*.txt` → **ПЕРЕМЕСТИТЬ** в `backend/tests/fixtures/`
- `test_user_keywords.txt` → **ПЕРЕМЕСТИТЬ** в `backend/tests/fixtures/`
- `test-groups-small.txt` → **ПЕРЕМЕСТИТЬ** в `backend/tests/fixtures/`

### 4. Утилиты в корне
- `check_comments.py` → **ПЕРЕМЕСТИТЬ** в `scripts/`
- `check_data.py` → **ПЕРЕМЕСТИТЬ** в `scripts/`
- `migration_keywords.py` → **ПЕРЕМЕСТИТЬ** в `backend/scripts/`

## 🔧 СТРУКТУРНЫЕ УЛУЧШЕНИЯ

### 1. Объединить .gitignore файлы
- Удалить дублирующиеся записи между корневым и backend/.gitignore
- Оставить только корневой .gitignore с полным покрытием

### 2. Очистить scripts/ директорию
- Много скриптов для разных целей
- Сгруппировать по категориям: `deploy/`, `maintenance/`, `dev/`

### 3. Улучшить структуру тестов
```
backend/tests/
├── unit/
├── integration/
├── fixtures/          # ← переместить сюда test_*.txt файлы
└── scripts/           # ← переместить сюда test_*.py файлы
```

## 📊 РАЗМЕРЫ ПРОБЛЕМ

| Компонент | Размер | Действие |
|-----------|--------|----------|
| `frontend/node_modules/` | 1.1GB | Удалить, пересобрать |
| `frontend/.next/` | 547MB | Удалить, пересобрать |
| `backend/venv/` | 32KB | Оставить (маленький) |
| `logs/` | ~10KB | Удалить |
| `coverage/` | ~5MB | Удалить |

**Общая экономия: ~1.6GB**

## 🚀 СКРИПТ АВТООЧИСТКИ

```bash
#!/bin/bash
# cleanup.sh - Автоматическая очистка проекта

echo "🧹 Начинаем очистку проекта..."

# 1. Python кэш
echo "Удаляем Python кэш..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true

# 2. Node.js артефакты
echo "Удаляем Node.js артефакты..."
rm -rf frontend/node_modules
rm -rf frontend/.next
rm -f frontend/bun.lock.backup
rm -f frontend/bun.lock.build
rm -f frontend/bun.lock.production
rm -f frontend/tsconfig.tsbuildinfo

# 3. Логи и coverage
echo "Удаляем логи и coverage..."
rm -rf logs/
rm -rf frontend/coverage
find . -name "*.log" -type f -delete 2>/dev/null || true

# 4. Кэш инструментов
echo "Удаляем кэш инструментов..."
rm -rf .mypy_cache
rm -rf backend/.ruff_cache
rm -rf backend/.pytest_cache

# 5. Дублирующиеся файлы
echo "Удаляем дублирующиеся файлы..."
rm -f backend/alembic.ini.old
rm -f frontend/package.json.production.json

# 6. Перемещение файлов
echo "Перемещаем тестовые файлы..."
mkdir -p backend/tests/fixtures
mkdir -p backend/tests/scripts
mkdir -p scripts/utilities

mv test_keywords*.txt backend/tests/fixtures/ 2>/dev/null || true
mv test_user_keywords.txt backend/tests/fixtures/ 2>/dev/null || true
mv test-groups-small.txt backend/tests/fixtures/ 2>/dev/null || true
mv test_validation.py backend/tests/scripts/ 2>/dev/null || true
mv check_*.py scripts/utilities/ 2>/dev/null || true
mv migration_keywords.py backend/scripts/ 2>/dev/null || true

echo "✅ Очистка завершена!"
echo "💾 Экономия места: ~1.6GB"
echo "🔄 Для восстановления зависимостей:"
echo "   Backend: cd backend && poetry install"
echo "   Frontend: cd frontend && bun install"
```

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Перед очисткой** убедитесь, что все изменения закоммичены
2. **После очистки** нужно будет пересобрать зависимости
3. **Тестовые файлы** будут перемещены, обновите импорты
4. **Скрипты** будут перемещены, обновите пути в Makefile

## 🎯 РЕЗУЛЬТАТ

После очистки проект будет:
- ✅ На 1.6GB меньше
- ✅ Без дублирующихся файлов  
- ✅ С правильной структурой тестов
- ✅ С чистой историей Git
- ✅ Готов к продакшену
