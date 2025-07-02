# Cursor Project Rules Configuration

Этот проект настроен с современными Cursor Project Rules для улучшения разработки.

## Структура правил

### Git Rules (Auto-attached)
- **git-commit-standards.mdc** - Стандарты коммитов (Conventional Commits)
- **git-branching-strategy.mdc** - Стратегия ветвления Git Flow
- **git-conflict-resolution.mdc** - Решение конфликтов
- **git-workflow.mdc** - Ежедневные git операции

### GitHub Rules (NEW! 🆕)
- **github-workflow.mdc** - GitHub workflow и daily operations
- **github-security-best-practices.mdc** - Комплексная безопасность GitHub
- **github-actions-security.mdc** - Безопасность GitHub Actions
- **github-organization-management.mdc** - Управление организациями

### Docker Rules (Auto-attached)
- **dockerfile-best-practices.mdc** - Security-first Dockerfile практики
- **docker-compose-best-practices.mdc** - Multi-environment Compose
- **docker-production-deployment.mdc** - Production deployment
- **docker-workflow.mdc** - Ежедневные Docker команды

### Development Rules (Auto-attached)
- **python-fastapi-best-practices.mdc** - Современные FastAPI паттерны
- **database-postgresql-best-practices.mdc** - PostgreSQL оптимизация
- **celery-redis-background-tasks.mdc** - Background task processing
- **testing-pytest-best-practices.mdc** - Comprehensive testing

## 🆕 Новые GitHub Rules

### GitHub Workflow (.cursor/rules/github-workflow.mdc)
**Глобы:** `.github/**/*.yml`, `.github/**/*.yaml`, `**/.gitignore`, `**/*.md`, `.git/**`

**Содержание:**
- ⚡ Daily GitHub Commands (базовые и продвинутые git операции)
- 🔄 GitHub Actions Workflow Patterns (CI/CD templates)
- 📋 Pull Request Workflow (чеклисты, templates, code review)
- 🔐 Security Best Practices (dependabot, branch protection)
- 🏷️ Release Management (semantic versioning, changelogs)
- 🔍 Monitoring & Analytics (repository insights, issue management)
- 🚀 Automation Scripts (daily maintenance, release automation)

### GitHub Security Best Practices (.cursor/rules/github-security-best-practices.mdc)
**Глобы:** `.github/**/*.yml`, `.github/**/*.yaml`, `SECURITY.md`, `**/.gitignore`, `**/secrets/**`

**Содержание:**
- 🔐 Account Security Foundation (2FA, SSH keys, GPG signing)
- 🛡️ Repository Security Configuration (branch protection, CODEOWNERS)
- 🔍 Secret Management & Scanning (GitHub secrets, custom patterns)
- 🚨 Dependency Security (Dependabot, vulnerability management)
- 🔒 GitHub Actions Security (secure workflows, pinning)
- 📊 Security Monitoring & Audit (audit logs, metrics)
- 🚀 Incident Response Plan (workflow, emergency scripts)

### GitHub Actions Security (.cursor/rules/github-actions-security.mdc)
**Глобы:** `.github/workflows/**/*.yml`, `.github/workflows/**/*.yaml`, `.github/actions/**/*`

**Содержание:**
- 🚦 Permission Management (minimal GITHUB_TOKEN permissions)
- 🔐 Action Security Pinning (commit SHA pinning, automated updates)
- 🔒 Secrets & Environment Management (secure handling, rotation)
- 🛡️ Input Validation & Injection Prevention (secure input handling)
- 🌐 Network Security (secure networking, private registries)
- 🔍 Monitoring & Logging (security events, anomaly detection)
- 🧪 Security Testing (SAST, container scanning)
- 🚀 Supply Chain Security (dependency verification, provenance)

### GitHub Organization Management (.cursor/rules/github-organization-management.mdc)
**Глобы:** `.github/**/*.yml`, `.github/**/*.yaml`, `SECURITY.md`, `**/CODEOWNERS`

**Содержание:**
- 🏢 Organization Setup & Configuration (initial security, policies)
- 👥 Team Management & Permissions (RBAC, custom roles)
- 🔐 Enterprise Security Features (SAML SSO, IP allowlist)
- 📊 Organization Audit & Monitoring (audit logs, security metrics)
- 🔄 Automated Organization Management (onboarding, templates)
- 📋 Compliance & Governance (compliance scanning, scoring)

## Как использовать GitHub Rules

### 1. Автоматическая активация
Правила автоматически активируются при работе с соответствующими файлами:
- Открытие `.github/workflows/*.yml` → активирует GitHub Actions security
- Редактирование `SECURITY.md` → активирует GitHub security practices
- Работа с GitHub API → активирует organization management

### 2. Ручная активация в чате
```
@github-workflow                    # Workflow и daily operations
@github-security-best-practices     # Комплексная безопасность
@github-actions-security            # Безопасность Actions
@github-organization-management     # Управление организациями
```

### 3. Комбинированное использование
```
@github-workflow @git-workflow      # Полный Git + GitHub workflow
@github-security-best-practices @docker-workflow  # Security + DevOps
```

## Ключевые возможности

### 🚀 Automation & Productivity
- **Daily Commands**: готовые команды для ежедневной работы
- **Workflow Templates**: проверенные CI/CD patterns
- **Release Automation**: автоматизация релизов и тегирования
- **Repository Templates**: стандартизированные шаблоны

### 🔐 Security & Compliance
- **Security Hardening**: comprehensive security guidelines
- **Secret Management**: безопасная работа с секретами
- **Compliance Monitoring**: автоматизированные проверки
- **Incident Response**: готовые планы реагирования

### 👥 Team & Organization
- **Access Control**: RBAC и least privilege
- **Team Management**: структурированное управление командами
- **Onboarding**: автоматизированный процесс
- **Audit & Monitoring**: полная отслеживаемость

### 📊 Analytics & Insights
- **Security Metrics**: дашборды безопасности
- **Compliance Scoring**: автоматическая оценка соответствия
- **Activity Monitoring**: отслеживание активности
- **Reporting**: регулярные отчеты

## Best Practices Highlights

### Security First
- ✅ 2FA обязательна для всех
- ✅ Branch protection на всех критических ветках
- ✅ Secret scanning и push protection
- ✅ Signed commits для критических изменений
- ✅ Regular security audits

### Automation Focus
- ✅ Automated dependency updates
- ✅ Continuous security scanning
- ✅ Automated compliance checks
- ✅ Self-service workflows
- ✅ Incident response automation

### Developer Experience
- ✅ Clear workflows и checklists
- ✅ Helpful templates и examples
- ✅ Quick reference commands
- ✅ Automated code quality checks
- ✅ Streamlined review process

## Интеграция с существующими правилами

GitHub правила отлично интегрируются с существующими:

```
Git Flow → GitHub Workflow → Docker Deployment
   ↓              ↓                 ↓
Git Rules    GitHub Rules    Docker Rules
   ↓              ↓                 ↓
FastAPI Development ← Testing ← Database
```

## 🔗 Quick Links

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [GitHub Organization Management](https://docs.github.com/en/organizations)
- [SLSA Framework](https://slsa.dev/)

---

## Активация правил

Правила `alwaysApply: false` — активируются по файловым паттернам или по запросу в чате.

**Приятной работы с GitHub! 🚀🔐**

## Как использовать

### Автоматическое применение
Правила автоматически применяются когда вы работаете с соответствующими файлами:
- Открываете `.py` файлы → активируются Python/FastAPI правила
- Работаете с `Dockerfile` → активируются Docker правила
- Создаете коммиты → активируются Git правила

### Ручное применение
В чате Cursor используйте:
- `@git-commit-standards` - для помощи с коммитами
- `@dockerfile-best-practices` - для оптимизации Docker
- `@python-fastapi-best-practices` - для FastAPI кода

### Просмотр правил
- Откройте Cursor Settings (Cmd/Ctrl + ,)
- Перейдите в раздел "Project Rules"
- Здесь вы увидите все активные правила

## Конфигурация правил

Каждое правило имеет метаданные:
```yaml
---
description: Описание правила
globs: ["**/*.py", "**/*.js"]  # Файловые паттерны
alwaysApply: false             # Не применять всегда
---
```

### Типы правил:
- **Auto Attached** - автоматически применяются при соответствии файловым паттернам
- **Manual** - применяются только при ручном вызове через @название
- **Always** - применяются ко всем запросам (не рекомендуется)

## Обновление правил

1. Откройте файл правила в `.cursor/rules/`
2. Отредактируйте содержимое
3. Сохраните файл
4. Правила обновятся автоматически

## Создание новых правил

```bash
# Через Command Palette
Cmd/Ctrl + Shift + P → "New Cursor Rule"

# Или создайте файл вручную
touch .cursor/rules/my-new-rule.mdc
```

## Лучшие практики

1. **Держите правила сфокусированными** - одно правило = одна концепция
2. **Используйте точные глобы** - чтобы правила активировались по назначению
3. **Пишите четкие описания** - ИИ должен понимать когда применять правило
4. **Регулярно обновляйте** - адаптируйте под изменения в проекте

## Troubleshooting

### Правила не применяются
1. Проверьте файловые паттерны в `globs`
2. Убедитесь что файл имеет расширение `.mdc`
3. Проверьте синтаксис YAML frontmatter

### Правила конфликтуют
1. Используйте более специфичные глобы
2. Разделите большие правила на мелкие
3. Избегайте `alwaysApply: true`

### Дебаг правил
1. Откройте Developer Console в Cursor
2. Найдите сообщения о правилах
3. Проверьте какие правила активированы 