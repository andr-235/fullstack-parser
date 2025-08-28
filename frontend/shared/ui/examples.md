# Примеры использования унифицированных компонентов

## Общие компоненты

### StatsCard и StatsGrid

```tsx
import { StatsCard, StatsGrid } from '@/shared/ui'
import { Users, MessageSquare, Target } from 'lucide-react'

function DashboardStats({ stats }) {
  return (
    <StatsGrid columns="grid-cols-1 md:grid-cols-3">
      <StatsCard
        title="Пользователи"
        value={stats.users}
        icon={Users}
        color="blue"
        trend="+12%"
        trendUp={true}
        description="Активных пользователей"
      />
      <StatsCard
        title="Комментарии"
        value={stats.comments}
        icon={MessageSquare}
        color="green"
        percentage={85}
      />
      <StatsCard
        title="Конверсия"
        value={stats.conversion}
        icon={Target}
        color="purple"
        variant="compact"
      />
    </StatsGrid>
  )
}
```

### MetricCard и MetricsGrid

```tsx
import { MetricCard, MetricsGrid } from '@/shared/ui'

function DashboardMetrics({ data }) {
  return (
    <MetricsGrid>
      <MetricCard
        title="Общий доход"
        value={data.revenue}
        icon={DollarSign}
        trend="+15%"
        trendUp={true}
        description="За последний месяц"
        gradient
      >
        <LineChart data={data.chartData} />
      </MetricCard>
    </MetricsGrid>
  )
}
```

### ChartCard и ChartsGrid

```tsx
import { ChartCard, ChartsGrid } from '@/shared/ui'

function AnalyticsCharts({ data }) {
  return (
    <ChartsGrid>
      <ChartCard
        title="Продажи по месяцам"
        icon={BarChart}
        trend={{ value: '+23%', direction: 'up' }}
        period="12 месяцев"
        actions={[{ label: 'Экспорт', onClick: handleExport, icon: Download }]}
      >
        <BarChart data={data.sales} />
      </ChartCard>
    </ChartsGrid>
  )
}
```

### PageHeader

```tsx
import { PageHeader } from '@/shared/ui'

function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Дашборд"
        description="Обзор ключевых метрик"
        icon={BarChart3}
        gradient
        actions={<Button onClick={handleExport}>Экспорт</Button>}
      />

      {/* Содержимое страницы */}
    </>
  )
}
```

### Состояния загрузки и пустоты

```tsx
import { LoadingState, EmptyState, ErrorState } from '@/shared/ui'

function DataComponent({ data, isLoading, error, onRetry }) {
  if (isLoading) {
    return <LoadingState message="Загрузка данных..." />
  }

  if (error) {
    return (
      <ErrorState
        title="Ошибка загрузки"
        message={error.message}
        onRetry={onRetry}
        fullScreen
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="Нет данных"
        description="Данные еще не загружены"
        action={{
          label: 'Загрузить',
          onClick: onRetry,
        }}
      />
    )
  }

  return <div>{/* Отображение данных */}</div>
}
```

### ErrorCard

```tsx
import { ErrorCard, ErrorsGrid } from '@/shared/ui'

function ErrorHandler({ errors }) {
  return (
    <ErrorsGrid>
      {errors.map((error, index) => (
        <ErrorCard
          key={index}
          title="Ошибка обработки"
          message={error.message}
          code={error.code}
          details={error.stack}
          actions={[
            { label: 'Повторить', onClick: () => retry(error.id) },
            { label: 'Пропустить', onClick: () => skip(error.id) },
          ]}
        />
      ))}
    </ErrorsGrid>
  )
}
```

### SearchInput

```tsx
import { SearchInput, useSearch } from '@/shared/ui'

function SearchPage() {
  const { query, setQuery, clearSearch, isSearching } = useSearch('', 500)

  return (
    <div>
      <SearchInput
        value={query}
        onChange={setQuery}
        placeholder="Поиск товаров..."
        isLoading={isSearching}
        showClearButton
        onSearch={(value) => console.log('Поиск:', value)}
      />

      {/* Результаты поиска */}
    </div>
  )
}
```

### DataTable

```tsx
import { DataTable } from '@/shared/ui'

const columns = [
  {
    key: 'name',
    title: 'Название',
    sortable: true,
    render: (value, record) => <div className="font-medium">{value}</div>,
  },
  {
    key: 'price',
    title: 'Цена',
    sortable: true,
    align: 'right',
    render: (value) => `${value} ₽`,
  },
  {
    key: 'status',
    title: 'Статус',
    render: (value) => (
      <Badge variant={value === 'active' ? 'success' : 'error'}>{value}</Badge>
    ),
  },
]

function ProductsTable({ products, loading }) {
  return (
    <DataTable
      data={products}
      columns={columns}
      loading={loading}
      rowSelection={{
        selectedRowKeys: [],
        onChange: (keys, rows) => console.log(keys, rows),
      }}
      sortConfig={{
        key: 'name',
        direction: 'asc',
        onSort: (key, direction) => console.log(key, direction),
      }}
      pagination={{
        current: 1,
        pageSize: 10,
        total: 100,
        onChange: (page, size) => console.log(page, size),
      }}
    />
  )
}
```

## Цветовые константы

```tsx
import { StatsCard, StatsGrid } from '@/shared/ui'
import { Users, MessageSquare, Target } from 'lucide-react'

function DashboardStats({ stats }) {
  return (
    <StatsGrid columns="grid-cols-1 md:grid-cols-3">
      <StatsCard
        title="Пользователи"
        value={stats.users}
        icon={Users}
        color="blue"
        trend="+12%"
        trendUp={true}
        description="Активных пользователей"
      />
      <StatsCard
        title="Комментарии"
        value={stats.comments}
        icon={MessageSquare}
        color="green"
        percentage={85}
      />
      <StatsCard
        title="Конверсия"
        value={stats.conversion}
        icon={Target}
        color="purple"
        variant="compact"
      />
    </StatsGrid>
  )
}
```

## Состояния загрузки и пустоты

```tsx
import { LoadingState, EmptyState, ErrorState } from '@/shared/ui'

function DataComponent({ data, isLoading, error, onRetry }) {
  if (isLoading) {
    return <LoadingState message="Загрузка данных..." />
  }

  if (error) {
    return (
      <ErrorState
        title="Ошибка загрузки"
        message={error.message}
        onRetry={onRetry}
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="Нет данных"
        description="Данные еще не загружены"
        action={{
          label: 'Загрузить',
          onClick: onRetry,
        }}
      />
    )
  }

  return <div>{/* Отображение данных */}</div>
}
```

## PageHeader

```tsx
import { PageHeader } from '@/shared/ui'
import { BarChart3 } from 'lucide-react'

function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Дашборд"
        description="Обзор ключевых метрик"
        icon={BarChart3}
        badge={{ text: 'Бета', variant: 'secondary' }}
        actions={<Button onClick={handleExport}>Экспорт</Button>}
        gradient={true}
      />

      {/* Содержимое страницы */}
    </>
  )
}
```

## Цветовые константы

```tsx
import { CHART_COLORS, getChartColor } from '@/shared/constants'

// Использование цветовых констант
const colors = CHART_COLORS.slice(0, 3) // ['#3B82F6', '#10B981', '#F59E0B']

// Или получение цвета по индексу
const color = getChartColor(0) // '#3B82F6'
```

## Форматирование чисел

```tsx
import { useNumberFormat, usePercentFormat } from '@/shared/hooks'

function FormattedStats({ value, percentage }) {
  const formattedValue = useNumberFormat(value, { compact: true })
  const formattedPercent = usePercentFormat(percentage / 100)

  return (
    <div>
      <div>Значение: {formattedValue}</div>
      <div>Процент: {formattedPercent}</div>
    </div>
  )
}
```

## Цветовые схемы графиков

```tsx
import { useChartColors } from '@/shared/hooks'

function ChartComponent({ dataCount }) {
  const colors = useChartColors(dataCount)

  return (
    <div>
      {data.map((item, index) => (
        <div key={item.id} style={{ backgroundColor: colors[index] }}>
          {item.name}
        </div>
      ))}
    </div>
  )
}
```

## Хуки для унификации

### useSearch - управление поиском с debounce

```tsx
import { useSearch } from '@/shared/ui'

function SearchComponent() {
  const { query, setQuery, clearSearch, isSearching } = useSearch('', 300)

  return (
    <SearchInput
      value={query}
      onChange={setQuery}
      placeholder="Поиск товаров..."
      isLoading={isSearching}
      showClearButton
    />
  )
}
```

### useFilters - управление фильтрами

```tsx
import { useFilters } from '@/shared/ui'

function FilterComponent() {
  const { filters, updateFilter, resetFilters, hasActiveFilters } = useFilters({
    status: 'all',
    search: '',
    dateRange: null,
  })

  return (
    <div>
      <SearchInput
        value={filters.search}
        onChange={(value) => updateFilter('search', value)}
        placeholder="Поиск..."
      />

      <Select
        value={filters.status}
        onValueChange={(value) => updateFilter('status', value)}
      >
        <SelectTrigger>
          <SelectValue placeholder="Все статусы" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Все статусы</SelectItem>
          <SelectItem value="active">Активные</SelectItem>
          <SelectItem value="inactive">Неактивные</SelectItem>
        </SelectContent>
      </Select>

      {hasActiveFilters && (
        <Button onClick={resetFilters} variant="outline">
          Сбросить фильтры
        </Button>
      )}
    </div>
  )
}
```

## PageContainer - единый контейнер для страниц

### Базовое использование

```tsx
import { PageContainer } from '@/shared/ui'

export default function MyPage() {
  return (
    <PageContainer>
      <div className="space-y-6">
        <h1>Заголовок страницы</h1>
        <p>Содержимое страницы</p>
      </div>
    </PageContainer>
  )
}
```

### С кастомными настройками

```tsx
<PageContainer
  maxWidth="xl"
  padding="lg"
  background="gradient"
  className="custom-page"
>
  <div className="space-y-6">{/* Содержимое страницы */}</div>
</PageContainer>
```

### Оптимизированные настройки для десктопа

```tsx
// Автоматические настройки по умолчанию для десктопа
<PageContainer>
  {/* Контент автоматически оптимизирован для десктопа */}
</PageContainer>

// Полная ширина экрана (используется на всех основных страницах)
<PageContainer maxWidth="full" background="gradient">
  {/* Контент занимает всю ширину экрана */}
</PageContainer>

// Или с кастомными настройками для больших экранов
<PageContainer
  maxWidth="6xl"  // Еще шире для больших экранов
  padding="xl"     // Больше отступов
  background="default"
>
  {/* Контент для широких десктопных экранов */}
</PageContainer>
```

### Компактный контейнер

```tsx
import { CompactContainer } from '@/shared/ui'

function LoginForm() {
  return (
    <CompactContainer size="sm" background="muted">
      <form>{/* Форма входа */}</form>
    </CompactContainer>
  )
}
```

### Обновление существующей страницы

```tsx
// ДО обновления
export default function MyPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Моя страница" />
      {/* остальной контент */}
    </div>
  )
}

// ПОСЛЕ обновления
import { PageContainer } from '@/shared/ui'

export default function MyPage() {
  return (
    <PageContainer background="gradient">
      <PageHeader title="Моя страница" />
      {/* остальной контент */}
    </PageContainer>
  )
}
```

### Параметры PageContainer

- `maxWidth`: `'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl' | 'full'` (по умолчанию: '4xl' для десктопа)
- `padding`: `'none' | 'sm' | 'md' | 'lg' | 'xl'` (по умолчанию: 'lg' для десктопа)
- `centered`: `boolean` - центрирование контента по вертикали
- `background`: `'default' | 'muted' | 'gradient'`
- `className`: дополнительные CSS классы

### Параметры CompactContainer

- `size`: `'sm' | 'md' | 'lg'` (по умолчанию: 'md')
- `padding`: `'none' | 'sm' | 'md' | 'lg' | 'xl'` (по умолчанию: 'sm')
- `background`: `'default' | 'muted' | 'gradient'`
- `className`: дополнительные CSS классы

## Новые унифицированные компоненты

### ActivityList

Компонент для отображения списка активности с унифицированными иконками и цветами.

```tsx
import { ActivityList, type ActivityItem } from '@/shared/ui'

const activities: ActivityItem[] = [
  {
    id: '1',
    type: 'parse',
    message: 'Парсинг завершен успешно',
    timestamp: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    type: 'comment',
    message: 'Найдено 5 новых комментариев',
    timestamp: '2024-01-15T09:45:00Z'
  }
]

<ActivityList activities={activities} maxItems={5} />
```

**Пропсы:**

- `activities: ActivityItem[]` - массив элементов активности
- `maxItems?: number` - максимальное количество элементов (по умолчанию 5)
- `className?: string` - дополнительные CSS классы

### TimeStats

Компонент для отображения статистики по времени с возможностью подсветки важных значений.

```tsx
import { TimeStats, type TimeStatsItem } from '@/shared/ui'

const timeStats: TimeStatsItem[] = [
  {
    label: "Сегодня",
    value: 123,
    description: "комментариев"
  },
  {
    label: "Совпадения сегодня",
    value: 45,
    description: "найдено",
    highlight: true
  }
]

<TimeStats
  title="Статистика за сегодня"
  items={timeStats}
  columns={2}
/>
```

**Пропсы:**

- `title: string` - заголовок секции
- `items: TimeStatsItem[]` - массив элементов статистики
- `columns?: 1 | 2 | 3 | 4` - количество колонок (по умолчанию 2)
- `className?: string` - дополнительные CSS классы

## Преимущества унификации

✅ **Единообразие** - Все компоненты выглядят согласованно
✅ **Поддерживаемость** - Изменения в одном месте отражаются везде
✅ **Быстрая разработка** - Готовые компоненты для типичных задач
✅ **Темы** - Все компоненты автоматически поддерживают темную/светлую тему
✅ **Доступность** - Унифицированные компоненты имеют правильные ARIA-атрибуты
✅ **Типизация** - Строгая типизация для всех компонентов

## Следующие шаги

✅ **Завершено:**

1. **Рефакторинг DashboardPage** - Полностью унифицирован с PageContainer (full width)
2. **Создание унифицированных компонентов** - DataTable, SearchInput, FilterPanel, StatsCard, ActivityList, TimeStats, etc.
3. **Унификация цветовых схем** - Все компоненты используют CSS переменные для темной/светлой темы
4. **Создание ErrorCard** - Единообразная обработка ошибок
5. **Создание PageContainer** - Единый контейнер для всех страниц с оптимизированными настройками для десктопа
6. **Применение PageContainer к ВСЕМ страницам** - Dashboard, Keywords, Comments, Groups, Settings (maxWidth="full")
7. **Создание ActivityList** - Унифицированный компонент для отображения активности
8. **Создание TimeStats** - Унифицированный компонент для статистики по времени
9. **Полная замена хардкодных цветов** - Все графики и компоненты используют CSS переменные тем

🔄 **В процессе:**

🚀 **Рекомендуется:**

1. **Создание Storybook** - Для демонстрации компонентов
2. **Тестирование** - Интеграционные тесты для унифицированных страниц
3. **Документация API** - Детальное описание всех компонентов
4. **Создание новых унифицированных компонентов** - Для специфических нужд проекта
5. **Оптимизация производительности** - Ленивая загрузка и виртуализация для больших списков
