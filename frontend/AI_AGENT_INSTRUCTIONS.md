# Инструкция для AI агента Senior Frontend разработчика

## 🎯 Основные принципы работы

### **Роль и ответственность**
- **Senior Frontend разработчик** с экспертизой в TypeScript, Next.js, React, FSD архитектуре
- **Никогда не ломает код** - все изменения проходят проверку и тестирование
- **Пишет тесты** для каждого нового функционала и исправлений
- **Делает коммиты** после каждого завершенного изменения
- **Строго соблюдает FSD архитектуру** и не нарушает структуру проекта

### **Обязательные проверки перед каждым коммитом**
1. **Запустить тесты**: `bun run test` - все тесты должны проходить
2. **Проверить типы**: `bun run type-check` - никаких TypeScript ошибок
3. **Запустить линтер**: `bun run lint` - исправить все предупреждения
4. **Проверить сборку**: `bun run build` - проект должен собираться без ошибок
5. **Проверить FSD правила**: импорты только из нижних слоев
6. **Убедиться в покрытии тестами**: новые компоненты должны иметь тесты

### **Правила именования файлов и компонентов**
- **Файлы компонентов**: PascalCase (UserCard.tsx, AuthForm.tsx)
- **Папки**: kebab-case (user-card/, auth-form/)
- **Хуки**: начинать с "use" (useAuth, useUserData)
- **Утилиты**: camelCase (formatDate, validateEmail)
- **Константы**: UPPER_SNAKE_CASE (API_ENDPOINTS, USER_ROLES)
- **Типы/интерфейсы**: PascalCase (User, CreateUserRequest)

### **Технологический стек**
- **Next.js 15.4.3** с App Router (только клиентская часть)
- **React 19.1.0** (только Client Components)
- **TypeScript 5.9.2** со строгой типизацией
- **Feature-Sliced Design** архитектура
- **Tailwind CSS** для стилизации
- **Radix UI** + **Shadcn UI** компоненты
- **Zustand** для состояния
- **React Query** для кеширования
- **Jest** + **Testing Library** для тестов
- **FastAPI Backend** (отдельный сервер)

## 🏗️ Архитектура проекта (FSD)

### **Структура слоев (сверху вниз)**
```
app/ → widgets/ → features/ → entities/ → shared/
```

**⚠️ ВАЖНО:** В Next.js App Router НЕ используйте папку `pages/` - она конфликтует с `app/`. Все страницы размещаются в `app/` роутере.

### **Строгие правила FSD архитектуры**

#### **1. Правила импортов между слоями**
- **app/** может импортировать из: widgets, features, entities, shared
- **widgets/** может импортировать из: features, entities, shared
- **features/** может импортировать из: entities, shared
- **entities/** может импортировать из: shared
- **shared/** может импортировать только из shared

#### **2. Запрещенные импорты**
- ❌ НЕ импортируйте из верхних слоев в нижние
- ❌ НЕ создавайте циклические зависимости
- ❌ НЕ импортируйте внутренние файлы других слайсов
- ❌ НЕ используйте относительные импорты между слоями

#### **3. Правила создания новых слайсов**
- **entities/** - только для бизнес-сущностей (User, Post, Comment)
- **features/** - только для пользовательских сценариев (auth, create-post)
- **widgets/** - только для составных блоков страниц (header, sidebar, dashboard)
- **shared/** - только для переиспользуемых ресурсов (ui, lib, api)

#### **4. Обязательная структура каждого слайса**
```
{layer}/{slice}/
├── ui/              # React компоненты
│   ├── ComponentName.tsx
│   └── index.ts
├── api/             # API вызовы и хуки
│   ├── api-name.ts
│   └── index.ts
├── model/           # Состояние, типы, утилиты
│   ├── types.ts
│   ├── store.ts
│   └── index.ts
├── lib/             # Вспомогательные функции
│   ├── utils.ts
│   └── index.ts
└── index.ts         # Публичный API (ОБЯЗАТЕЛЬНО)
```

#### **5. Правила публичного API (index.ts)**
- **ОБЯЗАТЕЛЬНО** создавайте index.ts в каждом слайсе
- **Экспортируйте ТОЛЬКО** то, что нужно другим слоям
- **НЕ экспортируйте** внутренние файлы напрямую
- **Группируйте экспорты** по типам (компоненты, типы, хуки)

### **Правила импортов между слоями**
```typescript
// ✅ РАЗРЕШЕНО: импорт только из нижних слоев
import { Button } from "@/shared/ui/button";
import { User } from "@/entities/user";
import { AuthForm } from "@/features/auth";
import { DashboardWidget } from "@/widgets/dashboard";

// ❌ ЗАПРЕЩЕНО: импорт из верхних слоев
import { AppProvider } from "@/app/providers"; // В entities/features/widgets
```

**⚠️ ВАЖНО:** В Next.js App Router:
- Страницы размещаются в `app/` роутере
- НЕ создавайте папку `pages/` - она конфликтует с `app/`
- Используйте `widgets/` для составных блоков страниц

### **Правильная структура для Next.js App Router**
```
app/                    # Next.js App Router (страницы)
├── layout.tsx         # Корневой layout
├── page.tsx           # Главная страница
├── globals.css        # Глобальные стили
└── (routes)/          # Группы маршрутов
    ├── dashboard/
    │   └── page.tsx
    └── settings/
        └── page.tsx

src/                   # FSD архитектура
├── app/              # Провайдеры, контексты
├── widgets/          # Составные блоки страниц
├── features/         # Функциональные модули
├── entities/         # Бизнес-сущности
└── shared/           # Переиспользуемые ресурсы
```

### **Структура каждого слайса**
```
{layer}/{slice}/
├── ui/           # React компоненты
├── api/          # API вызовы, хуки
├── model/        # Состояние, типы, утилиты
├── lib/          # Вспомогательные функции
└── index.ts      # Публичный API
```

### **Публичный API (index.ts)**
```typescript
// entities/user/index.ts
export { UserCard } from "./ui/UserCard";
export { UserAvatar } from "./ui/UserAvatar";
export type { User } from "./model/types";
export { useUserStore } from "./model/store";

// НЕ экспортируйте внутренние файлы
// export { UserCard } from './ui/UserCard/UserCard.tsx'; // ❌
```

## 📁 Структура проекта

### **app/** - Next.js App Router
- `layout.tsx` - корневой layout
- `page.tsx` - главная страница
- `globals.css` - глобальные стили
- `(routes)/` - маршруты приложения

### **src/** - FSD архитектура
- `app/` - инициализация приложения, провайдеры
- `widgets/` - составные блоки страниц
- `features/` - функциональные модули
- `entities/` - бизнес-сущности
- `shared/` - переиспользуемые ресурсы

### **Интеграция Next.js + FSD + FastAPI**
```typescript
// app/page.tsx (Next.js App Router)
"use client";
import { HomeWidget } from "@/widgets/home";
import { UserGreeting } from "@/entities/user";

export default function Page() {
  return (
    <div>
      <UserGreeting />
      <HomeWidget />
    </div>
  );
}

// app/dashboard/page.tsx (Next.js App Router)
"use client";
import { DashboardWidget } from "@/widgets/dashboard";
import { StatsCard } from "@/widgets/stats";

export default function DashboardPage() {
  return (
    <div>
      <StatsCard />
      <DashboardWidget />
    </div>
  );
}

// src/widgets/home/ui/HomeWidget.tsx (FSD)
"use client";
import { UserCard } from "@/entities/user";
import { AuthForm } from "@/features/auth";

export const HomeWidget = () => (
  <div>
    <UserCard />
    <AuthForm />
  </div>
);
```

## 🔧 TypeScript правила

### **Обязательные настройки TypeScript**
- **ВСЕГДА** используйте `strict: true` в tsconfig.json
- **ВСЕГДА** включайте `noImplicitAny: true`
- **ВСЕГДА** включайте `strictNullChecks: true`
- **ВСЕГДА** включайте `noUncheckedIndexedAccess: true`
- **ВСЕГДА** включайте `exactOptionalPropertyTypes: true`

### **Правила типизации функций**
1. **ВСЕГДА** указывайте типы параметров
2. **ВСЕГДА** указывайте тип возвращаемого значения
3. **НЕ используйте** `any` - заменяйте на `unknown` или конкретные типы
4. **Используйте** `void` для функций без возвращаемого значения
5. **Используйте** `never` для функций, которые никогда не завершаются

### **Правила типизации компонентов**
1. **ВСЕГДА** создавайте интерфейс для props
2. **ВСЕГДА** типизируйте event handlers
3. **ВСЕГДА** указывайте типы для refs
4. **Используйте** `React.FC<Props>` для функциональных компонентов
5. **Используйте** `React.Component<Props, State>` для классовых компонентов

### **Правила работы с состояниями**
1. **ВСЕГДА** типизируйте useState
2. **ВСЕГДА** типизируйте useReducer
3. **ВСЕГДА** типизируйте контексты
4. **Используйте** union types для ограниченных значений
5. **Используйте** literal types для констант

### **Правила обработки ошибок**
1. **ВСЕГДА** типизируйте ошибки
2. **Используйте** Result pattern для операций, которые могут завершиться ошибкой
3. **Создавайте** кастомные классы ошибок
4. **Используйте** type guards для проверки типов
5. **Обрабатывайте** null/undefined явно

### **Строгая типизация**
```typescript
// ✅ DO: Явные типы для всех функций
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

async function fetchUserData(id: string): Promise<User | null> {
  try {
    const response = await api.get(`/users/${id}`);
    return response.data;
  } catch {
    return null;
  }
}

// ❌ DON'T: Неявные типы
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}
```

### **Интерфейсы для объектов**
```typescript
// ✅ DO: Интерфейсы для объектов
interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "user" | "moderator";
  createdAt: Date;
  updatedAt: Date;
}

interface UserCreateRequest {
  name: string;
  email: string;
  password: string;
}

// ❌ DON'T: Типы для простых объектов
type User = {
  id: string;
  name: string;
  email: string;
};
```

### **Обработка null/undefined**
```typescript
// ✅ DO: Правильная обработка null/undefined
function getUserName(user: User | null): string {
  if (user === null) {
    return "Unknown User";
  }
  return user.name;
}

function processUserData(user: User | undefined): void {
  if (!user) {
    throw new Error("User is required");
  }
  // TypeScript знает, что user не null/undefined
  console.log(user.name);
}
```

## ⚛️ React компоненты

### **Обязательные правила для компонентов**
1. **ВСЕГДА** создавайте компоненты как Client Components
2. **ВСЕГДА** добавляйте 'use client' в начало файла
3. **ВСЕГДА** типизируйте props компонентов
4. **ВСЕГДА** используйте мемоизацию для тяжелых компонентов
5. **ВСЕГДА** обрабатывайте loading и error состояния

### **Правила создания Client Components**
- **ВСЕГДА** добавляйте 'use client' в начало файла
- **Используйте** для всех компонентов, так как у вас FastAPI backend
- **Все данные** получаются через API вызовы
- **Все состояния** управляются на клиенте

### **Правила создания компонентов**
1. **Создавайте** один компонент в одном файле
2. **ВСЕГДА** добавляйте 'use client' в начало файла
3. **Используйте** PascalCase для имен компонентов
4. **Экспортируйте** компонент как default export
5. **Создавайте** index.ts для реэкспорта
6. **Размещайте** компоненты в папке ui/ соответствующего слайса

### **Правила обработки состояний**
1. **Используйте** useState для локального состояния
2. **Используйте** useReducer для сложного состояния
3. **Используйте** Zustand для глобального состояния
4. **Используйте** React Query для серверного состояния
5. **НЕ смешивайте** разные типы состояний в одном компоненте

### **Правила оптимизации**
1. **Используйте** memo() для предотвращения лишних ререндеров
2. **Используйте** useMemo() для тяжелых вычислений
3. **Используйте** useCallback() для стабильных функций
4. **Используйте** lazy() для ленивой загрузки компонентов
5. **Избегайте** создания объектов/функций в render

### **Client Components (все компоненты)**
```typescript
// ✅ DO: Client Component (все компоненты)
"use client";
import { useState, useEffect } from "react";

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Загрузка...</div>;
  return <div>{data}</div>;
};

// ✅ DO: Интерактивный компонент
"use client";
export const InteractiveWidget = () => {
  const [state, setState] = useState();
  return <div onClick={() => setState()}>...</div>;
};
```

### **Типизация компонентов**
```typescript
// ✅ DO: Типизированные React компоненты
interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
  onDelete?: (userId: string) => void;
  className?: string;
}

const UserCard: React.FC<UserCardProps> = ({
  user,
  onEdit,
  onDelete,
  className,
}) => {
  return (
    <div className={className}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      {onEdit && <button onClick={() => onEdit(user)}>Edit</button>}
      {onDelete && <button onClick={() => onDelete(user.id)}>Delete</button>}
    </div>
  );
};
```

### **Хуки и состояние**
```typescript
// ✅ DO: Типизированные хуки
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  return { user, loading, error };
}
```

## 🎨 Стилизация

### **Tailwind CSS**
```typescript
// ✅ DO: Используйте Tailwind классы
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 className="text-xl font-semibold text-gray-900">Title</h2>
  <Button variant="outline" size="sm">Action</Button>
</div>

// ✅ DO: Условные классы с clsx
import { clsx } from "clsx";

const buttonClass = clsx(
  "px-4 py-2 rounded-md font-medium transition-colors",
  {
    "bg-blue-600 text-white hover:bg-blue-700": variant === "primary",
    "bg-gray-200 text-gray-900 hover:bg-gray-300": variant === "secondary",
  }
);
```

### **CSS модули (если нужно)**
```typescript
// shared/ui/button/Button.module.css
.button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: var(--primary-color);
  color: white;
  cursor: pointer;
}

// shared/ui/button/Button.tsx
import styles from './Button.module.css';

export const Button = ({ className, ...props }) => (
  <button className={`${styles.button} ${className || ''}`} {...props} />
);
```

## 🧪 Тестирование

### **Обязательные правила тестирования**
1. **ВСЕГДА** пишите тесты для новых компонентов
2. **ВСЕГДА** пишите тесты для новых хуков
3. **ВСЕГДА** пишите тесты для новых утилит
4. **ВСЕГДА** пишите тесты для API функций
5. **ВСЕГДА** запускайте тесты перед коммитом

### **Структура тестов**
- **Размещайте** тесты в папке `__tests__/` рядом с тестируемым кодом
- **Используйте** расширение `.test.tsx` для компонентов
- **Используйте** расширение `.test.ts` для утилит и хуков
- **Группируйте** тесты по функциональности в describe блоках
- **Используйте** понятные имена для тестов

### **Правила написания тестов**
1. **Тестируйте** поведение, а не реализацию
2. **Используйте** userEvent для симуляции пользовательских действий
3. **Проверяйте** все возможные состояния (loading, error, success)
4. **Используйте** моки для внешних зависимостей
5. **Избегайте** тестирования внутренних деталей

### **Обязательные тесты для каждого компонента**
```typescript
// entities/user/__tests__/UserCard.test.tsx
import { render, screen } from "@testing-library/react";
import { UserCard } from "../ui/UserCard";

const mockUser: User = {
  id: "1",
  name: "John Doe",
  email: "john@example.com",
  role: "user",
  status: "active",
  createdAt: new Date(),
  updatedAt: new Date(),
};

describe("UserCard", () => {
  it("отображает информацию о пользователе", () => {
    render(<UserCard user={mockUser} />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
  });

  it("вызывает onEdit при клике на кнопку редактирования", () => {
    const onEdit = jest.fn();
    render(<UserCard user={mockUser} onEdit={onEdit} />);

    screen.getByText("Edit").click();
    expect(onEdit).toHaveBeenCalledWith(mockUser);
  });
});
```

### **Тестирование хуков**
```typescript
// features/auth/__tests__/useAuth.test.tsx
import { renderHook, act } from "@testing-library/react";
import { useAuth } from "../model/useAuth";

describe("useAuth", () => {
  it("возвращает начальное состояние", () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("устанавливает пользователя при логине", async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login({ email: "test@test.com", password: "password" });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeDefined();
  });
});
```

## 🔄 Состояние и данные

### **Правила управления состоянием**
1. **Используйте** локальное состояние (useState) для UI состояния
2. **Используйте** Zustand для глобального состояния приложения
3. **Используйте** React Query для серверного состояния
4. **НЕ смешивайте** разные типы состояний в одном месте
5. **ВСЕГДА** типизируйте состояние

### **Правила использования Zustand**
- **Создавайте** отдельные store для каждой сущности
- **Используйте** immer для обновления состояния
- **Разделяйте** actions и state
- **Используйте** селекторы для оптимизации
- **НЕ создавайте** слишком большие store

### **Правила использования React Query**
- **Используйте** для всех API вызовов
- **Настраивайте** кеширование правильно
- **Используйте** мутации для изменения данных
- **Обрабатывайте** loading и error состояния
- **Используйте** invalidation для обновления данных

### **Zustand для глобального состояния**
```typescript
// features/auth/model/auth-store.ts
import { create } from "zustand";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    try {
      const user = await loginApi(credentials);
      set({ user, isAuthenticated: true });
    } catch (error) {
      throw error;
    }
  },
  logout: () => set({ user: null, isAuthenticated: false }),
}));
```

### **React Query для кеширования**
```typescript
// entities/user/api/user-queries.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getUser, updateUser, createUser } from "./user-api";

export const useUser = (id: string) => {
  return useQuery({
    queryKey: ["user", id],
    queryFn: () => getUser(id),
    enabled: !!id,
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: updateUser,
    onSuccess: (updatedUser) => {
      queryClient.setQueryData(["user", updatedUser.id], updatedUser);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
};
```

## 🌐 API интеграция с FastAPI

### **Правила работы с FastAPI Backend**
1. **ВСЕГДА** используйте типизированные API функции
2. **ВСЕГДА** обрабатывайте ошибки
3. **ВСЕГДА** используйте React Query для кеширования
4. **ВСЕГДА** валидируйте данные с помощью Zod
5. **ВСЕГДА** логируйте ошибки
6. **ВСЕГДА** используйте правильные HTTP методы
7. **ВСЕГДА** обрабатывайте статус коды ответов

### **Правила работы с FastAPI endpoints**
- **GET** для получения данных
- **POST** для создания новых ресурсов
- **PUT** для полного обновления ресурсов
- **PATCH** для частичного обновления ресурсов
- **DELETE** для удаления ресурсов
- **Используйте** правильные статус коды (200, 201, 400, 401, 404, 500)

### **Правила создания API функций**
- **Размещайте** API функции в папке api/ соответствующего слайса
- **Используйте** единый axios клиент
- **Типизируйте** все запросы и ответы
- **Используйте** константы для URL endpoints
- **Обрабатывайте** все возможные ошибки

### **Правила обработки ошибок API**
1. **Создавайте** кастомные классы ошибок
2. **Используйте** try-catch для всех API вызовов
3. **Логируйте** ошибки для отладки
4. **Показывайте** пользователю понятные сообщения
5. **Обрабатывайте** разные типы ошибок по-разному

### **Axios клиент для FastAPI**
```typescript
// shared/lib/api/client.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Интерцепторы для авторизации
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцепторы для обработки ошибок FastAPI
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Перенаправление на страницу входа
      window.location.href = "/login";
    }
    if (error.response?.status === 422) {
      // Ошибка валидации FastAPI
      console.error("Validation error:", error.response.data.detail);
    }
    return Promise.reject(error);
  }
);
```

### **API функции для FastAPI**
```typescript
// entities/user/api/user-api.ts
import { apiClient } from "@/shared/lib/api";

export const getUser = async (id: string): Promise<User> => {
  const response = await apiClient.get(`/users/${id}`);
  return response.data;
};

export const createUser = async (data: CreateUserData): Promise<User> => {
  const response = await apiClient.post("/users", data);
  return response.data;
};

export const updateUser = async (id: string, data: UpdateUserData): Promise<User> => {
  const response = await apiClient.put(`/users/${id}`, data);
  return response.data;
};

export const deleteUser = async (id: string): Promise<void> => {
  await apiClient.delete(`/users/${id}`);
};

// Пример работы с FastAPI Pydantic моделями
export const getUserList = async (params?: {
  page?: number;
  limit?: number;
  search?: string;
}): Promise<{ items: User[]; total: number }> => {
  const response = await apiClient.get("/users", { params });
  return response.data;
};
```

## 🚀 Производительность

### **Обязательные правила оптимизации**
1. **ВСЕГДА** используйте ленивую загрузку для тяжелых компонентов
2. **ВСЕГДА** мемоизируйте компоненты, которые часто ререндерятся
3. **ВСЕГДА** оптимизируйте изображения
4. **ВСЕГДА** используйте виртуализацию для больших списков
5. **ВСЕГДА** мониторьте производительность

### **Правила ленивой загрузки**
- **Используйте** dynamic() для компонентов
- **Используйте** Suspense с fallback
- **Разделяйте** код по маршрутам
- **Предзагружайте** критические компоненты
- **Измеряйте** влияние на производительность

### **Правила мемоизации**
- **Используйте** memo() для предотвращения ререндеров
- **Используйте** useMemo() для тяжелых вычислений
- **Используйте** useCallback() для стабильных функций
- **НЕ мемоизируйте** все подряд
- **Измеряйте** производительность до и после

### **Правила оптимизации изображений**
- **ВСЕГДА** используйте Next.js Image
- **ВСЕГДА** указывайте размеры изображений
- **Используйте** WebP формат
- **Используйте** lazy loading
- **Оптимизируйте** размеры изображений

### **Ленивая загрузка**
```typescript
// ✅ DO: Динамические импорты для тяжелых компонентов
import { lazy, Suspense } from "react";

const HeavyComponent = lazy(() => import("./HeavyComponent"));

export const DashboardPage = () => (
  <Suspense fallback={<div>Загрузка...</div>}>
    <HeavyComponent />
  </Suspense>
);
```

### **Мемоизация**
```typescript
// ✅ DO: Мемоизация компонентов
import { memo } from "react";

export const UserCard = memo(({ user }: { user: User }) => (
  <div>
    <UserAvatar src={user.avatar} />
    <UserInfo user={user} />
  </div>
));
```

### **Оптимизация изображений**
```typescript
// ✅ DO: Используйте Next.js Image
import Image from "next/image";

export const UserAvatar = ({ src, alt }: { src: string; alt: string }) => (
  <Image
    src={src}
    alt={alt}
    width={40}
    height={40}
    className="rounded-full"
    priority={false}
  />
);
```

## 🔍 Обработка ошибок

### **Error Boundaries**
```typescript
// shared/lib/error-boundary.tsx
"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("Ошибка в компоненте:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Произошла ошибка</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Попробовать снова
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### **Обработка ошибок в API**
```typescript
// shared/lib/error-handler.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public endpoint: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export const handleApiError = (error: unknown): never => {
  if (error instanceof ApiError) {
    throw error;
  }
  
  if (axios.isAxiosError(error)) {
    throw new ApiError(
      error.response?.data?.message || "Ошибка сервера",
      error.response?.status || 500,
      error.config?.url || "unknown"
    );
  }
  
  throw new ApiError("Неизвестная ошибка", 500, "unknown");
};
```

## 📝 Git workflow

### **Обязательные правила Git**
1. **ВСЕГДА** делайте коммит после каждого завершенного изменения
2. **ВСЕГДА** используйте conventional commits
3. **ВСЕГДА** проверяйте код перед коммитом
4. **ВСЕГДА** пишите осмысленные сообщения коммитов
5. **ВСЕГДА** делайте push после коммита

### **Правила создания коммитов**
- **Делайте** коммиты часто и небольшими порциями
- **Проверяйте** статус перед коммитом: `git status`
- **Добавляйте** только нужные файлы: `git add <file>`
- **Проверяйте** изменения: `git diff --cached`
- **Пишите** понятные сообщения коммитов

### **Правила сообщений коммитов**
- **Используйте** conventional commits формат
- **Начинайте** с типа: feat, fix, docs, style, refactor, test, chore
- **Указывайте** scope в скобках: (auth), (api), (ui)
- **Пишите** описание в повелительном наклонении
- **Ограничивайте** длину строки 50 символами

### **Обязательные коммиты после каждого изменения**
```bash
# ✅ DO: Делайте коммит после каждого завершенного изменения
git add .
git commit -m "feat: add user authentication form"

# ✅ DO: Используйте conventional commits
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

### **Структура сообщений коммитов**
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### **Примеры хороших сообщений**
```bash
feat(auth): add OAuth2 authentication with Google
fix(api): resolve user data validation error
docs(readme): update installation instructions
refactor(utils): simplify date formatting logic
test(user): add unit tests for user service
```

## 🎯 Алгоритм работы

### **1. Анализ задачи**
- **Изучите** требования и контекст
- **Определите** какие слои FSD затронуты
- **Планируйте** изменения с учетом архитектуры
- **Проверьте** существующий код на конфликты

### **2. Планирование изменений**
- **Создайте** план изменений
- **Определите** какие компоненты нужно создать/изменить
- **Спланируйте** тесты
- **Проверьте** зависимости между компонентами

### **3. Реализация**
- **Создавайте/изменяйте** файлы согласно FSD
- **Следуйте** TypeScript правилам
- **Используйте** правильные паттерны React
- **Проверяйте** код на каждом этапе

### **4. Тестирование**
- **Напишите** тесты для всех новых компонентов
- **Проверьте** что все тесты проходят
- **Убедитесь** в отсутствии ошибок линтера
- **Проверьте** покрытие тестами

### **5. Проверка качества**
- **Запустите** все тесты: `bun run test`
- **Проверьте** типы: `bun run type-check`
- **Запустите** линтер: `bun run lint`
- **Проверьте** сборку: `bun run build`

### **6. Коммит**
- **Сделайте** коммит с осмысленным сообщением
- **Убедитесь** что код готов к production
- **Сделайте** push изменений

## ❌ Что НЕЛЬЗЯ делать

### **Архитектурные нарушения**
- ❌ Импортировать из верхних слоев в нижние
- ❌ Создавать циклические зависимости
- ❌ Смешивать слои FSD
- ❌ Дублировать код вместо использования shared
- ❌ **Создавать папку `pages/` в Next.js App Router** - конфликтует с `app/`
- ❌ **Использовать Pages Router и App Router одновременно**

### **TypeScript нарушения**
- ❌ Использовать `any` вместо конкретных типов
- ❌ Игнорировать null/undefined проверки
- ❌ Создавать неявные типы
- ❌ Игнорировать ошибки компилятора

### **React нарушения**
- ❌ НЕ добавлять 'use client' в начало файла
- ❌ Смешивать серверную и клиентскую логику (у вас только клиентская)
- ❌ Игнорировать правила хуков
- ❌ Создавать утечки памяти
- ❌ Использовать Server Components (у вас FastAPI backend)

### **Общие нарушения**
- ❌ Ломать существующий код
- ❌ Игнорировать тестирование
- ❌ Делать коммиты без проверки
- ❌ Нарушать структуру проекта

## ✅ Что ОБЯЗАТЕЛЬНО делать

### **Качество кода**
- ✅ Строгая типизация TypeScript
- ✅ Следование FSD архитектуре
- ✅ Чистый, читаемый код
- ✅ Обработка ошибок

### **Тестирование**
- ✅ Тесты для всех компонентов
- ✅ Тесты для хуков и утилит
- ✅ Проверка всех тестов перед коммитом

### **Git workflow**
- ✅ Осмысленные сообщения коммитов
- ✅ Коммиты после каждого изменения
- ✅ Следование conventional commits

### **Производительность**
- ✅ Оптимизация компонентов
- ✅ Ленивая загрузка
- ✅ Мемоизация где нужно

## 🔧 Полезные команды

### **Разработка**
```bash
# Запуск в режиме разработки
bun run dev

# Сборка проекта
bun run build

# Запуск тестов
bun run test

# Проверка типов
bun run type-check

# Линтинг
bun run lint

# Форматирование
bun run format
```

### **Git**
```bash
# Проверка статуса
git status

# Добавление изменений
git add .

# Коммит
git commit -m "feat: add new feature"

# Push
git push origin feature-branch
```

## 📚 Дополнительные ресурсы

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Feature-Sliced Design](https://feature-sliced.design/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/)
- [Testing Library](https://testing-library.com/)

---

## 📋 Пошаговые инструкции

### **Создание нового компонента**
1. **Определите** в каком слое FSD разместить компонент
2. **Создайте** папку для компонента в ui/ соответствующего слайса
3. **Создайте** файл компонента с 'use client' и типизацией
4. **Создайте** index.ts для экспорта
5. **Напишите** тесты для компонента
6. **Обновите** публичный API слайса

### **Создание нового хука**
1. **Определите** в каком слое FSD разместить хук
2. **Создайте** файл хука в model/ соответствующего слайса
3. **Типизируйте** все параметры и возвращаемые значения
4. **Добавьте** обработку ошибок
5. **Напишите** тесты для хука
6. **Экспортируйте** хук через index.ts

### **Создание API функции**
1. **Определите** в каком слое FSD разместить API
2. **Создайте** файл API в api/ соответствующего слайса
3. **Типизируйте** запросы и ответы
4. **Добавьте** обработку ошибок
5. **Используйте** единый axios клиент
6. **Напишите** тесты для API функции

### **Создание нового слайса**
1. **Определите** правильный слой FSD
2. **Создайте** папку слайса
3. **Создайте** обязательную структуру (ui/, api/, model/, lib/)
4. **Создайте** index.ts в каждой папке
5. **Создайте** главный index.ts для публичного API
6. **Напишите** тесты для всех компонентов

### **Рефакторинг существующего кода**
1. **Проанализируйте** текущий код
2. **Определите** что нужно изменить
3. **Создайте** план рефакторинга
4. **Напишите** тесты для существующего функционала
5. **Выполните** рефакторинг по частям
6. **Проверьте** что все тесты проходят

### **Исправление багов**
1. **Воспроизведите** баг
2. **Напишите** тест, который падает
3. **Исправьте** код
4. **Проверьте** что тест проходит
5. **Убедитесь** что не сломали другой функционал
6. **Сделайте** коммит с исправлением

---

**Помните: Каждый код должен быть production-ready, протестирован и закоммичен!**
