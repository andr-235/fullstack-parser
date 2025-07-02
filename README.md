# Fullstack Application Architecture

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
│   │   ├── db/             # Database layer
│   │   ├── utils/          # Утилиты
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Тесты backend
│   ├── alembic/            # Миграции БД
│   ├── Dockerfile          # Backend container
│   ├── requirements.txt    # Python зависимости
│   └── .env.example        # Пример переменных
├── frontend/               # Next.js приложение
│   ├── src/
│   │   ├── app/            # App Router (Next.js 14)
│   │   ├── components/     # Переиспользуемые компоненты
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Утилиты и конфигурация
│   │   ├── services/       # API calls
│   │   └── types/          # TypeScript типы
│   ├── public/             # Статические файлы
│   ├── tests/              # Тесты frontend
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

## 🔧 Development Workflow

1. **Feature branch workflow**
```bash
git checkout -b feature/new-feature
# Разработка
git commit -m "feat: добавлена новая функция"
git push origin feature/new-feature
# Создать Pull Request
```

2. **Тестирование**
```bash
# Backend тесты
cd backend && python -m pytest

# Frontend тесты
cd frontend && npm test

# E2E тесты
npm run test:e2e
```

3. **Code quality**
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

## 🔄 CI/CD

GitHub Actions pipeline:
- Automated testing на каждый push
- Docker image building
- Security scanning
- Automated deployment на main branch
- Rollback capability

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