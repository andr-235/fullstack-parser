#!/bin/bash

# Скрипт для настройки GitLab для одного разработчика
# Использование: ./scripts/setup-gitlab.sh YOUR_GITLAB_USERNAME

set -e

GITLAB_USERNAME=$1

if [ -z "$GITLAB_USERNAME" ]; then
    echo "❌ Ошибка: Укажите имя пользователя GitLab"
    echo "Использование: ./scripts/setup-gitlab.sh YOUR_GITLAB_USERNAME"
    exit 1
fi

echo "🚀 Настройка GitLab для проекта fullstack-parser"
echo "Пользователь: $GITLAB_USERNAME"
echo ""

# Проверяем, что мы в git репозитории
if [ ! -d ".git" ]; then
    echo "❌ Ошибка: Не найден .git каталог. Запустите скрипт из корня проекта."
    exit 1
fi

# Проверяем текущие remotes
echo "📋 Текущие remotes:"
git remote -v
echo ""

# Создаем новую ветку для настройки
BRANCH_NAME="setup-gitlab-$(date +%Y%m%d-%H%M%S)"
echo "🔧 Создание ветки: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Добавляем GitLab remote
GITLAB_URL="https://gitlab.com/$GITLAB_USERNAME/fullstack-parser.git"
echo "🔗 Добавление GitLab remote: $GITLAB_URL"
git remote add gitlab "$GITLAB_URL"

# Проверяем SSH ключи
echo "🔑 Проверка SSH ключей..."
if [ ! -f ~/.ssh/id_ed25519.pub ]; then
    echo "⚠️  SSH ключ не найден. Создаем новый..."
    ssh-keygen -t ed25519 -C "$(git config user.email)" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH ключ создан: ~/.ssh/id_ed25519.pub"
    echo "📋 Добавьте этот ключ в GitLab:"
    echo "   cat ~/.ssh/id_ed25519.pub"
    echo ""
else
    echo "✅ SSH ключ найден: ~/.ssh/id_ed25519.pub"
fi

# Коммитим изменения
echo "💾 Коммит изменений..."
git add .
git commit -m "feat: add GitLab CI/CD configuration and templates

- Add .gitlab-ci.yml with test, build, deploy stages
- Add merge request templates
- Add issue templates for bugs and features
- Add setup documentation"

# Показываем инструкции
echo ""
echo "🎯 Следующие шаги:"
echo ""
echo "1. Создайте проект в GitLab:"
echo "   - Перейдите на https://gitlab.com"
echo "   - Нажмите 'New Project' → 'Create blank project'"
echo "   - Project name: fullstack-parser"
echo "   - Visibility Level: Private"
echo "   - НЕ ставьте галочки в 'Initialize repository'"
echo ""
echo "2. Добавьте SSH ключ в GitLab:"
echo "   - Settings → SSH Keys"
echo "   - Скопируйте содержимое: cat ~/.ssh/id_ed25519.pub"
echo ""
echo "3. Отправьте код в GitLab:"
echo "   git push gitlab $BRANCH_NAME"
echo ""
echo "4. Создайте Merge Request в GitLab UI"
echo ""
echo "5. После merge удалите локальную ветку:"
echo "   git checkout main"
echo "   git branch -D $BRANCH_NAME"
echo ""
echo "6. Настройте переменные окружения в GitLab:"
echo "   - Settings → CI/CD → Variables"
echo "   - Добавьте: SSH_PRIVATE_KEY, STAGING_HOST, PROD_HOST и др."
echo ""
echo "🔧 Дополнительные настройки:"
echo "   - Settings → Repository → Protected Branches (защитите main)"
echo "   - Settings → Notifications (настройте уведомления)"
echo "   - Settings → Account → Two-Factor Authentication"
echo ""

echo "✅ Настройка завершена! Следуйте инструкциям выше." 