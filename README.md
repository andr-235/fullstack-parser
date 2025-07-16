# 🚀 Fullstack Parser

Современное fullstack приложение для парсинга и анализа данных ВКонтакте с использованием FastAPI и Next.js.

## 🏗️ Архитектура проекта

Современное fullstack приложение для деплоя на Debian 12 сервер:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Next.js 14 + TypeScript + TailwindCSS
- **Infrastructure**: Docker + Nginx + Redis
- **Deployment**: Docker Compose на Debian 12

## 📁 Структура проекта

```
project-root/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   └── v1/         # API версии
│   │   ├── core/           # Конфигурация, security
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес логика
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Тесты backend
│   ├── Dockerfile          # Backend container
│   └── pyproject.toml      # Python зависимости
├── frontend/               # Next.js приложение
│   ├── app/                # App Router (Next.js 14)
│   ├── components/         # Переиспользуемые компоненты
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Утилиты и конфигурация
│   ├── types/              # TypeScript типы
│   ├── public/             # Статические файлы
│   ├── Dockerfile          # Frontend container
│   ├── package.json        # Node.js зависимости
│   └── next.config.js      # Next.js конфигурация
├── nginx/                  # Reverse proxy
│   ├── nginx.conf          # Продакшен конфигурация
│   └── ssl/                # SSL сертификаты
├── scripts/                # Деплой и утилиты
│   ├── deploy.sh           # Скрипт деплоя
│   ├── backup.sh           # Backup PostgreSQL
│   └── setup-server.sh     # Настройка Debian 12
├── docker-compose.yml      # Локальная разработка
├── docker-compose.prod.yml # Продакшен
├── .env.example            # Переменные окружения
├── .gitignore              # Git ignore
└── README.md               # Документация
```

## 🛠️ Технический стек

### Backend (FastAPI)
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и сессии
- **Alembic** - Миграции БД
- **Pydantic** - Валидация данных
- **pytest** - Тестирование
- **Uvicorn** - ASGI server

### Frontend (Next.js)
- **Next.js 14** - React framework с App Router
- **TypeScript** - Статическая типизация
- **TailwindCSS** - Utility-first CSS framework
- **React Query** - State management и кэширование
- **Zod** - Валидация схем
- **React Hook Form** - Управление формами
- **Jest + Testing Library** - Тестирование

### Infrastructure
- **Docker** - Контейнеризация
- **Nginx** - Reverse proxy + SSL termination
- **PostgreSQL** - База данных
- **Redis** - Кэш и session storage
- **Let's Encrypt** - SSL сертификаты

## 🔒 Безопасность

- JWT токены для аутентификации
- OAuth2 с PKCE flow
- Rate limiting на API уровне
- CORS конфигурация
- Input validation через Pydantic
- SQL injection protection через SQLAlchemy
- Security headers в Nginx
- Environment variables для secrets

## 🚀 Быстрый старт

1. **Клонировать репозиторий**
```bash
git clone <repo-url>
cd project-root
```

2. **Настроить переменные окружения**
```bash
cp .env.example .env
# Отредактировать .env файл
```

3. **Запустить для разработки**
```bash
docker-compose up -d
```

4. **Приложение доступно на:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 Deployment на Debian 12

### Подготовка сервера
```bash
# Установка Docker и dependencies
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Деплой приложения
```bash
# Клонировать проект
git clone <repo-url> /opt/app
cd /opt/app

# Настроить production переменные
cp .env.example .env.prod
# Отредактировать .env.prod

# Запустить в продакшене
docker-compose -f docker-compose.prod.yml up -d
```

### Настройка SSL
```bash
# Установка certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com

# Автообновление сертификата
sudo crontab -e
# Добавить: 0 2 * * * certbot renew --quiet
```

## 🚀 CI/CD для одного разработчика

Проект поддерживает **два режима CI/CD**:

### 🎯 Упрощённый CI/CD (рекомендуется для одного разработчика)
- **Быстрые тесты** - только критичные проверки
- **Прямой деплой** - без staging, сразу в production
- **Автоматические теги** - по коммитам в main
- **Простой workflow** - минимум сложности

```bash
# Быстрый старт
make dev          # Запуск разработки
make test         # Быстрые тесты
make deploy       # Деплой в production
./scripts/quick-deploy.sh  # Полный деплой с проверками

# Переключение CI/CD
./scripts/switch-cicd.sh   # Переключение между режимами
```

📖 **Документация**: [docs/SINGLE_DEV_CICD.md](docs/SINGLE_DEV_CICD.md)

### 🔧 Классический CI/CD (для команды)
- **Полные проверки** - линтинг, тесты, security scans
- **Staging environment** - промежуточное тестирование
- **Code review** - обязательные PR
- **Advanced monitoring** - детальная аналитика

## 🔧 Development Workflow

### Упрощённый workflow (один разработчик)
```bash
make branch       # Создать ветку
# Разработка
make test         # Быстрые тесты
make commit       # Коммит
make push         # Пуш
make pr           # Создать PR
# Merge в main → автоматический деплой
```

### Классический workflow (команда)
```bash
git checkout -b feature/new-feature
# Разработка
git commit -m "feat: добавлена новая функция"
git push origin feature/new-feature
# Создать Pull Request с review
```

### Тестирование
```bash
# Быстрые тесты (упрощённый режим)
make test

# Полные тесты (классический режим)
cd backend && python -m pytest
cd frontend && npm test
npm run test:e2e
```

### Code quality
```bash
# Backend linting
cd backend && ruff check . && black . && isort .

# Frontend linting
cd frontend && npm run lint && npm run format
```

## 📊 Мониторинг

- Health check endpoints для всех сервисов
- Structured logging в JSON формате
- Error tracking и alerting
- Resource usage monitoring

## 🤖 Cursor AI Integration

Проект настроен с **Cursor Project Rules** для улучшенного AI-assisted development:

- **Автоматические правила** для backend/frontend разработки
- **Контекстно-зависимые** советы по архитектуре
- **Security best practices** встроены в AI подсказки
- **Testing patterns** для pytest и React Testing Library

📖 **Подробнее**: [Cursor Rules Documentation](docs/CURSOR_RULES.md)

### Правила активируются автоматически:
- `backend/**/*.py` → FastAPI + SQLAlchemy patterns
- `frontend/**/*.{ts,tsx}` → Next.js + React patterns
- `**/Dockerfile` → Docker best practices
- `**/*.test.*` → Testing standards
- Security guidelines → По запросу AI
- Database performance monitoring

## CI/CD и автоматизация

В проекте реализована современная система CI/CD на базе GitHub Actions:
- Проверка кода (линтинг, автоформат, тесты) для backend и frontend
- Кэширование зависимостей (Poetry, pnpm, Docker buildx)
- Сканирование зависимостей (poetry check, pip-audit, pnpm audit)
- Минимальные права для всех jobs (principle of least privilege)
- Параллелизм и fail-fast для matrix jobs
- Уведомления о деплое в Telegram
- Автоматический деплой и публикация Docker-образов

Подробнее: [docs/CI_FIXES.md](docs/CI_FIXES.md)

## 🚀 Релизы и CI/CD

### Автоматизированные релизы

Проект использует современную систему релизов с полной автоматизацией:

#### 🏷️ Семантическое версионирование
- **MAJOR.MINOR.PATCH** формат (например: 1.2.3)
- Автоматическое обновление версий в backend и frontend
- Поддержка pre-release версий (beta, rc)

#### 🔄 Процесс создания релиза

**Автоматический способ (рекомендуется):**
```bash
# Создание нового релиза
make release-create
# или
./scripts/create-release.sh
```

**Ручной способ:**
```bash
# Создание тега
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

#### 🛠️ GitHub Actions Workflow

При создании тега автоматически запускается полный pipeline:

1. **🛡️ Валидация** - Проверка версии и параметров
2. **🔒 Безопасность** - Сканирование уязвимостей (Trivy)
3. **📦 Зависимости** - Проверка обновлений и уязвимостей
4. **🧪 Тестирование** - Backend и frontend тесты с покрытием
5. **🐳 Сборка** - Docker образы для всех сервисов
6. **📦 Публикация** - GitHub Container Registry
7. **🎉 Release** - GitHub Release с автоматическим changelog
8. **🚀 Деплой** - Автоматический деплой на staging
9. **📢 Уведомления** - Команда получает уведомления

#### 📊 Мониторинг релизов

- **GitHub Actions**: Отслеживание прогресса сборки
- **Docker Hub**: Публикация образов с тегами
- **Coverage**: Отчеты о покрытии тестами
- **Security**: Сканирование уязвимостей

#### 🔄 Управление релизами

```bash
# Создание релиза
make release-create

# Деплой версии
make release-deploy

# Откат к предыдущей версии
make release-rollback

# Статус текущих версий
make release-status
```

📖 **Подробная документация**: [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md)

### CI/CD Pipeline

- ✅ Automated testing на каждый push
- 🐳 Docker image building с кэшированием
- 🔒 Security scanning (Trivy, dependency audit)
- 🚀 Automated deployment на main branch
- 🔄 Rollback capability
- 📊 Coverage reporting
- 📢 Team notifications

## 📝 Дополнительная документация

- [Backend API Documentation](./backend/README.md)
- [Frontend Development Guide](./frontend/README.md)
- [Deployment Guide](./docs/deployment.md)
- [Contributing Guidelines](./docs/contributing.md)

## 🆘 Поддержка

Для вопросов и проблем:
1. Проверьте [FAQ](./docs/faq.md)
2. Создайте [Issue](../../issues)
3. Обратитесь к команде разработки

## ✅ Тестирование Branch Protection

Этот проект настроен с GitHub branch protection rules для обеспечения качества кода.
