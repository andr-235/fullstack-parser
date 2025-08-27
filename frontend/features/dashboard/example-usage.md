# Пример использования дашборда

## 🚀 Быстрый старт

### 1. Основной дашборд с графиками

```tsx
// app/dashboard/page.tsx
import DashboardPage from '@/features/dashboard/ui/DashboardPage'

export default function DashboardRoute() {
  return <DashboardPage />
}
```

## 🎨 Использование отдельных компонентов

### Виджеты

```tsx
import {
  QuickStatsWidget,
  SystemStatusWidget,
  ParsingProgressWidget,
  RecentActivityWidget,
  QuickActionsWidget,
} from '@/features/dashboard/ui/DashboardWidgets'
import { Users, MessageSquare, Target } from 'lucide-react'

function MyDashboard() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* Карточки с метриками */}
      <QuickStatsWidget
        title="Всего групп"
        value={42}
        change={12}
        changeType="increase"
        icon={Users}
        description="Активных групп"
      />

      <QuickStatsWidget
        title="Комментарии"
        value={1234}
        change={8}
        changeType="increase"
        icon={MessageSquare}
        description="За все время"
      />

      <QuickStatsWidget
        title="Совпадения"
        value={89}
        change={15}
        changeType="increase"
        icon={Target}
        description="Найдено совпадений"
      />

      {/* Статус системы */}
      <SystemStatusWidget
        status="healthy"
        message="Все системы работают нормально"
        lastCheck={new Date().toISOString()}
        uptime="7 дней 14 часов"
      />

      {/* Прогресс парсинга */}
      <ParsingProgressWidget
        currentTask="Парсинг группы 'Crypto News'"
        progress={65}
        totalItems={150}
        processedItems={97}
        estimatedTime="5 минут"
      />

      {/* Последняя активность */}
      <RecentActivityWidget
        activities={[
          {
            id: 1,
            type: 'parse',
            message: 'Завершен парсинг группы "Bitcoin Club"',
            timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
            status: 'success',
          },
          {
            id: 2,
            type: 'comment',
            message: 'Найдено 23 новых комментария с ключевыми словами',
            timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
            status: 'success',
          },
        ]}
      />

      {/* Быстрые действия */}
      <QuickActionsWidget />
    </div>
  )
}
```

### Фильтры

```tsx
import {
  DashboardFilters,
  useDashboardFilters,
} from '@/features/dashboard/ui/DashboardFilters'

function MyFilteredDashboard() {
  const { filters, setFilters, resetFilters } = useDashboardFilters()

  const groups = [
    { id: 1, name: 'Crypto News' },
    { id: 2, name: 'Bitcoin Club' },
    { id: 3, name: 'NFT World' },
  ]

  const keywords = [
    { id: 1, word: 'Криптовалюта' },
    { id: 2, word: 'Биткоин' },
    { id: 3, word: 'NFT' },
  ]

  return (
    <div className="space-y-6">
      <DashboardFilters
        filters={filters}
        onFiltersChange={setFilters}
        onReset={resetFilters}
        groups={groups}
        keywords={keywords}
      />

      {/* Отфильтрованный контент */}
      <div>{/* Ваш контент здесь */}</div>
    </div>
  )
}
```

### Экспорт

```tsx
import {
  DashboardExport,
  useDashboardExport,
} from '@/features/dashboard/ui/DashboardExport'

function MyExportableDashboard() {
  const { isExporting, handleExport } = useDashboardExport()

  return (
    <div className="space-y-6">
      <DashboardExport onExport={handleExport} isExporting={isExporting} />

      {/* Остальной контент дашборда */}
    </div>
  )
}
```

## 📊 Интеграция с API

### Использование хуков данных

```tsx
import { useDashboardData } from '@/features/dashboard/hooks/use-dashboard-data'

function MyDataDrivenDashboard() {
  const { data, isLoading, error, refetch } = useDashboardData()

  if (isLoading) {
    return <div>Загрузка...</div>
  }

  if (error) {
    return <div>Ошибка: {error.message}</div>
  }

  return (
    <div className="space-y-6">
      {/* Основные метрики */}
      <div className="grid gap-4 md:grid-cols-4">
        <QuickStatsWidget
          title="Всего групп"
          value={data.globalStats?.total_groups || 0}
          change={12}
          changeType="increase"
          icon={Users}
          description="Активных групп"
        />

        <QuickStatsWidget
          title="Комментарии"
          value={data.globalStats?.total_comments || 0}
          change={8}
          changeType="increase"
          icon={MessageSquare}
          description="За все время"
        />

        <QuickStatsWidget
          title="Ключевые слова"
          value={data.globalStats?.total_keywords || 0}
          change={5}
          changeType="increase"
          icon={Target}
          description="Активных слов"
        />

        <QuickStatsWidget
          title="Совпадения"
          value={data.globalStats?.comments_with_keywords || 0}
          change={15}
          changeType="increase"
          icon={Target}
          description="Найдено совпадений"
        />
      </div>

      {/* Топ групп */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Топ групп</CardTitle>
          </CardHeader>
          <CardContent>
            {data.topGroups?.items?.slice(0, 5).map((group, index) => (
              <div key={group.id} className="flex justify-between p-2">
                <span>
                  {index + 1}. {group.name}
                </span>
                <span>{group.total_comments_found} комментариев</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Топ ключевых слов */}
        <Card>
          <CardHeader>
            <CardTitle>Топ ключевых слов</CardTitle>
          </CardHeader>
          <CardContent>
            {data.topKeywords?.items?.slice(0, 5).map((keyword, index) => (
              <div key={keyword.id} className="flex justify-between p-2">
                <span>
                  {index + 1}. {keyword.word}
                </span>
                <span>{keyword.total_matches} совпадений</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Последние комментарии */}
      <Card>
        <CardHeader>
          <CardTitle>Последние комментарии</CardTitle>
        </CardHeader>
        <CardContent>
          {data.recentComments?.items?.slice(0, 5).map((comment) => (
            <div key={comment.id} className="p-3 border-b last:border-b-0">
              <div className="flex justify-between mb-2">
                <span className="font-medium">{comment.author_name}</span>
                <span className="text-sm text-gray-500">
                  {new Date(comment.published_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-sm">{comment.text}</p>
              <div className="flex gap-2 mt-2">
                <Badge variant="outline">
                  {comment.matched_keywords_count} совпадений
                </Badge>
                {comment.likes_count > 0 && (
                  <Badge variant="secondary">❤️ {comment.likes_count}</Badge>
                )}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
```

## 🎯 Кастомизация

### Создание собственного виджета

```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

interface CustomWidgetProps {
  title: string
  data: any[]
  icon: React.ComponentType<{ className?: string }>
}

export function CustomWidget({ title, data, icon: Icon }: CustomWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {data.map((item, index) => (
            <div
              key={index}
              className="flex justify-between items-center p-2 bg-gray-50 rounded"
            >
              <span>{item.name}</span>
              <Badge variant="secondary">{item.value}</Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
```

### Настройка тем

```tsx
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        dashboard: {
          primary: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          purple: '#8B5CF6',
        },
      },
    },
  },
}
```

## 🔧 Конфигурация

### Настройка API endpoints

```tsx
// lib/api.ts
export const api = {
  // Существующие методы...

  // Новые методы для дашборда
  getActivityData: async (params: { timeRange: string }) => {
    const response = await fetch(`/api/activity?timeRange=${params.timeRange}`)
    return response.json()
  },

  getTopGroups: async (params: { limit: number }) => {
    const response = await fetch(
      `/api/groups?limit=${params.limit}&sort=comments`
    )
    return response.json()
  },

  getTopKeywords: async (params: { limit: number }) => {
    const response = await fetch(
      `/api/keywords?limit=${params.limit}&sort=matches`
    )
    return response.json()
  },
}
```

### Настройка кэширования

```tsx
// hooks/use-dashboard-data.ts
export function useDashboardData() {
  const queryClient = useQueryClient()

  // Настройка кэширования
  const staleTime = 5 * 60 * 1000 // 5 минут
  const refetchInterval = 60 * 1000 // 1 минута

  // Ваши хуки...

  return {
    data,
    isLoading,
    error,
    refetch: () => {
      queryClient.invalidateQueries(['dashboard'])
    },
  }
}
```

## 📱 Адаптивность

### Мобильная версия

```tsx
function ResponsiveDashboard() {
  return (
    <div className="space-y-4 md:space-y-6">
      {/* На мобильных - одна колонка */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Метрики */}
      </div>

      {/* На мобильных - вертикальное расположение */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Виджеты */}
      </div>
    </div>
  )
}
```

## 🧪 Тестирование

### Тестирование компонентов

```tsx
// __tests__/DashboardWidgets.test.tsx
import { render, screen } from '@testing-library/react'
import { QuickStatsWidget } from '@/features/dashboard/ui/DashboardWidgets'
import { Users } from 'lucide-react'

describe('QuickStatsWidget', () => {
  it('отображает метрики корректно', () => {
    render(
      <QuickStatsWidget
        title="Группы"
        value={42}
        change={12}
        changeType="increase"
        icon={Users}
        description="Активных групп"
      />
    )

    expect(screen.getByText('Группы')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
    expect(screen.getByText('+12%')).toBeInTheDocument()
  })
})
```

## 🚀 Производительность

### Оптимизация рендеринга

```tsx
import { memo } from 'react'

// Мемоизация виджетов
export const QuickStatsWidget = memo(function QuickStatsWidget(props) {
  // Компонент
})

// Ленивая загрузка
const DashboardExport = lazy(() => import('./DashboardExport'))

function Dashboard() {
  return (
    <Suspense fallback={<div>Загрузка экспорта...</div>}>
      <DashboardExport />
    </Suspense>
  )
}
```

Этот пример демонстрирует полный спектр возможностей дашборда и показывает, как его можно интегрировать в ваше приложение.
