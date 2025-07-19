---
title: "Cursor AI Rules - Fullstack Parser Project"
description: "Обязательные правила и рекомендации для работы с Cursor AI в проекте Fullstack Parser"
version: "1.0.0"
last_updated: "2025-01-15"
tags: ["cursor-rules", "development-guidelines", "fullstack", "fastapi", "nextjs"]
---

# CURSOR AI RULES - Fullstack Parser Project
# ================================================

## 📁 Структура правил

Данный проект использует новый формат **Project Rules** от Cursor AI. Правила хранятся в директории [.cursor/rules/](mdc:.cursor/rules/) и автоматически применяются в зависимости от контекста:

### 🎯 Типы правил

#### 1. **Always Applied** (Всегда применяется)
- [project-architecture.mdc](mdc:.cursor/rules/project-architecture.mdc) - базовые принципы архитектуры

#### 2. **Auto Attached** (Автоматически подключается)
- [fastapi-backend.mdc](mdc:.cursor/rules/fastapi-backend.mdc) → `backend/**/*.py`
- [nextjs-frontend.mdc](mdc:.cursor/rules/nextjs-frontend.mdc) → `frontend/**/*.{ts,tsx}`
- [docker-deployment.mdc](mdc:.cursor/rules/docker-deployment.mdc) → `**/Dockerfile`, `**/docker-compose*.yml`
- [testing-standards.mdc](mdc:.cursor/rules/testing-standards.mdc) → `**/*.test.{py,ts}`, `**/tests/**/*`

#### 3. **Agent Requested** (По запросу AI)
- [security-guidelines.mdc](mdc:.cursor/rules/security-guidelines.mdc) - AI сам решает когда применить security правила

### 🚀 Преимущества новой системы
- **Контекстно-зависимые советы** - правила применяются автоматически
- **Модульность** - каждое правило фокусируется на конкретной области
- **Version Control** - все правила в Git с историей изменений
- **Производительность** - загружаются только релевантные правила

## 1. ВВЕДЕНИЕ

### 1.1 Назначение документа
Данный документ содержит обязательные правила и рекомендации для работы с Cursor AI в проекте Fullstack Parser. Правила основаны на индустриальных стандартах и лучших практиках разработки fullstack приложений.

### 1.2 Основные цели использования Cursor AI
- Ускорение разработки с сохранением качества кода
- Соблюдение архитектурных принципов проекта
- Автоматизация рутинных задач
- Обеспечение безопасности и производительности
- Поддержка единого стиля кодирования

### 1.3 Архитектура проекта
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis
- Frontend: Next.js 14 + TypeScript + TailwindCSS
- Infrastructure: Docker + Nginx + Docker Compose
- CI/CD: GitHub Actions + автоматический деплой

## 2. ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА

### 2.1 Управление зависимостями

#### Backend: ВСЕГДА используй Poetry для управления зависимостями
- Команда: `poetry add <package>` вместо `pip install`
- Фиксируй версии в pyproject.toml
- НЕ используй pip напрямую

#### Frontend: ВСЕГДА используй pnpm
- Команда: `pnpm add <package>` вместо npm install
- Используй pnpm-lock.yaml для фиксации версий

### 2.2 Git workflow
- ВСЕГДА создавай ветки от main: `git checkout -b feature/name`
- ВСЕГДА используй conventional commits:
  - feat: новая функциональность
  - fix: исправление ошибки
  - docs: изменения в документации
  - style: форматирование кода
  - refactor: рефакторинг
  - test: добавление тестов
  - chore: обновление зависимостей, CI/CD

- НЕ коммить .env файлы в репозиторий
- ВСЕГДА используй .env.example для шаблонов переменных окружения

### 2.3 Docker и деплой
- ВСЕГДА используй Docker Compose для локальной разработки
- ВСЕГДА используй внешние образы для production (ghcr.io/andr-235/*)
- НЕ хардкоди переменные окружения в docker-compose.yml
- ВСЕГДА используй environment variables из .env файлов

### 2.4 Безопасность
- НЕ хардкоди секреты в коде
- ВСЕГДА используй environment variables для конфиденциальных данных
- ВСЕГДА валидируй входные данные через Pydantic (backend) и Zod (frontend)
- ВСЕГДА используй HTTPS в production

## 3. РЕКОМЕНДУЕМЫЕ ПРАВИЛА

### 3.1 Структура кода
- Следуй принципам Clean Architecture
- Разделяй бизнес-логику и представление
- Используй dependency injection
- Пиши тесты для критической функциональности

### 3.2 Производительность
- Используй асинхронные операции для I/O операций
- Кэшируй часто используемые данные в Redis
- Оптимизируй запросы к базе данных
- Используй lazy loading для компонентов

### 3.3 Мониторинг и логирование
- Используй structured logging (JSON формат)
- Добавляй health check endpoints
- Мониторь производительность и ошибки
- Настрой alerting для критических ошибок

## 4. ПРИМЕРЫ КОРРЕКТНОГО И НЕКОРРЕКТНОГО ПОВЕДЕНИЯ

### 4.1 Управление зависимостями

✅ КОРРЕКТНО:
```bash
# Backend
poetry add fastapi
poetry add --group dev pytest

# Frontend
pnpm add react-query
pnpm add -D @types/node
```

❌ НЕКОРРЕКТНО:
```bash
# Backend
pip install fastapi
npm install react-query  # в frontend проекте
```

### 4.2 Git коммиты

✅ КОРРЕКТНО:
```bash
git commit -m "feat: добавлена аутентификация через JWT"
git commit -m "fix: исправлена валидация email адресов"
git commit -m "docs: обновлена документация API"
```

❌ НЕКОРРЕКТНО:
```bash
git commit -m "добавил что-то"
git commit -m "fix"
git commit -m "WIP"
```

### 4.3 Environment variables

✅ КОРРЕКТНО:
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    secret_key: str = Field(alias="SECRET_KEY")
```

❌ НЕКОРРЕКТНО:
```python
# Хардкод секретов
DATABASE_URL = "postgresql://user:pass@localhost/db"
SECRET_KEY = "my-secret-key"
```

## 5. ИНСТРУКЦИИ ПО РАБОТЕ С ИСХОДНЫМ КОДОМ

### 5.1 Создание новых функций

1. Создай ветку от main:
```bash
git checkout -b feature/new-feature
```

2. Разработай функциональность:
   - Backend: создай API endpoint в app/api/v1/
   - Frontend: создай компонент в components/ или страницу в app/
   - Добавь тесты в tests/

3. Протестируй локально:
```bash
# Backend
cd backend && poetry run pytest

# Frontend
cd frontend && pnpm test
```

4. Создай коммит:
```bash
git add .
git commit -m "feat: добавлена новая функция"
```

5. Создай Pull Request в main

### 5.2 Работа с базой данных

1. Создай миграцию:
```bash
cd backend
poetry run alembic revision --autogenerate -m "description"
```

2. Примени миграцию:
```bash
poetry run alembic upgrade head
```

3. Обнови модели в app/models/

### 5.3 Деплой

1. Убедись что все тесты проходят
2. Создай Pull Request в main
3. После merge автоматически запустится CI/CD
4. Проверь статус деплоя в GitHub Actions

## 6. ТРЕБОВАНИЯ К ОФОРМЛЕНИЮ И СТИЛЮ КОДА

### 6.1 Backend (Python/FastAPI)

> 📋 **Подробные правила**: [fastapi-backend.mdc](mdc:.cursor/rules/fastapi-backend.mdc)

#### Форматирование
- Line length: 79 символов
- Используй Black для форматирования
- Используй isort для сортировки импортов
- Используй Ruff для линтинга

#### Структура файлов
```
backend/app/
├── api/v1/          # API endpoints
├── core/            # Конфигурация, security
├── models/          # SQLAlchemy модели
├── schemas/         # Pydantic схемы
├── services/        # Бизнес логика
└── workers/         # Background tasks
```

#### Стиль кода
```python
# ✅ КОРРЕКТНО
from typing import Optional, List
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8)

async def create_user(user_data: UserCreate) -> User:
    """Создает нового пользователя."""
    hashed_password = hash_password(user_data.password)
    return await user_service.create(email=user_data.email, password=hashed_password)
```

```python
# ❌ НЕКОРРЕКТНО
def create_user(email, password):
    # Нет type hints
    # Нет валидации
    # Нет docstring
    pass
```

### 6.2 Frontend (TypeScript/Next.js)

> 📋 **Подробные правила**: [nextjs-frontend.mdc](mdc:.cursor/rules/nextjs-frontend.mdc)

#### Форматирование
- Используй Prettier для форматирования
- Используй ESLint для линтинга
- Line length: 80 символов
- Используй single quotes

#### Структура файлов
```
frontend/
├── app/             # Next.js App Router
├── components/      # Переиспользуемые компоненты
├── hooks/           # Custom React hooks
├── lib/             # Утилиты
├── types/           # TypeScript типы
└── features/        # Feature-based структура
```

#### Стиль кода
```typescript
// ✅ КОРРЕКТНО
import { useState } from 'react'
import { z } from 'zod'

interface User {
  id: string
  email: string
  name: string
}

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
})

export function UserForm({ onSubmit }: { onSubmit: (user: User) => void }) {
  const [formData, setFormData] = useState({ email: '', name: '' })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validated = userSchema.parse(formData)
    onSubmit(validated)
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  )
}
```

```typescript
// ❌ НЕКОРРЕКТНО
function UserForm(props) {
  // Нет типизации
  // Нет валидации
  // Нет обработки ошибок
  return <div>form</div>
}
```

### 6.3 Docker

> 📋 **Подробные правила**: [docker-deployment.mdc](mdc:.cursor/rules/docker-deployment.mdc)

#### Dockerfile best practices
```dockerfile
# ✅ КОРРЕКТНО
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .
RUN poetry run python -m pytest

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

```dockerfile
# ❌ НЕКОРРЕКТНО
FROM python:3.11
COPY . .
RUN pip install -r requirements.txt
# Нет многоэтапной сборки
# Нет оптимизации слоев
```

## 7. МЕРЫ БЕЗОПАСНОСТИ

> 📋 **Подробные правила**: [security-guidelines.mdc](mdc:.cursor/rules/security-guidelines.mdc)

### 7.1 Обязательные меры
- ВСЕГДА используй HTTPS в production
- ВСЕГДА валидируй входные данные
- ВСЕГДА используй prepared statements для SQL
- ВСЕГДА хешируй пароли (bcrypt)
- ВСЕГДА используй JWT токены с коротким временем жизни
- ВСЕГДА настрой CORS правильно

### 7.2 Обращение с секретами
- НЕ коммить .env файлы
- НЕ хардкоди секреты в коде
- Используй GitHub Secrets для CI/CD
- Ротация секретов каждые 90 дней

### 7.3 Логирование безопасности
```python
# ✅ КОРРЕКТНО
import structlog

logger = structlog.get_logger()

def login_user(email: str, password: str):
    try:
        user = authenticate_user(email, password)
        logger.info("user_login_successful", user_id=user.id, email=email)
        return user
    except AuthenticationError:
        logger.warning("user_login_failed", email=email, reason="invalid_credentials")
        raise
```

## 8. ВЗАИМОДЕЙСТВИЕ ПОЛЬЗОВАТЕЛЕЙ

### 8.1 Коммуникация
- Используй GitHub Issues для багов и feature requests
- Используй GitHub Discussions для обсуждений
- Используй Pull Request reviews для code review
- Отвечай на комментарии в течение 24 часов

### 8.2 Code Review
- ВСЕГДА ревью код перед merge в main
- Проверяй:
  - Соответствие стандартам кода
  - Покрытие тестами
  - Безопасность
  - Производительность
  - Документацию

### 8.3 Разрешение конфликтов
- Обсуждай технические решения в Issues
- Используй GitHub Discussions для архитектурных решений
- При разногласиях - следуй принципу "лучше работает"
- Документируй принятые решения

## 9. ИНСТРУМЕНТЫ И АВТОМАТИЗАЦИЯ

### 9.1 Backend инструменты
- Poetry: управление зависимостями
- Black: форматирование кода
- isort: сортировка импортов
- Ruff: линтинг
- mypy: проверка типов
- pytest: тестирование
- bandit: security scanning

### 9.2 Frontend инструменты
- pnpm: управление зависимостями
- Prettier: форматирование
- ESLint: линтинг
- TypeScript: типизация
- Jest: тестирование
- React Testing Library: тестирование компонентов

### 9.3 CI/CD инструменты
- GitHub Actions: автоматизация
- Docker: контейнеризация
- Docker Compose: оркестрация
- Nginx: reverse proxy
- Let's Encrypt: SSL сертификаты

## 10. МОНИТОРИНГ И ОТЛАДКА

### 10.1 Логирование
```python
# ✅ КОРРЕКТНО
import structlog

logger = structlog.get_logger()

logger.info("user_action", 
    user_id=user.id, 
    action="login", 
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

### 10.2 Health checks
```python
# ✅ КОРРЕКТНО
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### 10.3 Error handling
```python
# ✅ КОРРЕКТНО
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except DatabaseError as e:
        logger.error("database_error", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 11. ПРОИЗВОДИТЕЛЬНОСТЬ И ОПТИМИЗАЦИЯ

### 11.1 Database optimization
- Используй индексы для часто запрашиваемых полей
- Используй connection pooling
- Оптимизируй запросы (N+1 problem)
- Используй Redis для кэширования

### 11.2 Frontend optimization
- Используй React.memo для компонентов
- Используй useMemo и useCallback
- Lazy loading для компонентов
- Code splitting
- Оптимизация изображений

### 11.3 API optimization
- Используй pagination для больших списков
- Используй compression (gzip)
- Кэшируй статические данные
- Используй background tasks для тяжелых операций

## 12. ТЕСТИРОВАНИЕ

> 📋 **Подробные правила**: [testing-standards.mdc](mdc:.cursor/rules/testing-standards.mdc)

### 12.1 Backend тестирование
```python
# ✅ КОРРЕКТНО
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json={
            "email": "test@example.com",
            "password": "password123"
        })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### 12.2 Frontend тестирование
```typescript
// ✅ КОРРЕКТНО
import { render, screen, fireEvent } from '@testing-library/react'
import { UserForm } from './UserForm'

test('submits form with valid data', () => {
  const mockSubmit = jest.fn()
  render(<UserForm onSubmit={mockSubmit} />)
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' },
  })
  fireEvent.click(screen.getByRole('button', { name: /submit/i }))
  
  expect(mockSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
  })
})
```

## 13. ДОКУМЕНТАЦИЯ

### 13.1 API документация
- Используй автоматическую генерацию через FastAPI
- Добавляй описания для всех endpoints
- Включай примеры запросов и ответов
- Документируй коды ошибок

### 13.2 Код документация
```python
# ✅ КОРРЕКТНО
def create_user(email: str, password: str) -> User:
    """
    Создает нового пользователя в системе.
    
    Args:
        email: Email адрес пользователя
        password: Пароль пользователя (минимум 8 символов)
    
    Returns:
        User: Созданный пользователь
    
    Raises:
        ValidationError: Если данные некорректны
        DuplicateUserError: Если пользователь уже существует
    """
    pass
```

## 14. ИСПОЛЬЗОВАНИЕ CURSOR RULES

### 14.1 Как работают правила
1. **Автоматическое применение** - правила активируются при работе с соответствующими файлами
2. **Контекстная помощь** - AI предоставляет релевантные советы в зависимости от типа файла
3. **Ссылки на файлы** - используйте формат `[filename](mdc:path/to/file)` для ссылок в правилах

### 14.2 Управление правилами
- **Просмотр**: `Cursor Settings` → `Rules` → список всех правил
- **Редактирование**: напрямую в файлах `.cursor/rules/*.mdc`
- **Создание новых**: `Cmd/Ctrl + Shift + P` → "New Cursor Rule"
- **Генерация из чата**: `/Generate Cursor Rules`

### 14.3 Структура правил
```
.cursor/rules/
├── project-architecture.mdc    # Всегда применяется
├── fastapi-backend.mdc         # Auto для Python файлов
├── nextjs-frontend.mdc         # Auto для TS/React файлов
├── docker-deployment.mdc       # Auto для Docker файлов
├── testing-standards.mdc       # Auto для тестовых файлов
└── security-guidelines.mdc     # По запросу AI
```

## 15. ЗАКЛЮЧЕНИЕ

Соблюдение данных правил обеспечивает:
- Высокое качество кода
- Безопасность приложения
- Производительность системы
- Легкость поддержки и развития
- Эффективную работу команды

### 📚 Дополнительные ресурсы
- [Официальная документация Cursor Rules](https://docs.cursor.com/context/rules)
- [Примеры community rules](https://github.com/PatrickJS/awesome-cursorrules)
- [MDC формат документации](https://docs.cursor.com/context/rules#example-mdc-rule)

Все участники проекта обязаны следовать данным правилам. При возникновении вопросов или предложений по улучшению правил - создавайте Issues в репозитории.
