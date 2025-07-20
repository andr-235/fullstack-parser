'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useGlobalStats, useDashboardStats } from '@/hooks/use-stats'
import { useDashboardData } from '../hooks/use-dashboard-data'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import type { KeywordResponse, VKGroupResponse } from '@/types/api'
import {
  Users,
  MessageSquare,
  KeyRound,
  Activity,
  TrendingUp,
  Clock,
  Target,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  BarChart3,
  Calendar,
  Filter,
  Download,
  Eye,
  Search,
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

/**
 * Основная страница дашборда с современным дизайном и визуализациями
 */
export default function DashboardPage() {
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
  const { data: dashboardData } = useDashboardData()

  // Данные для графиков активности
  const activityData = dashboardData?.activityData || []

  // Данные для круговой диаграммы ключевых слов
  const keywordData =
    dashboardData?.topKeywords?.map(
      (keyword: KeywordResponse, index: number) => ({
        name: keyword.word,
        value: keyword.total_matches,
        color: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][
          index % 5
        ],
      })
    ) || []

  // Данные для производительности групп
  const groupPerformanceData =
    dashboardData?.topGroups?.map((group: VKGroupResponse) => ({
      name: group.name,
      posts: group.total_posts_parsed,
      comments: group.total_comments_found,
      matches: group.total_comments_found, // Используем общее количество комментариев как приближение
    })) || []

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-500 flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Ошибка загрузки
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600 mb-4">
              Не удалось загрузить данные дашборда. Попробуйте обновить
              страницу.
            </p>
            <Button onClick={() => window.location.reload()} className="w-full">
              <RefreshCw className="h-4 w-4 mr-2" />
              Обновить
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Заголовок и быстрые действия */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Дашборд</h1>
          <p className="text-slate-600 mt-1">
            Обзор активности парсера VK и ключевых метрик
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Экспорт
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Фильтры
          </Button>
          <Button size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </Button>
        </div>
      </div>

      {/* Основные метрики */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Всего групп"
          value={globalStats?.total_groups || 0}
          icon={Users}
          trend="+12%"
          trendUp={true}
          description="Активных групп"
        />
        <MetricCard
          title="Комментарии"
          value={globalStats?.total_comments || 0}
          icon={MessageSquare}
          trend="+8%"
          trendUp={true}
          description="За все время"
        />
        <MetricCard
          title="Ключевые слова"
          value={globalStats?.total_keywords || 0}
          icon={KeyRound}
          trend="+5%"
          trendUp={true}
          description="Активных слов"
        />
        <MetricCard
          title="Совпадения"
          value={globalStats?.comments_with_keywords || 0}
          icon={Target}
          trend="+15%"
          trendUp={true}
          description="Найдено совпадений"
        />
      </div>

      {/* Вкладки с детальной информацией */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="space-y-4"
      >
        <TabsList className="flex w-full overflow-x-auto">
          <TabsTrigger
            value="overview"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3"
          >
            <span className="hidden lg:inline">Обзор</span>
            <span className="hidden sm:inline lg:hidden">Обзор</span>
            <span className="sm:hidden">Обзор</span>
          </TabsTrigger>
          <TabsTrigger
            value="activity"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3"
          >
            <span className="hidden lg:inline">Активность</span>
            <span className="hidden sm:inline lg:hidden">Актив</span>
            <span className="sm:hidden">Актив</span>
          </TabsTrigger>
          <TabsTrigger
            value="groups"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3"
          >
            <span className="hidden lg:inline">Группы</span>
            <span className="hidden sm:inline lg:hidden">Группы</span>
            <span className="sm:hidden">Группы</span>
          </TabsTrigger>
          <TabsTrigger
            value="keywords"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3"
          >
            <span className="hidden lg:inline">Ключевые слова</span>
            <span className="hidden sm:inline lg:hidden">Ключи</span>
            <span className="sm:hidden">Ключи</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* График активности */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Активность за неделю
                  </span>
                  <Badge variant="secondary">+23%</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) =>
                        format(new Date(value), 'dd.MM')
                      }
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) =>
                        format(new Date(value), 'dd MMM yyyy')
                      }
                      formatter={(value, name) => [
                        value,
                        name === 'comments' ? 'Комментарии' : 'Совпадения',
                      ]}
                    />
                    <Area
                      type="monotone"
                      dataKey="comments"
                      stackId="1"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.3}
                    />
                    <Area
                      type="monotone"
                      dataKey="matches"
                      stackId="1"
                      stroke="#10B981"
                      fill="#10B981"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Топ ключевых слов */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <KeyRound className="h-5 w-5" />
                  Топ ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={keywordData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {keywordData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => [
                        `${value} совпадений`,
                        'Количество',
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Последняя активность */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Последняя активность
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardStats?.recent_activity
                  ?.slice(0, 5)
                  .map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-center gap-3 p-3 rounded-lg bg-slate-50"
                    >
                      <div className="flex-shrink-0">
                        {activity.type === 'parse' && (
                          <RefreshCw className="h-4 w-4 text-blue-500" />
                        )}
                        {activity.type === 'comment' && (
                          <MessageSquare className="h-4 w-4 text-green-500" />
                        )}
                        {activity.type === 'group' && (
                          <Users className="h-4 w-4 text-purple-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900">
                          {activity.message}
                        </p>
                        <p className="text-xs text-slate-500">
                          {formatDistanceToNow(new Date(activity.timestamp), {
                            addSuffix: true,
                            locale: ru,
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Детальный график активности */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Динамика комментариев
                  </span>
                  <div className="flex gap-2">
                    {['1d', '7d', '30d'].map((range) => (
                      <Button
                        key={range}
                        variant={timeRange === range ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setTimeRange(range)}
                      >
                        {range}
                      </Button>
                    ))}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) =>
                        format(new Date(value), 'dd.MM')
                      }
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) =>
                        format(new Date(value), 'dd MMM yyyy')
                      }
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="comments"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      name="Комментарии"
                    />
                    <Line
                      type="monotone"
                      dataKey="matches"
                      stroke="#10B981"
                      strokeWidth={2}
                      name="Совпадения"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Статистика по времени */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Статистика по времени
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Сегодня</span>
                    <div className="text-right">
                      <div className="font-semibold">
                        {dashboardStats?.today_comments || 0}
                      </div>
                      <div className="text-xs text-slate-500">комментариев</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">За неделю</span>
                    <div className="text-right">
                      <div className="font-semibold">
                        {dashboardStats?.week_comments || 0}
                      </div>
                      <div className="text-xs text-slate-500">комментариев</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">
                      Совпадения сегодня
                    </span>
                    <div className="text-right">
                      <div className="font-semibold text-green-600">
                        {dashboardStats?.today_matches || 0}
                      </div>
                      <div className="text-xs text-slate-500">найдено</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">
                      Совпадения за неделю
                    </span>
                    <div className="text-right">
                      <div className="font-semibold text-green-600">
                        {dashboardStats?.week_matches || 0}
                      </div>
                      <div className="text-xs text-slate-500">найдено</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Производительность групп
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={groupPerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="posts" fill="#3B82F6" name="Посты" />
                  <Bar dataKey="comments" fill="#10B981" name="Комментарии" />
                  <Bar dataKey="matches" fill="#F59E0B" name="Совпадения" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="keywords" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <KeyRound className="h-5 w-5" />
                  Распределение ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={keywordData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {keywordData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Топ ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {keywordData.map((keyword: any, index: number) => (
                    <div
                      key={keyword.name}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-50"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: keyword.color }}
                        />
                        <span className="font-medium">{keyword.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{keyword.value}</div>
                        <div className="text-xs text-slate-500">совпадений</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

/**
 * Компонент карточки метрики
 */
interface MetricCardProps {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  trend: string
  trendUp: boolean
  description: string
}

function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
  description,
}: MetricCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-slate-400" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        <div className="flex items-center gap-2 mt-1">
          <Badge
            variant={trendUp ? 'default' : 'destructive'}
            className="text-xs"
          >
            {trend}
          </Badge>
          <p className="text-xs text-slate-500">{description}</p>
        </div>
      </CardContent>
    </Card>
  )
}
