# FSD (Feature-Sliced Design) Architecture Guide

## Структура проекта

```
frontend/
├── app/                    # Next.js App Router (Pages)
│   ├── (auth)/            # Route Groups
│   ├── api/               # API Routes
│   └── globals.css        # Global Styles
├── shared/                 # Переиспользуемые модули
│   ├── ui/                # UI компоненты (Radix UI + Tailwind)
│   ├── hooks/             # Переиспользуемые хуки
│   ├── types/             # Общие типы
│   ├── store/             # Глобальное состояние (Zustand)
│   ├── lib/               # Утилиты и API
│   ├── config/            # Конфигурация
│   └── constants/         # Константы
├── entities/              # Бизнес-сущности
│   ├── comment/
│   ├── group/
│   ├── keyword/
│   ├── post/
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
- Запрещены циклические зависимости

### 2. Структура слайса

Каждый слайс должен содержать:

```
slice/
├── ui/           # React компоненты
├── hooks/        # React хуки
├── types/        # TypeScript типы
├── model/        # Бизнес-логика (опционально)
├── api/          # API интеграции (опционально)
├── store/        # Локальное состояние (опционально)
└── index.ts      # Публичный API
```

### 3. Экспорты

- Все публичные экспорты через `index.ts`
- Приватные модули не экспортируются
- Именованные экспорты предпочтительнее default
- Использовать barrel exports

### 4. Импорты

```typescript
// ✅ Правильно
import { Button } from '@/shared/ui'
import { useComments } from '@/entities/comment'
import { CommentsPage } from '@/widgets/comments-page'

// ❌ Неправильно
import { CommentsPage } from '@/features/comments/ui/CommentsPage'
```

## Next.js 15 + React 19 Особенности

### 1. Server Components

```typescript
// ✅ Server Component
export default async function CommentsPage() {
  const comments = await getComments()
  return <CommentsList comments={comments} />
}

// ✅ Client Component
'use client'
export default function CommentsList({ comments }: Props) {
  return <div>{/* JSX */}</div>
}
```

### 2. App Router Patterns

```typescript
// Route Groups
app/
├── (auth)/
│   ├── login/
│   └── register/
├── (dashboard)/
│   ├── dashboard/
│   └── settings/
└── api/
```

### 3. Server Actions

```typescript
// ✅ В features
export async function createComment(formData: FormData) {
  'use server'
  // Логика создания комментария
}
```

### 4. Streaming и Suspense

```typescript
// ✅ Использование Suspense
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div>
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardStats />
      </Suspense>
    </div>
  )
}
```

## Рекомендации

### 1. Размер компонентов

- Максимум 200-300 строк в одном файле
- Разбивать большие компоненты на подкомпоненты
- Использовать composition pattern

### 2. Типизация

- Использовать строгую типизацию
- Избегать `any`
- Экспортировать типы через `types/`
- Использовать Zod для валидации

### 3. Тестирование

- Тесты рядом с кодом
- Использовать `__tests__` папки
- Тестировать публичный API
- Использовать MSW для API моков

### 4. Производительность

- Использовать React.memo для оптимизации
- Ленивая загрузка компонентов
- Оптимизация изображений с next/image
- Использование React Query для кеширования

### 5. Безопасность

- Валидация данных на сервере
- Использование CSRF токенов
- Санитизация пользовательского ввода
- Безопасные заголовки

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

### 5. Смешивание Server/Client

```typescript
// ❌ Неправильно - использование 'use client' в Server Component
export default async function Page() {
  'use client' // ❌
  const data = await fetchData()
  return <div>{data}</div>
}
```

## Миграция

При рефакторинге:

1. Создать новый слайс
2. Перенести код
3. Обновить импорты
4. Удалить старый код
5. Обновить тесты
6. Проверить типы

## Инструменты

### 1. ESLint Rules

```json
{
  "rules": {
    "import/no-restricted-paths": [
      "error",
      {
        "zones": [
          {
            "target": "./app",
            "from": "./features"
          }
        ]
      }
    ]
  }
}
```

### 2. TypeScript Path Mapping

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"],
      "@/shared/*": ["./shared/*"],
      "@/entities/*": ["./entities/*"],
      "@/features/*": ["./features/*"],
      "@/widgets/*": ["./widgets/*"]
    }
  }
}
```

### 3. Barrel Exports

```typescript
// shared/ui/index.ts
export { Button } from './Button'
export { Input } from './Input'
export { Modal } from './Modal'
```

## Мониторинг и Аналитика

### 1. Bundle Analyzer

```bash
pnpm add -D @next/bundle-analyzer
```

### 2. Performance Monitoring

```typescript
// shared/lib/analytics.ts
export const trackEvent = (event: string, data?: Record<string, any>) => {
  // Аналитика
}
```

### 3. Error Boundaries

```typescript
// shared/ui/ErrorBoundary.tsx
'use client'
export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  // Обработка ошибок
}
```
