# FSD (Feature-Sliced Design) Architecture Guide

## Структура проекта

```
frontend/
├── app/                    # Next.js App Router (Pages)
├── shared/                 # Переиспользуемые модули
│   ├── ui/                # UI компоненты
│   ├── hooks/             # Переиспользуемые хуки
│   ├── types/             # Общие типы
│   ├── store/             # Глобальное состояние
│   └── lib/               # Утилиты и API
├── entities/              # Бизнес-сущности
│   ├── comment/
│   ├── group/
│   ├── keyword/
│   └── user/
├── features/              # Функциональные модули
│   ├── comments/
│   ├── dashboard/
│   ├── groups/
│   ├── keywords/
│   ├── monitoring/
│   ├── parser/
│   └── settings/
├── widgets/               # Композитные блоки
│   ├── comments-page/
│   ├── dashboard-page/
│   ├── layout/
│   └── comments-table/
└── providers/             # Провайдеры (React Context)
```

## Правила FSD

### 1. Иерархия слоев

- `shared` → `entities` → `features` → `widgets` → `app`
- Каждый слой может импортировать только нижележащие слои

### 2. Структура слайса

Каждый слайс должен содержать:

```
slice/
├── ui/           # React компоненты
├── hooks/        # React хуки
├── types/        # TypeScript типы
├── model/        # Бизнес-логика (опционально)
└── index.ts      # Публичный API
```

### 3. Экспорты

- Все публичные экспорты через `index.ts`
- Приватные модули не экспортируются
- Именованные экспорты предпочтительнее default

### 4. Импорты

```typescript
// ✅ Правильно
import { Button } from '@/shared/ui'
import { useComments } from '@/entities/comment'
import { CommentsPage } from '@/widgets/comments-page'

// ❌ Неправильно
import { CommentsPage } from '@/features/comments/ui/CommentsPage'
```

## Рекомендации

### 1. Размер компонентов

- Максимум 200-300 строк в одном файле
- Разбивать большие компоненты на подкомпоненты

### 2. Типизация

- Использовать строгую типизацию
- Избегать `any`
- Экспортировать типы через `types/`

### 3. Тестирование

- Тесты рядом с кодом
- Использовать `__tests__` папки
- Тестировать публичный API

### 4. Документация

- README для каждого слайса
- JSDoc для публичных функций
- Примеры использования

## Антипаттерны

### 1. Нарушение слоев

```typescript
// ❌ Неправильно - импорт из features в app
import { CommentsPage } from '@/features/comments/ui/CommentsPage'
```

### 2. Большие файлы

```typescript
// ❌ Неправильно - файл на 800+ строк
// features/comments/ui/CommentsPage.tsx
```

### 3. Циклические зависимости

```typescript
// ❌ Неправильно - циклический импорт
// entities/comment/hooks.ts → entities/group/hooks.ts → entities/comment/hooks.ts
```

### 4. Прямые импорты

```typescript
// ❌ Неправильно - прямой импорт внутренних модулей
import { CommentModel } from '@/entities/comment/model/CommentModel'
```

## Миграция

При рефакторинге:

1. Создать новый слайс
2. Перенести код
3. Обновить импорты
4. Удалить старый код
5. Обновить тесты
