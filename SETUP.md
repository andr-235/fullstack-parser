# 🚀 ПОЛНАЯ ИНСТРУКЦИЯ ПО НАСТРОЙКЕ GITHUB ACTIONS WORKFLOWS

## 📋 ОБЗОР СИСТЕМЫ

В вашем проекте настроены следующие workflows:

- **CI/CD Pipeline** (`ci-cd.yml`) - автоматическая сборка, тестирование и развертывание
- **Security Audit** (`security-audit.yml`) - еженедельная проверка безопасности
- **Release Management** (`release.yml`) - автоматизация создания релизов
- **PR Checks** (`pr-checks.yml`) - валидация pull requests

---

## 🔐 1. ОБЯЗАТЕЛЬНЫЕ СЕКРЕТЫ GITHUB

Перейдите в: **Repository Settings → Secrets and variables → Actions**

### SSH и Сервер

```
PRODUCTION_SSH_KEY    # Ваш приватный SSH ключ для доступа к серверу
PRODUCTION_HOST       # IP или домен продакшн сервера
PRODUCTION_USER       # Пользователь сервера для SSH
PRODUCTION_APP_DIR    # Директория приложения на сервере
PRODUCTION_PORT       # Порт для деплоя
```

### GitHub Container Registry (GHCR)

```
GHCR_USERNAME         # Логин GitHub Container Registry
GHCR_TOKEN            # Personal Access Token для GHCR
```

### Slack (опционально)

```
SLACK_WEBHOOK_URL     # Webhook URL для Slack уведомлений
```

### Codecov (опционально)

```
CODECOV_TOKEN         # Токен для Codecov отчетов о покрытии
```

---

## 🛠️ 2. КОНФИГУРАЦИЯ ПРОЕКТА

### Создайте `docker-compose.prod.yml`

```yaml
version: "3.8"
services:
  frontend:
    image: ghcr.io/YOUR_USERNAME/YOUR_REPO/frontend:latest
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    depends_on:
      - backend

  backend:
    image: ghcr.io/YOUR_USERNAME/YOUR_REPO/backend:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis

  nginx:
    image: ghcr.io/YOUR_USERNAME/YOUR_REPO/nginx:latest
    restart: unless-stopped
    ports:
      - "${PRODUCTION_PORT}:80"
      - "443:443"
    depends_on:
      - frontend
      - backend

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### Создайте `.env.prod` на сервере

```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/prod_db
POSTGRES_DB=prod_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-super-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Production
PRODUCTION_PORT=${PRODUCTION_PORT}
PRODUCTION_APP_DIR=${PRODUCTION_APP_DIR}
```

---

## 🖥️ 3. НАСТРОЙКА ПРОДАКШН СЕРВЕРА

### Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Установка Git
sudo apt install git -y
```

### Создание пользователя для деплоя

```bash
# Создание пользователя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Настройка SSH
sudo -u deploy mkdir /home/deploy/.ssh
sudo -u deploy chmod 700 /home/deploy/.ssh

# Добавьте ваш публичный SSH ключ в /home/deploy/.ssh/authorized_keys
echo "your-public-ssh-key-here" | sudo -u deploy tee /home/deploy/.ssh/authorized_keys
sudo -u deploy chmod 600 /home/deploy/.ssh/authorized_keys
```

### Клонирование проекта

```bash
# Переход в домашнюю директорию пользователя deploy
sudo -u deploy bash
cd /home/deploy

# Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git app
cd app

# Создание .env.prod файла
cp .env.example .env.prod

# Отредактируйте .env.prod с продакшн значениями:
# - DATABASE_URL, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
# - REDIS_URL, SECRET_KEY
# - NEXT_PUBLIC_API_URL, PRODUCTION_PORT, PRODUCTION_APP_DIR
```

---

## 🔄 4. ПОШАГОВАЯ НАСТРОЙКА WORKFLOWS

### 4.1 CI/CD Pipeline (`ci-cd.yml`)

**Что делает:**

- Автоматическое тестирование frontend и backend
- Сборка Docker образов
- Push в GitHub Container Registry
- Деплой на продакшн сервер
- Health checks после деплоя

**Необходимые файлы:**

- `docker-compose.prod.yml` (создан выше)
- `.env.prod` на сервере
- Health check endpoints в приложении

**Health Check примеры:**

```python
# backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

```typescript
// frontend/pages/api/health.ts
import { NextApiRequest, NextApiResponse } from "next";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({ status: "healthy" });
}
```

### 4.2 Security Audit (`security-audit.yml`)

**Что делает:**

- Еженедельный аудит зависимостей
- Сканирование Docker образов на уязвимости
- Проверка конфигурации Docker Compose
- Отчеты в artifacts и Slack

**Настройка:**

- Запускается автоматически по понедельникам в 9:00 UTC
- Можно запустить вручную с разными типами аудита
- Результаты сохраняются как artifacts

### 4.3 Release Management (`release.yml`)

**Что делает:**

- Создание GitHub releases при тегах
- Генерация changelog
- Создание Docker образов с версиями
- Автоматическое развертывание

**Настройка:**

- Создает релиз при пуше тега `v*.*.*`
- Обновляет Docker образы с тегом версии
- Деплоит на продакшн

### 4.4 PR Checks (`pr-checks.yml`)

**Что делает:**

- Проверка кода на pull requests
- Линтинг и форматирование
- Запуск тестов
- Проверка типов

---

## 📊 5. МОНИТОРИНГ И ОТЛАДКА

### Просмотр логов workflows

1. Перейдите во вкладку **Actions** в репозитории
2. Выберите нужный workflow
3. Кликните на конкретный запуск
4. Просмотрите логи каждого шага

### Распространенные проблемы

#### ❌ SSH Connection Failed

```bash
# Проверьте SSH ключ
ssh -T git@github.com

# Проверьте доступ к серверу
ssh ${{ secrets.PRODUCTION_USER }}@${{ secrets.PRODUCTION_HOST }}
```

#### ❌ Docker Build Failed

```bash
# Проверьте Dockerfile
docker build -t test .

# Проверьте наличие файлов
ls -la
```

#### ❌ Health Check Failed

```bash
# Проверьте endpoints локально
curl http://localhost:8000/health
curl http://localhost:3000/api/health
```

---

## 🚀 6. ЗАПУСК И ТЕСТИРОВАНИЕ

### Тестовый запуск

1. **Добавьте секреты** в GitHub
2. **Настройте сервер** с Docker и SSH
3. **Создайте необходимые файлы** (docker-compose.prod.yml, .env.prod)
4. **Запустите тестовый деплой:**
   ```bash
   # На develop ветке
   git checkout develop
   git push origin develop
   ```
5. **Проверьте workflows** во вкладке Actions
6. **При успехе** смерджите в main

### Ручной запуск workflows

- **CI/CD**: Автоматически при пуше в main
- **Security Audit**: Вкладка Actions → Security Audit → Run workflow
- **Release**: Создайте git tag `v1.0.0`

---

## 🆘 7. TROUBLESHOOTING

### Workflow не запускается

- Проверьте синтаксис YAML
- Убедитесь что файлы в `.github/workflows/`
- Проверьте права доступа к репозиторию

### Деплой падает

- Проверьте SSH доступ
- Убедитесь что Docker установлен
- Проверьте .env.prod файл

### Тесты падают

- Проверьте переменные окружения
- Убедитесь что сервисы (PostgreSQL, Redis) запущены
- Проверьте coverage reports

---

## 📝 8. ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

### Безопасность

- Регулярно обновляйте секреты
- Используйте principle of least privilege
- Включайте Dependabot для обновления зависимостей

### Производительность

- Кешируйте Docker layers
- Оптимизируйте Dockerfiles
- Используйте GitHub Actions cache

### Мониторинг

- Настройте логирование в приложении
- Добавьте метрики производительности
- Настройте алерты в Slack/Discord

---

## 🎯 ЧЕКЛИСТ ГОТОВНОСТИ

- [x] Секреты добавлены в GitHub (GHCR*USERNAME, GHCR_TOKEN, PRODUCTION*\*)
- [x] Продакшн сервер настроен
- [ ] `docker-compose.prod.yml` создан
- [ ] `.env.prod` настроен
- [ ] Health checks реализованы
- [ ] SSH доступ проверен
- [ ] Docker образы собираются локально
- [ ] Тестовый деплой прошел успешно

---

_Создано для настройки CI/CD pipeline с использованием GitHub Actions, Docker и Docker Compose_ 🚀
