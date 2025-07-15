# Naming Conventions

Документ описывает стандарты именования для всех ключевых сущностей проекта (backend и frontend).

---

## 1. Файлы и директории

- **Python (backend):**
  - snake_case для файлов и директорий.
  - Пример: `user_service.py`, `vk_group.py`, `core/database.py`
- **TypeScript/JS (frontend):**
  - camelCase или kebab-case для файлов, PascalCase для компонентов.
  - Пример: `use-comments.ts`, `app-store.ts`, `Button.tsx`, `layout/sidebar.tsx`

---

## 2. Переменные

- **Python:**
  - snake_case
  - Пример: `user_id`, `is_active`, `db_session`
- **TypeScript/JS:**
  - camelCase
  - Пример: `userId`, `isActive`, `refreshInterval`

---

## 3. Функции и методы

- **Python:**
  - snake_case
  - Пример: `get_user_by_id()`, `create_group()`, `parse_comments()`
- **TypeScript/JS:**
  - camelCase
  - Пример: `fetchGroups()`, `handleSubmit()`, `useDebounce()`

---

## 4. Классы

- **Python:**
  - PascalCase
  - Пример: `UserService`, `VKGroup`, `BaseModel`
- **TypeScript/JS:**
  - PascalCase
  - Пример: `AppStore`, `VKGroupResponse`, `BaseEntity`

---

## 5. React-компоненты (frontend)

- PascalCase для всех компонентов.
- Пример: `Button`, `CardHeader`, `Sidebar`, `DashboardPage`

---

## 6. Интерфейсы и типы (TypeScript)

- PascalCase
- Пример: `UserResponse`, `KeywordUpdate`, `AppSettings`, `BaseEntity`

---

## 7. Enum

- **Python:**
  - PascalCase для класса, UPPER_CASE для значений.
  - Пример: `class UserRole(Enum): ADMIN = 'admin'`
- **TypeScript:**
  - PascalCase для enum, UPPER_CASE для значений.
  - Пример: `enum UserRole { ADMIN = 'admin', USER = 'user' }`

---

## 8. Константы

- **Python:**
  - UPPER_CASE
  - Пример: `DEFAULT_TIMEOUT = 30`
- **TypeScript/JS:**
  - UPPER_CASE
  - Пример: `DEFAULT_PAGE_SIZE = 20`

---

## 9. Прочее

- **Pydantic-схемы (backend):**
  - PascalCase, с суффиксом по назначению: `UserBase`, `UserCreate`, `UserUpdate`, `UserRead`
- **Hooks (frontend):**
  - camelCase с префиксом `use`: `useGroups`, `useParserState`, `useDebounce`
- **Props (frontend):**
  - PascalCase: `ButtonProps`, `CardProps`

---

Документ отражает только основные правила именования. Для новых сущностей придерживайтесь аналогичных паттернов для единообразия кода. 