# Architectural Patterns

Документ описывает основные архитектурные паттерны, применяемые в проекте (backend и frontend), с пояснением их назначения и областей применения.

---

## 1. Слои и разделение ответственности

- **Backend:**
  - Четкая слоистая архитектура: API (FastAPI), сервисы, схемы (Pydantic), модели (SQLAlchemy), инфраструктура (core).
  - Каждый слой отвечает только за свою зону ответственности.
- **Frontend:**
  - Разделение на UI-компоненты, страницы, хуки, глобальное состояние, утилиты.
  - Используется App Router (Next.js 14) для маршрутизации и layout.

---

## 2. Data Access Layer (ORM/Repository)

- **Паттерн:** ORM-модели (SQLAlchemy 2.0)
- **Где:** backend/app/models/
- **Когда использовать:** Для описания структуры данных, связей, бизнес-атрибутов. Все операции с БД идут через модели.

---

## 3. Сервисный слой (Service Layer)

- **Паттерн:** BaseService (generic CRUD), специализированные сервисы
- **Где:** backend/app/services/
- **Когда использовать:** Для инкапсуляции бизнес-логики, работы с моделями, интеграций (VK API, Redis, очереди). Сервисы не зависят от FastAPI и могут использоваться отдельно.

---

## 4. Схемы валидации и сериализации (DTO/Schema Pattern)

- **Паттерн:** Pydantic-схемы с разделением по назначению (Base, Create, Update, Read)
- **Где:** backend/app/schemas/
- **Когда использовать:** Для валидации входных/выходных данных API, разделения схем для разных операций (создание, обновление, чтение).

---

## 5. API Layer (Controller/Router)

- **Паттерн:** FastAPI routers, endpoint-файлы по сущностям
- **Где:** backend/app/api/v1/
- **Когда использовать:** Для организации REST API, маршрутизации запросов, делегирования в сервисы.

---

## 6. Middleware и инфраструктурные паттерны

- **Паттерн:** Middleware для логирования, CORS, безопасности
- **Где:** backend/app/middleware/, backend/app/core/
- **Когда использовать:** Для кросс-срезовых задач: логирование (structlog), обработка ошибок, CORS, JWT, конфигурация.

---

## 7. Миграции и управление схемой БД

- **Паттерн:** Alembic migrations
- **Где:** backend/alembic/
- **Когда использовать:** Для версионирования и миграций структуры БД.

---

## 8. Очереди и фоновые задачи

- **Паттерн:** Arq worker (async task queue)
- **Где:** backend/app/workers/
- **Когда использовать:** Для асинхронных задач (парсинг, интеграции), не блокирующих основной поток API.

---

## 9. UI-компоненты и композиция (Frontend)

- **Паттерн:** Переиспользуемые UI-компоненты (Button, Card, Table и др.)
- **Где:** frontend/components/ui/
- **Когда использовать:** Для построения интерфейса из атомарных и составных компонентов, соблюдения единого стиля.

---

## 10. State Management (Frontend)

- **Паттерн:** Zustand store для глобального состояния
- **Где:** frontend/store/
- **Когда использовать:** Для хранения и управления состоянием приложения (настройки, фильтры, выборки, UI-состояние).

---

## 11. Data Fetching и кэширование (Frontend)

- **Паттерн:** React Query hooks
- **Где:** frontend/hooks/
- **Когда использовать:** Для работы с API, кэширования, автоматического обновления данных, управления загрузкой/ошибками.

---

## 12. Провайдеры и layout (Frontend)

- **Паттерн:** Контекстные провайдеры (ReactQueryProvider), layout-композиция
- **Где:** frontend/app/layout.tsx, frontend/providers/
- **Когда использовать:** Для внедрения глобальных зависимостей (React Query, темы, уведомления), организации структуры страниц.

---

## 13. API-клиент и абстракция доступа к данным (Frontend)

- **Паттерн:** API-клиент (Axios), абстракция методов
- **Где:** frontend/lib/api.ts
- **Когда использовать:** Для централизованного доступа к backend API, обработки ошибок, повторного использования логики.

---

Документ отражает только ключевые паттерны, реально применяемые в проекте. Для новых модулей и фич придерживайтесь аналогичных архитектурных подходов.
