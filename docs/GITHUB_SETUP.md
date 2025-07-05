# 🚀 Настройка GitHub и CI/CD Pipeline

Полное руководство по настройке GitHub репозитория, CI/CD pipeline и автоматизации для fullstack приложения.

## 📋 Оглавление

1. [Первоначальная настройка](#первоначальная-настройка)
2. [GitHub Repository Setup](#github-repository-setup)
3. [GitHub Secrets](#github-secrets)
4. [GitHub Environments](#github-environments)
5. [Branch Protection Rules](#branch-protection-rules)
6. [Pre-commit Hooks](#pre-commit-hooks)
7. [CI/CD Workflows](#cicd-workflows)
8. [Мониторинг и уведомления](#мониторинг-и-уведомления)
9. [Troubleshooting](#troubleshooting)

## 🎯 Первоначальная настройка

### 1. Создание GitHub репозитория

```bash
# Создание репозитория через GitHub CLI
gh repo create fullstack-parser --public --description "Fullstack приложение с FastAPI + Next.js"

# Или создайте через веб-интерфейс GitHub
```

### 2. Клонирование и настройка локально

```bash
# Клонирование репозитория
git clone https://github.com/your-username/your-project-name.git
cd your-project-name

# Настройка Git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Настройка commit template
git config commit.template .gitmessage

# Установка pre-commit hooks
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. Первый коммит

```bash
# Добавление всех файлов архитектуры
git add .
git commit -m "feat: добавлена базовая архитектура fullstack приложения

- Настроен Docker Compose для development и production
- Созданы GitHub Actions workflows для CI/CD
- Добавлены скрипты деплоя и backup
- Настроена security конфигурация
- Добавлены templates для PR и issues"

git push origin main
```

## 🔧 GitHub Repository Setup

### 1. Обновление CODEOWNERS

Отредактируйте файл `CODEOWNERS` и замените placeholder'ы:

```bash
# Замените в CODEOWNERS файле:
# @your-github-username → ваш реальный GitHub username
# @backend-team-lead → GitHub username или команда
# @frontend-team-lead → GitHub username или команда
# @devops-expert → GitHub username или команда
# @security-expert → GitHub username или команда
```

### 2. Настройка labels

Создайте labels для классификации issues и PR:

```bash
# Через GitHub CLI
gh label create "bug" --color "d73a4a" --description "Что-то работает не так"
gh label create "enhancement" --color "a2eeef" --description "Новая функциональность"
gh label create "documentation" --color "0075ca" --description "Улучшения документации"
gh label create "security" --color "ee0701" --description "Вопросы безопасности"
gh label create "performance" --color "fbca04" --description "Оптимизация производительности"
gh label create "needs-triage" --color "ededed" --description "Требует рассмотрения"
gh label create "good-first-issue" --color "7057ff" --description "Хорошо для новичков"
gh label create "help-wanted" --color "008672" --description "Требуется помощь"
gh label create "backend" --color "0e8a16" --description "Backend related"
gh label create "frontend" --color "1d76db" --description "Frontend related"
gh label create "devops" --color "f29513" --description "DevOps/Infrastructure"
gh label create "automated" --color "c2e0c6" --description "Автоматически созданный"
```

## 🔐 GitHub Secrets

Настройте secrets для автоматического деплоя:

### Repository Secrets

```bash
# Через GitHub CLI или веб-интерфейс добавьте:

# Production сервер
PRODUCTION_HOST="your-production-server.com"
PRODUCTION_USER="deploy-user"
PRODUCTION_SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----..."
PRODUCTION_PORT="22"
PRODUCTION_APP_DIR="/opt/app"

# Staging сервер
STAGING_HOST="staging.your-domain.com"
STAGING_USER="deploy-user"
STAGING_SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----..."
STAGING_PORT="22"
STAGING_APP_DIR="/opt/app-staging"

# Уведомления
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
SECURITY_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Security scanning (опционально)
SEMGREP_APP_TOKEN="your-semgrep-token"
```

## 🌍 GitHub Environments

### Создание environments

1. **Staging Environment**
   - Automatic deployment
   - Required reviewers: нет
   - Environment secrets для staging

2. **Production Environment**
   - Manual approval required
   - Required reviewers: минимум 1
   - Protection rules
   - Environment secrets для production

## 🛡️ Branch Protection Rules

Настройте защиту main branch:

**Settings → Branches → Add rule**

- Branch name pattern: `main`
- ✅ Require a pull request before merging
  - ✅ Require approvals (1)
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Required status checks:
    - `Tests Summary`
    - `Backend Tests`
    - `Frontend Tests`
    - `Security Scan`
- ✅ Require conversation resolution before merging
- ✅ Include administrators

## 🔨 Pre-commit Hooks

### Установка и настройка

```bash
# В корне проекта
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# Первый запуск (может занять время)
pre-commit run --all-files

# Обновление hooks
pre-commit autoupdate
```

## 🚀 CI/CD Workflows

### Созданные workflows:

1. **`.github/workflows/test.yml`** - Тестирование
   - Запускается при каждом PR и push
   - Backend и frontend тесты
   - Integration тесты
   - Security scanning

2. **`.github/workflows/deploy.yml`** - Деплой
   - Сборка Docker образов
   - Деплой в staging (автоматический)
   - Деплой в production (manual approval)
   - Rollback при ошибках

3. **`.github/workflows/security.yml`** - Безопасность
   - Еженедельное сканирование
   - Dependency audit
   - Container security
   - Code analysis

## 🎉 Заключение

После выполнения всех шагов у вас будет полностью настроенный GitHub репозиторий с:

- ✅ Автоматическим тестированием
- ✅ Automated security scanning
- ✅ Zero-downtime deployment
- ✅ Code quality checks
- ✅ Proper Git workflow
- ✅ Issue и PR templates
- ✅ Monitoring и notifications

Теперь можно приступать к разработке! 🚀

# GitHub Repository Setup Guide

## Branch Protection Setup

### Обязательные Status Checks

Для правильной работы CI/CD pipeline настройте следующие status checks в Branch Protection Rules:

#### Required Status Checks:
- `🔍 Detect Changes`
- `🐍 Backend Lint` (для backend изменений)
- `🐍 Backend Tests` (для backend изменений)
- `⚛️ Frontend Lint` (для frontend изменений)
- `⚛️ Frontend Tests` (для frontend изменений)
- `🐳 Docker Build` (для Docker изменений)
- `🔗 Integration Test` (если backend и frontend тесты прошли)
- `✅ CI Status` (финальный статус)

#### Настройка через веб-интерфейс:

1. Перейдите в **Settings → Branches**
2. Нажмите **Add rule** или отредактируйте существующее правило
3. Укажите **Branch name pattern**: `main`
4. Включите **Require status checks to pass before merging**
5. Включите **Require branches to be up to date before merging**
6. В поле поиска status checks добавьте:
   - `🔍 Detect Changes`
   - `🐍 Backend Lint`
   - `🐍 Backend Tests`
   - `⚛️ Frontend Lint`
   - `⚛️ Frontend Tests`
   - `🐳 Docker Build`
   - `🔗 Integration Test`
   - `✅ CI Status`

#### Настройка через GitHub CLI:

```bash
# Установка branch protection для main
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["🔍 Detect Changes","🐍 Backend Lint","🐍 Backend Tests","⚛️ Frontend Lint","⚛️ Frontend Tests","🐳 Docker Build","🔗 Integration Test","✅ CI Status"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

### Рекомендуемые настройки:

- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- ✅ **Require pull request reviews before merging** (минимум 1)
- ✅ **Dismiss stale pull request reviews when new commits are pushed**
- ✅ **Require review from code owners**
- ✅ **Include administrators**
- ✅ **Allow force pushes** (отключено)
- ✅ **Allow deletions** (отключено)

### Troubleshooting Status Checks

#### Проблема: Status checks не отображаются

1. **Проверьте workflow файл**:
   - Убедитесь, что workflow запускается на `pull_request` событиях
   - Проверьте, что job names точно совпадают с указанными в branch protection

2. **Проверьте permissions**:
   ```yaml
   permissions:
     contents: read
     checks: write
     pull-requests: write
   ```

3. **Проверьте trigger условия**:
   - Workflow должен запускаться на нужных ветках
   - Убедитесь, что условия `if:` не блокируют выполнение

4. **Проверьте зависимости между jobs**:
   - Убедитесь, что `needs:` правильно настроены
   - Избегайте циклических зависимостей

#### Проблема: Status checks показывают неправильный статус

1. **Проверьте финальный job**:
   - `ci-status` job должен корректно анализировать результаты
   - Убедитесь, что `if: always()` не маскирует ошибки

2. **Проверьте условия в jobs**:
   - Убедитесь, что условия `if:` корректны
   - Проверьте, что skipped jobs не вызывают ложных негативов

### Мониторинг Status Checks

#### Просмотр статуса через GitHub CLI:
```bash
# Проверка статуса PR
gh pr status

# Проверка конкретного PR
gh pr view 123 --json statusCheckRollup

# Проверка последнего commit
gh api repos/:owner/:repo/commits/:sha/status
```

#### Просмотр в веб-интерфейсе:
1. Откройте Pull Request
2. Прокрутите до секции **Checks**
3. Нажмите на конкретный check для просмотра деталей
4. Используйте **Re-run jobs** при необходимости

### Автоматизация

#### GitHub Actions для автоматической настройки:
```yaml
name: Setup Repository

on:
  workflow_dispatch:

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - name: Setup branch protection
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.repos.updateBranchProtection({
              owner: context.repo.owner,
              repo: context.repo.repo,
              branch: 'main',
              required_status_checks: {
                strict: true,
                contexts: [
                  '🔍 Detect Changes',
                  '🐍 Backend Lint',
                  '🐍 Backend Tests',
                  '⚛️ Frontend Lint',
                  '⚛️ Frontend Tests',
                  '🐳 Docker Build',
                  '🔗 Integration Test',
                  '✅ CI Status'
                ]
              },
              enforce_admins: true,
              required_pull_request_reviews: {
                required_approving_review_count: 1,
                dismiss_stale_reviews: true
              },
              restrictions: null,
              allow_force_pushes: false,
              allow_deletions: false
            });
```
