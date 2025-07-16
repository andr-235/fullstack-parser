#!/bin/bash

echo "🗑️ Удаляем оставшиеся ветки после мержа..."

# Удаляем ветки feature
echo "Удаляем feature ветки..."
git push origin --delete feature/keywords-infinite-scroll-main 2>/dev/null || echo "Ветка feature/keywords-infinite-scroll-main уже удалена"
git push origin --delete feature/ci-cd-refactor 2>/dev/null || echo "Ветка feature/ci-cd-refactor уже удалена"

# Удаляем любые другие оставшиеся ветки
echo "Проверяем другие ветки..."
git branch -r | grep -v HEAD | grep -v main | sed 's/origin\///' | while read branch; do
    echo "Удаляем ветку: $branch"
    git push origin --delete "$branch" 2>/dev/null || echo "Не удалось удалить $branch"
done

# Очищаем локальные ссылки
echo "🧹 Очищаем локальные ссылки..."
git remote prune origin

echo "✅ Готово! Все ветки удалены."
echo "📋 Текущие ветки:"
git branch -a
