# Техническое задание: Миграция backend на структуру FastAPI Best Practices

## 📋 Обзор проекта

**Цель:** Перевести существующий FastAPI проект с текущей DDD-архитектуры на рекомендованную структуру из репозитория [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices).

**Текущая версия:** VK Comments Parser API v1.6.0
**Целевая структура:** Netflix-inspired domain-driven structure

---

## 🏗️ Текущая структура проекта

```
/opt/app/backend/
├── app/
│   ├── main.py                           # Точка входа приложения
│   └── api/
│       └── v1/
│           ├── api.py                    # Главный роутер API
│           ├── application/              # Application Services (DDD)
│           │   ├── comment_service.py
│           │   ├── user_service.py
│           │   ├── group_service.py
│           │   ├── monitoring_service.py
│           │   ├── parsing_manager.py
│           │   └── ...
│           ├── domain/                   # Domain Entities (DDD)
│           │   ├── comment.py
│           │   ├── user.py
│           │   ├── group.py
│           │   └── ...
│           ├── infrastructure/           # Infrastructure Layer
│           │   ├── models/               # SQLAlchemy models
│           │   ├── repositories/         # Data repositories
│           │   ├── services/             # Infrastructure services
│           │   └── events/               # Domain events
│           ├── routers/                  # FastAPI routers
│           │   ├── comments.py
│           │   ├── groups.py
│           │   ├── keywords.py
│           │   └── ...
│           ├── schemas/                  # Pydantic schemas
│           ├── middleware/               # Custom middleware
│           ├── handlers/                 # Request handlers
│           ├── exceptions.py             # Exception handlers
│           └── dependencies.py           # Dependencies
├── alembic/                              # Database migrations
├── tests/                                # Test files
├── pyproject.toml                        # Dependencies
└── Dockerfile                            # Container config
```

---

## 🎯 Целевая структура (FastAPI Best Practices)

```
/opt/app/backend/
├── src/
│   ├── auth/                            # 🔐 Authentication module
│   │   ├── router.py                    # API endpoints
│   │   ├── schemas.py                   # Pydantic models
│   │   ├── models.py                    # DB models
│   │   ├── dependencies.py              # FastAPI dependencies
│   │   ├── config.py                    # Module config
│   │   ├── constants.py                 # Module constants
│   │   ├── exceptions.py                # Module exceptions
│   │   ├── service.py                   # Business logic
│   │   └── utils.py                     # Utility functions
│   ├── comments/                        # 💬 Comments module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── groups/                          # 👥 Groups module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── parser/                          # 🔍 Parser module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   ├── client.py                    # External service client
│   │   └── utils.py
│   ├── monitoring/                      # 📊 Monitoring module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── morphological/                   # 🔤 Morphological module
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py                        # 🌐 Global configurations
│   ├── models.py                        # 🗄️ Global database models
│   ├── exceptions.py                    # ⚠️ Global exceptions
│   ├── pagination.py                    # 📄 Pagination utilities
│   ├── database.py                      # 🗃️ Database connection
│   └── main.py                          # 🚀 Application entry point
├── alembic/                             # 🏗️ Database migrations
├── tests/                               # 🧪 Test files
│   ├── auth/
│   ├── comments/
│   ├── groups/
│   └── ...
├── requirements/                        # 📦 Dependencies
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env                                 # 🔑 Environment variables
├── .gitignore                           # 🚫 Git ignore rules
├── logging.ini                          # 📝 Logging configuration
├── alembic.ini                          # 🏗️ Alembic config
└── pyproject.toml                       # 📋 Project metadata
```

---

## 📊 Анализ изменений

### ✅ Преимущества новой структуры

1. **Масштабируемость**: Каждый домен в отдельной папке
2. **Четкость**: Явное разделение ответственности
3. **Поддерживаемость**: Легко найти код по домену
4. **Тестируемость**: Изоляция модулей для тестирования
5. **Стандартизация**: Следование best practices сообщества
6. **Модульность**: Независимые компоненты

### ⚠️ Вызовы миграции

1. **Объем работ**: Перемещение ~20+ файлов
2. **Рефакторинг импортов**: Обновление всех import statements
3. **Тестирование**: Проверка всех эндпоинтов после миграции
4. **Документация**: Обновление всех ссылок на файлы
5. **CI/CD**: Обновление deployment скриптов

---

## 🚀 План миграции

### Этап 1: Подготовка (1-2 дня)

#### 1.1 Создание новой структуры папок

```bash
# Создание основных директорий
mkdir -p src/{auth,comments,groups,parser,monitoring,morphological}
mkdir -p tests/{auth,comments,groups,parser,monitoring,morphological}
mkdir -p requirements
mkdir -p templates

# Создание файлов в каждом модуле
for module in auth comments groups parser monitoring morphological; do
  touch src/$module/{router.py,schemas.py,models.py,dependencies.py,config.py,constants.py,exceptions.py,service.py,utils.py}
  mkdir -p tests/$module
done
```

#### 1.2 Создание базовых конфигурационных файлов

- `src/config.py` - Глобальные настройки
- `src/models.py` - Глобальные модели БД
- `src/exceptions.py` - Глобальные исключения
- `src/pagination.py` - Утилиты пагинации
- `src/database.py` - Подключение к БД
- `requirements/base.txt` - Основные зависимости
- `requirements/dev.txt` - Dev зависимости
- `requirements/prod.txt` - Production зависимости

### Этап 2: Миграция модулей (3-5 дней)

#### 2.1 Миграция домена Comments

**Файлы для миграции:**

- `app/api/v1/application/comment_service.py` → `src/comments/service.py`
- `app/api/v1/domain/comment.py` → `src/comments/models.py`
- `app/api/v1/routers/comments.py` → `src/comments/router.py`
- `app/api/v1/infrastructure/models/comment_model.py` → `src/comments/schemas.py`

**Обновление импортов:**

```python
# Было
from app.api.v1.application.comment_service import CommentService
from app.api.v1.domain.comment import Comment
from app.api.v1.infrastructure.repositories.comment_repository import CommentRepository

# Стало
from src.comments.service import CommentService
from src.comments.models import Comment
from src.comments.dependencies import get_comment_repository
```

#### 2.2 Миграция домена Groups

Аналогично Comments, но с учетом специфики групп VK.

#### 2.3 Миграция домена Parser

**Особенности:**

- Внешний клиент VK API
- Создание `src/parser/client.py` для VK API взаимодействия
- Комплексная бизнес-логика парсинга

#### 2.4 Миграция домена Monitoring

**Особенности:**

- Метрики производительности
- Сбор статистики
- Health checks

#### 2.5 Миграция домена Morphological

**Особенности:**

- Интеграция с pymorphy2
- Анализ текста комментариев

#### 2.6 Миграция домена Auth (создание с нуля)

**Необходимые компоненты:**

- JWT токены
- Пользовательские сессии
- OAuth для VK API

### Этап 3: Глобальные компоненты (1-2 дня)

#### 3.1 Миграция main.py

```python
# Было
from app.api.v1.api import api_router

# Стало
from src.auth.router import router as auth_router
from src.comments.router import router as comments_router
from src.groups.router import router as groups_router
# ... остальные роутеры

app = FastAPI(...)
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(comments_router, prefix="/api/v1/comments")
# ... остальные include_router
```

#### 3.2 Миграция конфигурации

- Перемещение настроек в `src/config.py`
- Создание модульных конфигураций
- Обновление переменных окружения

#### 3.3 Миграция зависимостей

```python
# src/comments/dependencies.py
from src.database import get_db_session
from src.comments.models import Comment
from src.comments.service import CommentService

def get_comment_service() -> CommentService:
    return CommentService()

async def get_comment_repository(db: AsyncSession = Depends(get_db_session)):
    return CommentRepository(db)
```

### Этап 4: Тестирование и валидация (2-3 дня)

#### 4.1 Модульное тестирование

```bash
# Тесты для каждого модуля
pytest tests/comments/ -v
pytest tests/groups/ -v
pytest tests/parser/ -v
# ... остальные модули
```

#### 4.2 Интеграционное тестирование

- Проверка всех API эндпоинтов
- Тестирование базы данных
- Проверка внешних интеграций (VK API)

#### 4.3 Производительность

- Замер времени отклика
- Проверка потребления памяти
- Сравнение с предыдущей версией

### Этап 5: Документация и развертывание (1 день)

#### 5.1 Обновление документации

- README.md с новой структурой
- API документация
- Документация для разработчиков

#### 5.2 Обновление CI/CD

- Dockerfile
- Docker Compose
- Deployment скрипты

---

## 📁 Детальный план файлов

### Модуль Comments

```
src/comments/
├── router.py          # /api/v1/comments/*
├── schemas.py         # CommentCreate, CommentResponse, etc.
├── models.py          # Comment (SQLAlchemy)
├── dependencies.py    # get_comment_service, get_comment_repository
├── config.py          # Настройки модуля комментариев
├── constants.py       # Константы комментариев
├── exceptions.py      # CommentNotFoundError, etc.
├── service.py         # CommentService (бизнес-логика)
└── utils.py           # Утилиты для работы с комментариями
```

### Модуль Groups

```
src/groups/
├── router.py          # /api/v1/groups/*
├── schemas.py         # GroupCreate, GroupResponse, etc.
├── models.py          # Group (SQLAlchemy)
├── dependencies.py    # get_group_service, get_group_repository
├── config.py          # Настройки модуля групп
├── constants.py       # Константы групп
├── exceptions.py      # GroupNotFoundError, etc.
├── service.py         # GroupService (бизнес-логика)
└── utils.py           # Утилиты для работы с группами
```

### Модуль Parser

```
src/parser/
├── router.py          # /api/v1/parser/*
├── schemas.py         # ParseRequest, ParseResponse, etc.
├── models.py          # ParseTask, ParseResult (SQLAlchemy)
├── dependencies.py    # get_parser_service, get_parser_client
├── config.py          # Настройки парсера
├── constants.py       # Константы парсинга
├── exceptions.py      # ParseError, VKAPIError, etc.
├── service.py         # ParserService (основная логика)
├── client.py          # VKAPIClient (внешний сервис)
└── utils.py           # Утилиты парсинга
```

---

## 🛠️ Технические требования

### Python версии

- **Текущая:** Python 3.11+
- **Целевая:** Python 3.11+ (без изменений)

### Зависимости

```toml
# requirements/base.txt
fastapi==0.116.1
uvicorn[standard]==0.35.0
pydantic>=2.5.0,<3.0.0
sqlalchemy>=2.0.25
alembic>=1.13.0
asyncpg==0.30.0
httpx==0.26.0
redis>=4.2.0,<6
# ... остальные зависимости

# requirements/dev.txt
pytest>=8.4.1
black==25.1.0
ruff==0.12.1
mypy==1.8.0
# ... dev зависимости
```

### База данных

- **Текущая:** PostgreSQL + AsyncPG
- **Целевая:** PostgreSQL + AsyncPG (без изменений)

### Кеширование

- **Текущая:** Redis
- **Целевая:** Redis (без изменений)

---

## 📈 Критерии успеха

### Функциональные

- ✅ Все API эндпоинты работают корректно
- ✅ База данных функционирует без ошибок
- ✅ Внешние интеграции (VK API) работают
- ✅ Аутентификация и авторизация работают

### Нефункциональные

- ✅ Производительность не ухудшилась
- ✅ Все тесты проходят
- ✅ Код соответствует стандартам (ruff, black, mypy)
- ✅ Документация обновлена

### Технические

- ✅ Структура соответствует fastapi-best-practices
- ✅ Импорты обновлены во всех файлах
- ✅ Модули изолированы и независимы
- ✅ Конфигурация централизована

---

## ⚠️ Риски и mitigation

### Риск 1: Регрессии в функциональности

**Mitigation:**

- Полное покрытие тестами перед миграцией
- Поэтапная миграция с промежуточными коммитами
- Ручное тестирование всех эндпоинтов

### Риск 2: Проблемы с импортами

**Mitigation:**

- Использование абсолютных импортов
- Статический анализ импортов (mypy, ruff)
- Автоматизированные скрипты проверки

### Риск 3: Увеличение времени разработки

**Mitigation:**

- Параллельная разработка (новая структура + поддержка старой)
- Автоматизация рутинных задач
- Четкое планирование этапов

---

## 📅 Оценка времени

| Этап                   | Время   | Ответственный          |
| ---------------------- | ------- | ---------------------- |
| Подготовка структуры   | 1-2 дня | Backend Developer      |
| Миграция Comments      | 1 день  | Backend Developer      |
| Миграция Groups        | 1 день  | Backend Developer      |
| Миграция Parser        | 1 день  | Backend Developer      |
| Миграция Monitoring    | 0.5 дня | Backend Developer      |
| Миграция Morphological | 0.5 дня | Backend Developer      |
| Миграция Auth          | 1 день  | Backend Developer      |
| Глобальные компоненты  | 1 день  | Backend Developer      |
| Тестирование           | 2-3 дня | QA + Backend Developer |
| Документация           | 0.5 дня | Technical Writer       |

**Общее время:** 9-11 дней
**Команда:** 1-2 Backend Developer + QA

---

## 🎯 Следующие шаги

1. **Анализ и планирование** (1 день)

   - Детальный анализ текущего кода
   - Оценка сложности миграции каждого модуля
   - Создание детального плана миграции

2. **Подготовка инфраструктуры** (1 день)

   - Создание новой структуры папок
   - Настройка базовых конфигураций
   - Подготовка тестового окружения

3. **Пошаговая миграция** (5-7 дней)

   - Миграция модулей по одному
   - Тестирование после каждого модуля
   - Фикс багов и регрессий

4. **Финализация и развертывание** (2-3 дня)
   - Полное тестирование системы
   - Обновление документации
   - Развертывание в production

---

_Техническое задание создано на основе анализа текущей структуры проекта и рекомендаций из репозитория fastapi-best-practices._
