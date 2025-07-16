#!/bin/bash

# 🚀 Быстрый деплой для одного разработчика
set -e

echo "🚀 Быстрый деплой в production..."

# Проверка что мы в main ветке
if [[ $(git branch --show-current) != "main" ]]; then
    echo "❌ Ошибка: Деплой только из main ветки!"
    echo "Переключись на main: git checkout main"
    exit 1
fi

# Проверка что нет незакоммиченных изменений
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Ошибка: Есть незакоммиченные изменения!"
    echo "Сделай коммит или stash: git add . && git commit -m 'fix: последние изменения'"
    exit 1
fi

# Быстрые тесты
echo "🧪 Запуск быстрых тестов..."
cd backend && poetry run pytest tests/ -v --tb=short --maxfail=3 && cd ..
cd frontend && pnpm test --passWithNoTests --watchAll=false && cd ..
echo "✅ Тесты пройдены!"

# Подтверждение деплоя
read -p "🚀 Деплоить в production? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ Деплой отменён"
    exit 0
fi

# Пуш в main (запустит CI/CD)
echo "📤 Отправка в репозиторий..."
git push origin main

echo "✅ Деплой запущен!"
echo "📊 Следи за прогрессом: https://github.com/andr-235/fullstack/actions"
echo "🌐 Production: https://192.168.88.12"

# Ожидание завершения деплоя (опционально)
read -p "Ждать завершения деплоя? (y/N): " wait
if [[ $wait =~ ^[Yy]$ ]]; then
    echo "⏳ Ожидание завершения деплоя..."
    # Можно добавить проверку статуса через GitHub API
    echo "✅ Деплой должен завершиться через 5-10 минут"
fi
