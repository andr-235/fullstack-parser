# 🎛️ Settings Feature

Модуль настроек предоставляет централизованное управление конфигурацией приложения через веб-интерфейс.

## 📁 Структура

```
frontend/features/settings/
├── ui/
│   ├── SettingsTabs.tsx          # Основной компонент с табами
│   ├── SettingsHeader.tsx        # Заголовок страницы
│   ├── SettingsHealthWidget.tsx  # Виджет здоровья системы
│   ├── VKAPISettingsTab.tsx      # Настройки VK API
│   ├── MonitoringSettingsTab.tsx # Настройки мониторинга
│   ├── DatabaseSettingsTab.tsx   # Настройки базы данных
│   ├── LoggingSettingsTab.tsx    # Настройки логирования
│   └── UISettingsTab.tsx         # Настройки интерфейса
└── README.md                     # Эта документация
```

## 🎯 Функциональность

### VK API Settings

- **Access Token** - токен доступа к API ВКонтакте (с маскировкой)
- **API Version** - версия API (рекомендуется 5.131)
- **Requests per Second** - лимит запросов (1-20)
- **Test Connection** - проверка подключения к VK API

### Monitoring Settings

- **Scheduler Interval** - интервал планировщика (60-3600 сек)
- **Max Concurrent Groups** - максимум групп одновременно (1-50)
- **Group Delay** - задержка между группами (0-10 сек)
- **Auto Start Scheduler** - автозапуск планировщика

### Database Settings

- **Pool Size** - размер пула соединений (5-50)
- **Max Overflow** - максимальное переполнение (10-100)
- **Pool Recycle** - пересоздание соединений (300-7200 сек)

### Logging Settings

- **Level** - уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Format** - формат логов (JSON, TEXT)
- **Include Timestamp** - включение временных меток

### UI Settings

- **Theme** - тема интерфейса (light, dark, system)
- **Auto Refresh** - автообновление данных
- **Refresh Interval** - интервал обновления (10-300 сек)
- **Items per Page** - элементов на странице (10-100)
- **Show Notifications** - показ уведомлений

## 🔧 Использование

### Основная страница

```tsx
import { SettingsPage } from '@/app/settings/page'

// Страница автоматически загружается с Suspense
export default function App() {
  return <SettingsPage />
}
```

### Отдельные компоненты

```tsx
import { SettingsTabs } from '@/features/settings/ui/SettingsTabs'
import { SettingsHealthWidget } from '@/features/settings/ui/SettingsHealthWidget'

function MyComponent() {
  return (
    <div>
      <SettingsTabs />
      <SettingsHealthWidget />
    </div>
  )
}
```

## 🎨 UI Components

### SettingsTabs

Основной компонент с табами для различных разделов настроек.

**Props:** Нет

**Features:**

- Автоматическое переключение между табами
- Сохранение состояния активного таба
- Responsive дизайн

### SettingsHeader

Заголовок страницы с описанием и иконками.

**Props:** Нет

**Features:**

- Иконки для каждого раздела настроек
- Описание функциональности
- Информативные подсказки

### SettingsHealthWidget

Виджет для отображения состояния системы.

**Props:** Нет

**Features:**

- Real-time статус компонентов
- Автообновление каждую минуту
- Цветовая индикация состояния
- Время последней проверки

### VKAPISettingsTab

Таб для настройки параметров VK API.

**Props:** Нет

**Features:**

- Маскировка Access Token
- Валидация в реальном времени
- Тест подключения к VK API
- Информативные подсказки

### MonitoringSettingsTab

Таб для настройки автоматического мониторинга.

**Props:** Нет

**Features:**

- Валидация интервалов
- Переключатели для boolean настроек
- Описания параметров
- Предупреждения о лимитах

### DatabaseSettingsTab

Таб для настройки параметров базы данных.

**Props:** Нет

**Features:**

- Валидация пула соединений
- Оптимизация производительности
- Описания параметров

### LoggingSettingsTab

Таб для настройки системы логирования.

**Props:** Нет

**Features:**

- Выбор уровня логирования
- Выбор формата логов
- Переключатели для опций

### UISettingsTab

Таб для настройки пользовательского интерфейса.

**Props:** Нет

**Features:**

- Выбор темы
- Настройка автообновления
- Конфигурация пагинации
- Управление уведомлениями

## 🔄 State Management

### React Query Hooks

```tsx
import {
  useSettings,
  useUpdateSettings,
  useResetSettings,
  useSettingsHealth,
  useTestVKAPIConnection,
} from '@/hooks/use-settings'

function MyComponent() {
  const { data: settings, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()
  const resetSettings = useResetSettings()
  const { data: health } = useSettingsHealth()
  const testConnection = useTestVKAPIConnection()

  // Использование
  const handleSave = async () => {
    await updateSettings.mutateAsync({
      vk_api: { access_token: 'new_token' },
    })
  }
}
```

### Form State

Каждый таб управляет своим состоянием формы:

```tsx
const [formData, setFormData] = useState({
  access_token: '',
  api_version: '5.131',
  requests_per_second: 3,
})

const handleInputChange = (field: string, value: string | number) => {
  setFormData((prev) => ({ ...prev, [field]: value }))
}
```

## ✅ Валидация

### Client-side Validation

```tsx
import { SETTINGS_VALIDATION } from '@/types/settings'

const isTokenValid = formData.access_token.length > 0
const isRequestsValid =
  formData.requests_per_second >=
    SETTINGS_VALIDATION.vk_api.requests_per_second.min &&
  formData.requests_per_second <=
    SETTINGS_VALIDATION.vk_api.requests_per_second.max
```

### Server-side Validation

Все данные валидируются на сервере через Pydantic схемы:

```python
class VKAPISettings(BaseModel):
    access_token: str = Field(..., description="VK Access Token")
    api_version: str = Field(default="5.131", description="Версия VK API")
    requests_per_second: int = Field(default=3, ge=1, le=20, description="Запросов в секунду")
```

## 🎨 Styling

### TailwindCSS Classes

```tsx
// Основные контейнеры
<div className="space-y-6">
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

// Карточки
<Card className="p-6">
<CardHeader>
<CardContent className="space-y-4">

// Формы
<div className="space-y-2">
<Label htmlFor="field">Label</Label>
<Input id="field" />
<p className="text-xs text-slate-500">Description</p>
```

### Dark Mode Support

Все компоненты поддерживают темную тему:

```tsx
className = 'text-slate-900 dark:text-slate-50'
className = 'bg-slate-200 dark:bg-slate-700'
```

## 🔒 Безопасность

### Защита чувствительных данных

- Access Token отображается как password field
- Возможность скрыть/показать токен
- Валидация токена через тест подключения

### Валидация данных

- Client-side валидация для UX
- Server-side валидация для безопасности
- Типизация TypeScript для предотвращения ошибок

## 🚀 Производительность

### Оптимизации

- **React Query кеширование** - 5 минут
- **Suspense** - плавные загрузочные состояния
- **Lazy loading** - компоненты загружаются по требованию
- **Debounced updates** - предотвращение частых API вызовов

### Loading States

```tsx
if (isLoading) {
  return <div>Загрузка настроек...</div>
}
```

## 🧪 Тестирование

### Unit Tests

```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { VKAPISettingsTab } from './VKAPISettingsTab'

test('renders VK API settings form', () => {
  render(<VKAPISettingsTab />)
  expect(screen.getByLabelText(/access token/i)).toBeInTheDocument()
})
```

### Integration Tests

```tsx
import { useSettings } from '@/hooks/use-settings'

test('loads settings from API', async () => {
  const { result } = renderHook(() => useSettings())
  await waitFor(() => {
    expect(result.current.data).toBeDefined()
  })
})
```

## 🔄 Расширяемость

### Добавление нового таба

1. Создать компонент таба в `ui/`
2. Добавить в `SettingsTabs.tsx`
3. Добавить типы в `@/types/settings.ts`
4. Добавить валидацию в `SETTINGS_VALIDATION`

### Пример нового таба

```tsx
// ui/NewSettingsTab.tsx
export function NewSettingsTab() {
  const { data: settingsData, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()

  const [formData, setFormData] = useState({
    new_setting: '',
  })

  const handleSave = async () => {
    await updateSettings.mutateAsync({
      new_section: formData,
    })
  }

  return (
    <div className="space-y-6">
      <h2>Новые настройки</h2>
      {/* Форма */}
    </div>
  )
}
```

## 📚 Дополнительные ресурсы

- [Архитектура системы настроек](../../../docs/SETTINGS_ARCHITECTURE.md)
- [API документация](../../../docs/API.md)
- [TypeScript типы](../../../types/settings.ts)
- [React Query хуки](../../../hooks/use-settings.ts)
