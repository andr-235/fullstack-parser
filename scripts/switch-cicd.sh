#!/bin/bash

# 🔄 Переключение между старым и новым CI/CD
set -e

echo "🔄 Переключение CI/CD системы..."

# Проверка текущего состояния
if [[ -f ".github/workflows/ci.yml" && -f ".github/workflows/simple-ci.yml" ]]; then
    echo "📋 Текущее состояние:"
    echo "  - ci.yml: $(ls -la .github/workflows/ci.yml | awk '{print $5}' | sed 's/^/    /')"
    echo "  - simple-ci.yml: $(ls -la .github/workflows/simple-ci.yml | awk '{print $5}' | sed 's/^/    /')"
    echo ""

    read -p "Переключиться на упрощённый CI/CD? (y/N): " switch
    if [[ $switch =~ ^[Yy]$ ]]; then
        echo "🔄 Переключение на упрощённый CI/CD..."

        # Резервная копия старого
        mv .github/workflows/ci.yml .github/workflows/ci.yml.backup
        echo "✅ Старый CI сохранён как ci.yml.backup"

        # Активация нового
        mv .github/workflows/simple-ci.yml .github/workflows/ci.yml
        echo "✅ Упрощённый CI активирован"

        echo ""
        echo "🎯 Теперь используется упрощённый CI/CD!"
        echo "📖 Документация: docs/SINGLE_DEV_CICD.md"
        echo "🚀 Команды: make help"

    else
        echo "❌ Переключение отменено"
    fi

elif [[ -f ".github/workflows/ci.yml.backup" ]]; then
    echo "📋 Текущее состояние: упрощённый CI/CD активен"
    echo ""

    read -p "Вернуться к старому CI/CD? (y/N): " switch
    if [[ $switch =~ ^[Yy]$ ]]; then
        echo "🔄 Возврат к старому CI/CD..."

        # Резервная копия нового
        mv .github/workflows/ci.yml .github/workflows/simple-ci.yml
        echo "✅ Упрощённый CI сохранён как simple-ci.yml"

        # Восстановление старого
        mv .github/workflows/ci.yml.backup .github/workflows/ci.yml
        echo "✅ Старый CI восстановлен"

        echo ""
        echo "🎯 Теперь используется старый CI/CD!"

    else
        echo "❌ Переключение отменено"
    fi

else
    echo "❌ Ошибка: Не найдены файлы CI/CD"
    echo "Проверь директорию .github/workflows/"
    exit 1
fi

echo ""
echo "📊 Статус файлов:"
ls -la .github/workflows/ci*.yml* 2>/dev/null || echo "Файлы не найдены"
