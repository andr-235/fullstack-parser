# Frontend - VK Parser

Frontend приложение для парсинга комментариев ВКонтакте, построенное на основе Feature-Sliced Design (FSD) архитектуры.

## Архитектура FSD

Проект следует принципам Feature-Sliced Design с четким разделением на слои:

### 📁 Структура проекта

```
frontend/
├── app/                    # App layer - инициализация приложения
│   ├── layout.tsx         # Корневой layout
│   ├── providers.tsx      # Провайдеры приложения
│   └── globals.css        # Глобальные стили
├── pages/                 # Pages layer - страницы приложения
│   └── index.ts           # Экспорты страниц
├── widgets/               # Widgets layer - композитные блоки
│   ├── comments-table/    # Виджет таблицы комментариев
│   └── index.ts           # Экспорты виджетов
├── features/              # Features layer - функциональные модули
│   ├── comments/          # Управление комментариями
│   ├── groups/            # Управление группами
│   ├── keywords/          # Управление ключевыми словами
│   ├── monitoring/        # Мониторинг групп
│   ├── parser/            # Парсинг данных
│   ├── dashboard/         # Дашборд
│   └── settings/          # Настройки
├── entities/              # Entities layer - бизнес-сущности
│   ├── comment/           # Сущность комментария
│   ├── group/             # Сущность группы
│   ├── keyword/           # Сущность ключевого слова
│   └── index.ts           # Экспорты сущностей
├── shared/                # Shared layer - переиспользуемый код
│   ├── ui/                # UI компоненты
│   ├── hooks/             # Переиспользуемые хуки
│   ├── types/             # Общие типы
│   └── store/             # Глобальное состояние
├── processes/             # Processes layer - бизнес-процессы
│   ├── comment-processing.ts
│   └── index.ts
└── lib/                   # Внешние библиотеки и утилиты
    ├── api.ts             # API клиент
    └── utils.ts           # Утилиты
```

### 🔄 Правила импортов

Слои могут импортировать только слои ниже себя:

```
app → pages → widgets → features → entities → shared
```

**✅ Правильно:**

```typescript
// features может импортировать entities и shared
import { useComments } from '@/entities/comment'
import { Button } from '@/shared/ui'

// entities может импортировать только shared
import { formatDate } from '@/shared/utils'
```

**❌ Неправильно:**

```typescript
// Нарушение FSD - features импортирует features
import { useGroups } from '@/features/groups/hooks/use-groups'

// Нарушение FSD - entities импортирует features
import { useDashboard } from '@/features/dashboard'
```

### 🏗️ Структура слоев

#### **App Layer** (`app/`)

- Инициализация приложения
- Провайдеры (React Query, Toast, etc.)
- Глобальные стили и конфигурация

#### **Pages Layer** (`pages/`)

- Страницы приложения
- Композиция виджетов и фич
- Роутинг

#### **Widgets Layer** (`widgets/`)

- Композитные UI блоки
- Объединение нескольких фич
- Переиспользуемые виджеты

#### **Features Layer** (`features/`)

- Функциональные модули
- UI компоненты фич
- Хуки для работы с данными
- Типы фич

#### **Entities Layer** (`entities/`)

- Бизнес-сущности
- Модели данных
- Хуки для работы с сущностями
- Типы сущностей

#### **Shared Layer** (`shared/`)

- Переиспользуемый код
- UI компоненты
- Утилиты
- Хуки
- Типы

#### **Processes Layer** (`processes/`)

- Бизнес-процессы
- Сложная логика
- Оркестрация фич

### 🎯 Принципы FSD

1. **Слоистая архитектура** - четкое разделение ответственности
2. **Правила импортов** - только вниз по слоям
3. **Изоляция фич** - фичи не зависят друг от друга
4. **Переиспользование** - shared слой для общего кода
5. **Модели данных** - entities содержат бизнес-логику

### 🚀 Разработка

#### Добавление новой фичи:

```bash
# Создание структуры фичи
mkdir -p features/new-feature/{ui,hooks,types}
touch features/new-feature/index.ts
```

#### Добавление нового UI компонента:

```bash
# В shared/ui для переиспользуемых компонентов
touch shared/ui/new-component.tsx
# Обновить shared/ui/index.ts
```

#### Добавление новой сущности:

```bash
# Создание структуры сущности
mkdir -p entities/new-entity/{model,hooks,types}
touch entities/new-entity/index.ts
```

### 📦 Технологии

- **Next.js 14** - React фреймворк
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **React Query** - управление состоянием
- **Lucide React** - иконки
- **Date-fns** - работа с датами

### 🔧 Команды

```bash
# Установка зависимостей
pnpm install

# Запуск в режиме разработки
pnpm dev

# Сборка для продакшена
pnpm build

# Запуск тестов
pnpm test

# Линтинг
pnpm lint

# Форматирование кода
pnpm format
```

### 📋 Checklist для FSD

- [x] Правильная структура слоев
- [x] Корректные импорты между слоями
- [x] Модели в entities
- [x] UI компоненты в shared/ui
- [x] Изоляция фич
- [x] Переиспользуемые виджеты
- [x] Бизнес-процессы в processes
- [x] Провайдеры в app слое
