#!/bin/bash

set -e

echo "[GIT CLEANUP] Обновляю информацию о ветках..."
git fetch --all --prune

echo "[GIT CLEANUP] Удаляю локальные ветки, смерженные в main (кроме main и develop)..."
for branch in $(git branch --merged main | grep -vE '^(\*| main$| develop$)'); do
  echo "  - Удаляю локальную ветку: $branch"
  git branch -d "$branch"
done

echo "[GIT CLEANUP] Удаляю удалённые ветки, смерженные в main (кроме main и develop)..."
for remote_branch in $(git branch -r --merged origin/main | grep -vE 'origin/(main$|develop$)' | sed 's/origin\///'); do
  echo "  - Удаляю удалённую ветку: $remote_branch"
  git push origin --delete "$remote_branch"
done

echo "[GIT CLEANUP] Очистка завершена!" 