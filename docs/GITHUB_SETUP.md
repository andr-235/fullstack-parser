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

### Обязательные Status Checks

Для полной уверенности в качестве и безопасности кода, настройте следующие status checks в Branch Protection Rules для веток `main` и `develop`.

#### CI Checks (`ci.yml`)
- `🔍 Detect Changes`
- `🐍 Backend Lint`
- `🐍 Backend Tests (3.11)`
- `🐍 Backend Tests (3.12)`
- `⚛️ Frontend Lint`
- `⚛️ Frontend Tests (18)`
- `⚛️ Frontend Tests (20)`
- `🐳 Docker Build`
- `🔗 Integration Test`

#### Security Checks (`security.yml`)
- `🔒 CodeQL Analysis`
- `🔬 Trivy Vulnerability Scan`
- `📦 Dependency Check`

#### Настройка через веб-интерфейс:

1.  Перейдите в **Settings → Branches** вашего репозитория.
2.  Нажмите **Add rule** или отредактируйте существующее правило для `main` или `develop`.
3.  Включите **Require status checks to pass before merging**.
4.  Включите **Require branches to be up to date before merging**.
5.  В поле поиска **Search for status checks** добавьте все перечисленные выше checks.

    *Вы должны запустить workflow хотя бы один раз после этих изменений, чтобы GitHub "увидел" новые job'ы и предложил их в списке.*

#### Настройка через GitHub CLI:

```bash
# Пример команды для ветки main
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  -f required_status_checks='{"strict":true,"checks":[
    {"context":"🔍 Detect Changes"},
    {"context":"🐍 Backend Lint"},
    {"context":"🐍 Backend Tests (3.11)"},
    {"context":"🐍 Backend Tests (3.12)"},
    {"context":"⚛️ Frontend Lint"},
    {"context":"⚛️ Frontend Tests (18)"},
    {"context":"⚛️ Frontend Tests (20)"},
    {"context":"🐳 Docker Build"},
    {"context":"🔗 Integration Test"},
    {"context":"🔒 CodeQL Analysis"},
    {"context":"🔬 Trivy Vulnerability Scan"},
    {"context":"📦 Dependency Check"}
  ]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  -F allow_force_pushes=false \
  -F allow_deletions=false
```

### Рекомендуемые настройки:

-   ✅ **Require status checks to pass before merging**
-   ✅ **Require branches to be up to date before merging**
-   ✅ **Require pull request reviews before merging** (минимум 1)
-   ✅ **Dismiss stale pull request reviews when new commits are pushed**
-   ✅ **Require review from code owners** (если используется `CODEOWNERS`)
-   ✅ **Include administrators**
-   ❌ **Allow force pushes** (отключено)
-   ❌ **Allow deletions** (отключено)

### Troubleshooting Status Checks

#### Проблема: Status checks не отображаются в списке

1.  **Запустите Workflow**: Создайте Pull Request после обновления `.github/workflows/`, чтобы запустить CI и Security workflows. GitHub добавит job'ы в список только после их первого запуска.
2.  **Проверьте `name` job'a**: Имя job'а в workflow файле (`name: ...`) должно точно совпадать с тем, что вы добавляете в `contexts`.
3.  **Проверьте `permissions`**: Убедитесь, что в workflow есть права на `checks: write` и `pull-requests: write`.

#### Проблема: Status check "завис" в состоянии pending

1.  **Проверьте `if` условия**: Убедитесь, что условия `if:` для job'а не блокируют его выполнение. Например, `if: needs.changes.outputs.backend == 'true'`.
2.  **Проверьте `needs` зависимости**: Убедитесь, что все job'ы, от которых зависит текущий, успешно завершились.

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
