# Базовая структура проекта

## Корень репозитория

- **backend/** — серверная часть на FastAPI (Python 3.11+)
- **frontend/** — клиентская часть на Next.js 14 (TypeScript)
- **nginx/** — конфигурация обратного прокси и SSL
- **scripts/** — скрипты для деплоя, бэкапа, обслуживания
- **environments/** — конфигурации для production и staging
- **monitoring/** — настройки мониторинга (Prometheus, алерты)
- **docker-compose.yml, docker-compose.prod.yml, docker-compose.prod.ip.yml** — описания сервисов для разработки и продакшена
- **env.example** — пример переменных окружения
- **memory-bank/** — файлы для AI-ассистента и документации

---

## Backend (`backend/`)

- **app/** — основной код приложения
  - **api/** — реализация REST API
    - **v1/** — версия API, содержит:
      - `api.py` — главный роутер API
      - `comments.py`, `groups.py`, `keywords.py`, `parser.py`, `stats.py` — обработчики соответствующих сущностей
      - `endpoints/` — вспомогательные эндпоинты (`health.py`, `info.py`)
      - `router.py` — агрегирующий роутер
      - `health.py` — эндпоинты проверки состояния
  - **core/** — инфраструктурные модули
    - `config.py` — конфигурация приложения (Pydantic)
    - `database.py` — подключение к БД (SQLAlchemy)
    - `security.py` — JWT, OAuth2, авторизация
    - `hashing.py` — хеширование паролей
    - `logging.py` — структурированное логирование (structlog)
  - **middleware/** — промежуточные обработчики (например, логирование запросов)
  - **models/** — SQLAlchemy-модели данных
    - `base.py` — базовая модель
    - `user.py`, `vk_group.py`, `vk_post.py`, `vk_comment.py`, `keyword.py`, `comment_keyword_match.py` — основные сущности
  - **schemas/** — Pydantic-схемы для валидации и сериализации
    - `base.py` — базовые миксины и схемы
    - `user.py`, `vk_group.py`, `vk_comment.py`, `keyword.py`, `parser.py`, `stats.py`, `health.py` — схемы для API
  - **services/** — бизнес-логика и интеграции
    - `base.py` — базовый CRUD-сервис
    - `group_service.py`, `parser_service.py`, `user_service.py`, `vkbottle_service.py`, `redis_parser_manager.py`, `arq_enqueue.py` — сервисы для работы с группами, парсером, пользователями, VK API, очередями задач
  - **workers/** — фоновые задачи (Arq)
    - `arq_worker.py`, `arq_tasks.py`, `tasks.py` — обработка фоновых задач парсинга
  - `main.py` — точка входа FastAPI-приложения
- **alembic/** — миграции базы данных (Alembic)
- **migrations/** — дополнительные миграции
- **Dockerfile** — сборка backend-контейнера
- **pyproject.toml** — зависимости и настройки Poetry
- **requirements.txt** — экспорт зависимостей для Docker

---

## Frontend (`frontend/`)

- **app/** — страницы и layout (Next.js App Router)
  - `layout.tsx` — корневой layout
  - `page.tsx` — главная страница
  - `dashboard/`, `groups/`, `keywords/`, `comments/`, `parser/` — основные разделы
- **components/** — переиспользуемые компоненты
  - **layout/** — компоненты layout (header, sidebar)
  - **ui/** — UI-компоненты (кнопки, таблицы, формы и др.)
- **hooks/** — кастомные React-хуки для работы с API и состоянием
- **lib/** — вспомогательные функции и утилиты
- **providers/** — провайдеры контекста (например, React Query)
- **store/** — Zustand store для глобального состояния
- **types/** — типы API и данных
- **Dockerfile** — сборка frontend-контейнера
- **package.json** — зависимости и скрипты
- **tailwind.config.js** — настройки TailwindCSS
- **next.config.js** — конфигурация Next.js
- **tsconfig.json** — настройки TypeScript

---

## Инфраструктура и DevOps

- **nginx/** — конфигурация обратного прокси и SSL (production/staging)
- **scripts/** — bash-скрипты для деплоя, бэкапа, обслуживания
  - `deploy.sh`, `deploy-production.sh`, `deploy-staging.sh`, `deploy-ip.sh` — деплой
  - `backup.sh` — резервное копирование БД
  - `create-ssl-certs.sh` — генерация SSL-сертификатов
  - `maintenance/` — регулярное обслуживание (cleanup, health-check)
- **environments/** — переменные окружения и docker-compose для разных окружений
- **monitoring/** — конфигурация мониторинга (Prometheus, алерты)
- **docker-compose.yml** — локальная разработка
- **docker-compose.prod.yml**, **docker-compose.prod.ip.yml** — продакшен и продакшен по IP
- **env.example** — шаблон переменных окружения

---

## Memory Bank (`memory-bank/`)

- **tasks.md** — активные задачи и чек-листы
- **activeContext.md** — текущий контекст задачи
- **progress.md** — статус выполнения
- **projectbrief.md** — краткое описание проекта
- **productContext.md** — продуктовый контекст
- **systemPatterns.md** — архитектурные паттерны
- **techContext.md** — технический контекст
- **style-guide.md** — гайд по стилю
- **creative/** — документы креативной фазы (по фичам)
- **reflection/** — рефлексии по задачам
- **archive/** — архив завершённых задач

---

## Прочее

- **README.md** — основная документация
- **docs/** — дополнительные руководства и инструкции
- **pull_request_template.md** — шаблон PR

---

Документ отражает только ключевые директории и файлы, необходимые для понимания архитектуры и поддержки проекта. Для деталей по тестам, примерам и второстепенным файлам см. соответствующие разделы в исходном коде и документации. 