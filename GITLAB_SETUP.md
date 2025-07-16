# Настройка GitLab для одного разработчика

## 🚀 Быстрая настройка

### 1. Создание проекта в GitLab

1. Перейди на [gitlab.com](https://gitlab.com)
2. Нажми "New Project" → "Create blank project"
3. Заполни:
   - **Project name**: `fullstack-parser`
   - **Visibility Level**: Private
   - **Initialize repository with**: НЕ ставь галочки

### 2. Настройка локального репозитория

```bash
# Добавить GitLab как новый remote
git remote add gitlab https://gitlab.com/YOUR_USERNAME/fullstack-parser.git

# Или заменить origin на GitLab
git remote set-url origin https://gitlab.com/YOUR_USERNAME/fullstack-parser.git

# Проверить remotes
git remote -v

# Отправить код в GitLab
git push -u origin main
```

### 3. Настройка CI/CD (опционально)

Создай файл `.gitlab-ci.yml` в корне проекта:

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python -m pytest tests/
  only:
    - main
    - merge_requests

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t fullstack-parser:$CI_COMMIT_SHA .
  only:
    - main

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
  when: manual
```

## 🔧 Дополнительные настройки

### Настройка SSH ключей

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавление в GitLab
# Скопируй содержимое ~/.ssh/id_ed25519.pub в GitLab → Settings → SSH Keys
```

### Настройка Git конфигурации

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### Настройка GitLab Runner (для CI/CD)

1. В GitLab проекте: Settings → CI/CD → Runners
2. Установи GitLab Runner на свой сервер
3. Зарегистрируй runner с токеном из GitLab

## 📋 Рекомендуемые настройки проекта

### Protected Branches

- Settings → Repository → Protected Branches
- Защити `main` ветку от прямых push

### Merge Request Templates

Создай файл `.gitlab/merge_request_templates/default.md`:

```markdown
## Описание изменений

## Тип изменений

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование

- [ ] Локальные тесты пройдены
- [ ] CI/CD pipeline успешен

## Дополнительные заметки
```

### Issue Templates

Создай `.gitlab/issue_templates/bug.md`:

```markdown
## Описание бага

## Шаги для воспроизведения

1.
2.
3.

## Ожидаемое поведение

## Фактическое поведение

## Окружение

- OS:
- Browser:
- Version:
```

## 🎯 Workflow для одного разработчика

### Ежедневная работа

```bash
# Создание новой ветки для задачи
git checkout -b feature/new-feature

# Работа над кодом...

# Commit изменений
git commit -m "feat: add new feature"

# Push в GitLab
git push origin feature/new-feature

# Создание Merge Request в GitLab UI
# После ревью и тестов - merge в main
```

### Автоматизация

- Настрой Webhook для автоматического деплоя
- Используй GitLab Pages для документации
- Настрой автоматические тесты в CI/CD

## 🔒 Безопасность

### Переменные окружения

- Settings → CI/CD → Variables
- Добавь секретные переменные (API keys, passwords)

### Двухфакторная аутентификация

- Settings → Account → Two-Factor Authentication

## 📊 Мониторинг

### Analytics

- GitLab предоставляет встроенную аналитику
- Issues → Analytics
- Repository → Analytics

### Notifications

- Settings → Notifications
- Настрой уведомления о важных событиях
