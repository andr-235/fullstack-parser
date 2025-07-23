# Fullstack Parser Frontend

Современное React приложение для парсинга и мониторинга контента ВКонтакте, построенное на Next.js 15 с React 19 и FSD архитектурой.

## 🚀 Технологии

- **Next.js 15** - React фреймворк с App Router
- **React 19** - Библиотека для создания пользовательских интерфейсов
- **TypeScript** - Типизированный JavaScript
- **Tailwind CSS** - Utility-first CSS фреймворк
- **Radix UI** - Доступные UI примитивы
- **Zustand** - Легковесное управление состоянием
- **React Query** - Кеширование и синхронизация данных
- **Zod** - Валидация схем

## 🏗️ Архитектура FSD

Проект использует Feature-Sliced Design (FSD) архитектуру для масштабируемости и поддерживаемости:

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

### Правила FSD

1. **Иерархия слоев**: `shared` → `entities` → `features` → `widgets` → `app`
2. **Импорты**: Каждый слой может импортировать только нижележащие слои
3. **Экспорты**: Все публичные экспорты через `index.ts`
4. **Структура слайса**: `ui/`, `hooks/`, `types/`, `model/`, `api/`, `store/`

## 🛠️ Установка и запуск

### Требования

- Node.js 18+
- pnpm 8+

### Установка зависимостей

```bash
pnpm install
```

### Разработка

```bash
pnpm dev
```

Приложение будет доступно по адресу [http://localhost:3000](http://localhost:3000)

### Сборка

```bash
pnpm build
```

### Запуск production версии

```bash
pnpm start
```

## 📝 Скрипты

```bash
pnpm dev          # Запуск в режиме разработки
pnpm build        # Сборка для production
pnpm start        # Запуск production версии
pnpm lint         # Проверка кода ESLint
pnpm format       # Форматирование кода Prettier
pnpm type-check   # Проверка типов TypeScript
pnpm test         # Запуск тестов
pnpm test:watch   # Запуск тестов в watch режиме
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### TypeScript

Проект использует строгую типизацию TypeScript с дополнительными правилами:

- `noUncheckedIndexedAccess` - проверка индексов массивов
- `exactOptionalPropertyTypes` - точные типы опциональных свойств
- `noImplicitReturns` - явные возвраты функций

### ESLint

Настроены правила для FSD архитектуры:

- Порядок импортов
- Запрет импортов между слоями
- Строгие правила TypeScript

## 🎨 UI Компоненты

Используются компоненты на основе Radix UI с кастомизацией через Tailwind CSS:

- **Button** - Кнопки с различными вариантами
- **Card** - Карточки для контента
- **Dialog** - Модальные окна
- **Select** - Выпадающие списки
- **Table** - Таблицы с сортировкой
- **Form** - Формы с валидацией

## 📊 Управление состоянием

### Глобальное состояние (Zustand)

```typescript
import { useAppStore } from '@/shared/store'

// Использование
const theme = useAppStore((state) => state.ui.theme)
const setTheme = useAppStore((state) => state.setTheme)
```

### Кеширование данных (React Query)

```typescript
import { useApiQuery } from '@/shared/hooks/useApi'

// Использование
const { data, isLoading, error } = useApiQuery(['comments'], '/api/comments')
```

## 🔒 Безопасность

- Валидация данных с Zod
- Безопасные заголовки HTTP
- Content Security Policy
- Защита от XSS и CSRF

## 📱 Адаптивность

Приложение полностью адаптивно и поддерживает:

- Мобильные устройства
- Планшеты
- Десктопы
- Большие экраны

## 🧪 Тестирование

```bash
# Запуск всех тестов
pnpm test

# Запуск тестов в watch режиме
pnpm test:watch

# Покрытие кода
pnpm test --coverage
```

## 📦 Оптимизация

### Bundle Analysis

```bash
# Анализ размера бандла
pnpm build
npx @next/bundle-analyzer
```

### Performance

- Ленивая загрузка компонентов
- Оптимизация изображений
- Кеширование данных
- Code splitting

## 🚀 Деплой

### Vercel (рекомендуется)

1. Подключите репозиторий к Vercel
2. Настройте переменные окружения
3. Деплой произойдет автоматически

### Docker

```bash
# Сборка образа
docker build -t fullstack-parser-frontend .

# Запуск контейнера
docker run -p 3000:3000 fullstack-parser-frontend
```

## 📚 Документация

- [FSD Architecture Guide](./FSD_GUIDE.md)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License
