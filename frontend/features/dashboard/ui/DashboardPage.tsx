'use client'

import { useState } from 'react'
import {
  PageHeader,
  StatsCard,
  StatsGrid,
  ChartCard,
  ChartsGrid,
  LoadingState,
  ErrorState,
  ActivityList,
  TimeStats,
  PageContainer,
  Button,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'
import { useGlobalStats, useDashboardStats } from '@/features/dashboard/hooks'
import { useDashboardData } from '@/features/dashboard/hooks/use-dashboard-data'
import type { KeywordResponse, VKGroupResponse } from '@/shared/types'
import {
  Users,
  MessageSquare,
  KeyRound,
  Activity,
  Clock,
  Target,
  RefreshCw,
  BarChart3,
  Calendar,
  Download,
  TrendingUp,
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  LineChart as RechartsLineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [timeRange, setTimeRange] = useState('7d')

  const {
    data: globalStats,
    isLoading: globalLoading,
    error: globalError,
  } = useGlobalStats()
  const {
    data: dashboardStats,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useDashboardStats()

  const isLoading = globalLoading || dashboardLoading
  const error = globalError || dashboardError

  // Используем реальные данные из API
  const dashboardData = useDashboardData()

  // Данные для графиков активности
  const activityData = Array.isArray(dashboardData.activityData?.data?.recent_activity)
    ? dashboardData.activityData?.data?.recent_activity || []
    : []

  // Данные для круговой диаграммы ключевых слов
  const keywordData =
    Array.isArray(dashboardData.topKeywords?.data)
      ? dashboardData.topKeywords.data.map(
        (keyword: KeywordResponse, index: number) => ({
          name: keyword.word || 'Без названия',
          value: keyword.total_matches || 0,
          color: ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))'][
            index % 5
          ],
        })
      )
      : []

  // Данные для производительности групп
  const groupPerformanceData =
    Array.isArray(dashboardData.topGroups?.data)
      ? dashboardData.topGroups.data.map((group: VKGroupResponse) => ({
        name: group.name || 'Без названия',
        posts: group.total_posts_parsed || 0,
        comments: group.total_comments_found || 0,
        matches: group.total_comments_found || 0,
      }))
      : []

  if (isLoading) {
    return <LoadingState message="Загрузка дашборда..." />
  }

  if (error) {
    return (
      <ErrorState
        title="Ошибка загрузки дашборда"
        message="Не удалось загрузить данные дашборда. Попробуйте обновить страницу."
        onRetry={() => window.location.reload()}
        retryLabel="Обновить страницу"
      />
    )
  }

  return (
    <PageContainer maxWidth="full" background="gradient">
      {/* Заголовок */}
      <PageHeader
        title="Дашборд"
        description="Обзор активности парсера VK и ключевых метрик"
        icon={BarChart3}
        actions={
          <Button variant="secondary" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Экспорт
          </Button>
        }
      />

      {/* Основные метрики */}
      <StatsGrid
        stats={[
          {
            title: "Всего групп",
            value: globalStats?.total_groups || 0,
            icon: Users,
            color: "blue"
          },
          {
            title: "Комментарии",
            value: globalStats?.total_comments || 0,
            icon: MessageSquare,
            color: "green"
          },
          {
            title: "Ключевые слова",
            value: globalStats?.total_keywords || 0,
            icon: KeyRound,
            color: "purple"
          },
          {
            title: "Совпадения",
            value: globalStats?.comments_with_keywords || 0,
            icon: Target,
            color: "orange"
          }
        ]}
      />

      {/* Вкладки с детальной информацией */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Обзор</TabsTrigger>
          <TabsTrigger value="activity">Активность</TabsTrigger>
          <TabsTrigger value="groups">Группы</TabsTrigger>
          <TabsTrigger value="keywords">Ключевые слова</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <ChartsGrid>
            {/* График активности */}
            <ChartCard
              title="Активность за неделю"
              description="Комментарии и совпадения по дням"
              icon={Activity}
              trend={{ value: '+23%', direction: 'up' }}
              period="7 дней"
            >
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => {
                      try {
                        const date = new Date(value)
                        return isNaN(date.getTime()) ? '' : format(date, 'dd.MM')
                      } catch {
                        return ''
                      }
                    }}
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))',
                    }}
                    labelFormatter={(value) => {
                      try {
                        const date = new Date(value)
                        return isNaN(date.getTime()) ? '' : format(date, 'dd MMM yyyy')
                      } catch {
                        return ''
                      }
                    }}
                    formatter={(value, name) => [
                      value,
                      name === 'comments' ? 'Комментарии' : 'Совпадения',
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="comments"
                    stackId="1"
                    stroke="hsl(var(--chart-1))"
                    fill="hsl(var(--chart-1))"
                    fillOpacity={0.3}
                  />
                  <Area
                    type="monotone"
                    dataKey="matches"
                    stackId="1"
                    stroke="hsl(var(--chart-2))"
                    fill="hsl(var(--chart-2))"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Топ ключевых слов */}
            <ChartCard
              title="Топ ключевых слов"
              description="Распределение по частоте совпадений"
              icon={KeyRound}
            >
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={keywordData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name || 'Без названия'} ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="hsl(var(--chart-1))"
                    dataKey="value"
                  >
                    {keywordData.map((entry, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    )).slice(0, 5)}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))',
                    }}
                    formatter={(value) => [
                      `${value} совпадений`,
                      'Количество',
                    ]}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </ChartCard>
          </ChartsGrid>

          {/* Последняя активность */}
          <ChartCard
            title="Последняя активность"
            description="Недавние события в системе"
            icon={Clock}
            height={300}
          >
            <ActivityList
              activities={Array.isArray(dashboardStats?.recent_activity)
                ? dashboardStats?.recent_activity?.map(activity => ({
                  ...activity,
                  id: String(activity.id)
                })) || []
                : []
              }
              maxItems={5}
            />
          </ChartCard>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <ChartsGrid>
            {/* Детальный график активности */}
            <ChartCard
              title="Динамика комментариев"
              description="Детальный анализ активности за выбранный период"
              icon={TrendingUp}
              period={timeRange}
              actions={['1d', '7d', '30d'].map((range) => ({
                label: range,
                onClick: () => setTimeRange(range),
                variant: timeRange === range ? 'default' : 'outline' as const,
              }))}
            >
              <ResponsiveContainer width="100%" height={300}>
                <RechartsLineChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => {
                      try {
                        const date = new Date(value)
                        return isNaN(date.getTime()) ? '' : format(date, 'dd.MM')
                      } catch {
                        return ''
                      }
                    }}
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))',
                    }}
                    labelFormatter={(value) => {
                      try {
                        const date = new Date(value)
                        return isNaN(date.getTime()) ? '' : format(date, 'dd MMM yyyy')
                      } catch {
                        return ''
                      }
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="comments"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    name="Комментарии"
                  />
                  <Line
                    type="monotone"
                    dataKey="matches"
                    stroke="hsl(var(--chart-2))"
                    strokeWidth={2}
                    name="Совпадения"
                  />
                </RechartsLineChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Статистика по времени */}
            <ChartCard
              title="Статистика по времени"
              description="Анализ активности за разные периоды"
              icon={Calendar}
              height={300}
            >
              <TimeStats
                title=""
                items={[
                  {
                    label: "Сегодня",
                    value: dashboardStats?.today_comments || 0,
                    description: "комментариев"
                  },
                  {
                    label: "За неделю",
                    value: dashboardStats?.week_comments || 0,
                    description: "комментариев"
                  },
                  {
                    label: "Совпадения сегодня",
                    value: dashboardStats?.today_matches || 0,
                    description: "найдено",
                    highlight: true
                  },
                  {
                    label: "Совпадения за неделю",
                    value: dashboardStats?.week_matches || 0,
                    description: "найдено",
                    highlight: true
                  }
                ]}
                columns={2}
              />
            </ChartCard>
          </ChartsGrid>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          <ChartCard
            title="Производительность групп"
            description="Сравнение активности по группам"
            icon={BarChart3}
            height={400}
          >
            <ResponsiveContainer width="100%" height={400}>
              <RechartsBarChart data={groupPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis tick={{ fill: 'hsl(var(--muted-foreground))' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                    color: 'hsl(var(--foreground))',
                  }}
                />
                <Legend />
                <Bar dataKey="posts" fill="hsl(var(--primary))" name="Посты" />
                <Bar dataKey="comments" fill="hsl(var(--chart-2))" name="Комментарии" />
                <Bar dataKey="matches" fill="hsl(var(--chart-3))" name="Совпадения" />
              </RechartsBarChart>
            </ResponsiveContainer>
          </ChartCard>
        </TabsContent>

        <TabsContent value="keywords" className="space-y-4">
          <ChartsGrid>
            <ChartCard
              title="Распределение ключевых слов"
              description="Круговая диаграмма распределения по частоте"
              icon={KeyRound}
            >
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={keywordData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="hsl(var(--chart-1))"
                    dataKey="value"
                  >
                    {keywordData.map((entry, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    )).slice(0, 5)}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--background))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      color: 'hsl(var(--foreground))',
                    }}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard
              title="Топ ключевых слов"
              description="Список наиболее частых совпадений"
              icon={Target}
            >
              <div className="space-y-3">
                {keywordData.length > 0 ? (
                  keywordData.slice(0, 5).map((keyword, index: number) => (
                    <div
                      key={keyword.name}
                      className="flex items-center justify-between p-3 rounded-lg bg-card border animate-fade-in-up"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: keyword.color }}
                        />
                        <span className="font-medium">
                          {keyword.name}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">
                          {keyword.value}
                        </div>
                        <div className="text-xs text-muted-foreground">совпадений</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-center py-8 text-muted-foreground">
                    Нет данных о ключевых словах
                  </div>
                )}
              </div>
            </ChartCard>
          </ChartsGrid>
        </TabsContent>
      </Tabs>
    </PageContainer>
  )
}
