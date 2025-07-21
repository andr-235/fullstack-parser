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
  BarChart,
  PieChart,
  LineChart,
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
        <div className="flex flex-col items-center justify-center space-y-4">
          <LoadingSpinner className="h-8 w-8 text-blue-500" />
          <span className="text-slate-400 font-medium">
            Загрузка дашборда...
          </span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Card className="w-96 border-slate-700 bg-slate-800">
          <CardHeader>
            <CardTitle className="text-red-400 flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Ошибка загрузки
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400 mb-4">
              Не удалось загрузить данные дашборда. Попробуйте обновить
              страницу.
            </p>
            <Button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
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
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <BarChart className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold">Дашборд</h1>
        </div>
        <p className="text-slate-300">
          Обзор активности парсера VK и ключевых метрик
        </p>
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
        <TabsList className="flex w-full overflow-x-auto bg-slate-800 border-slate-700">
          <TabsTrigger
            value="overview"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3 data-[state=active]:bg-slate-700 data-[state=active]:text-slate-200"
          >
            <span className="hidden lg:inline">Обзор</span>
            <span className="hidden sm:inline lg:hidden">Обзор</span>
            <span className="sm:hidden">Обзор</span>
          </TabsTrigger>
          <TabsTrigger
            value="activity"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3 data-[state=active]:bg-slate-700 data-[state=active]:text-slate-200"
          >
            <span className="hidden lg:inline">Активность</span>
            <span className="hidden sm:inline lg:hidden">Актив</span>
            <span className="sm:hidden">Актив</span>
          </TabsTrigger>
          <TabsTrigger
            value="groups"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3 data-[state=active]:bg-slate-700 data-[state=active]:text-slate-200"
          >
            <span className="hidden lg:inline">Группы</span>
            <span className="hidden sm:inline lg:hidden">Группы</span>
            <span className="sm:hidden">Группы</span>
          </TabsTrigger>
          <TabsTrigger
            value="keywords"
            className="flex-1 min-w-[80px] whitespace-nowrap px-2 sm:px-3 data-[state=active]:bg-slate-700 data-[state=active]:text-slate-200"
          >
            <span className="hidden lg:inline">Ключевые слова</span>
            <span className="hidden sm:inline lg:hidden">Ключи</span>
            <span className="sm:hidden">Ключи</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* График активности */}
            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-slate-200">
                  <span className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-blue-400" />
                    Активность за неделю
                  </span>
                  <Badge className="bg-green-900 text-green-300 border-green-700">
                    +23%
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) =>
                        format(new Date(value), 'dd.MM')
                      }
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis tick={{ fill: '#9CA3AF' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F9FAFB',
                      }}
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
            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-200">
                  <KeyRound className="h-5 w-5 text-purple-400" />
                  Топ ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
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
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F9FAFB',
                      }}
                      formatter={(value) => [
                        `${value} совпадений`,
                        'Количество',
                      ]}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Последняя активность */}
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-200">
                <Clock className="h-5 w-5 text-orange-400" />
                Последняя активность
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardStats?.recent_activity
                  ?.slice(0, 5)
                  .map((activity, index) => (
                    <div
                      key={activity.id}
                      className="flex items-center gap-3 p-3 rounded-lg bg-slate-700 border border-slate-600 animate-fade-in-up"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <div className="flex-shrink-0">
                        {activity.type === 'parse' && (
                          <RefreshCw className="h-4 w-4 text-blue-400" />
                        )}
                        {activity.type === 'comment' && (
                          <MessageSquare className="h-4 w-4 text-green-400" />
                        )}
                        {activity.type === 'group' && (
                          <Users className="h-4 w-4 text-purple-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-200">
                          {activity.message}
                        </p>
                        <p className="text-xs text-slate-400">
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
            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-slate-200">
                  <span className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-400" />
                    Динамика комментариев
                  </span>
                  <div className="flex gap-2">
                    {['1d', '7d', '30d'].map((range) => (
                      <Button
                        key={range}
                        variant={timeRange === range ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setTimeRange(range)}
                        className={
                          timeRange === range
                            ? 'bg-blue-600 hover:bg-blue-700'
                            : 'border-slate-600 text-slate-300 hover:bg-slate-700'
                        }
                      >
                        {range}
                      </Button>
                    ))}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsLineChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) =>
                        format(new Date(value), 'dd.MM')
                      }
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis tick={{ fill: '#9CA3AF' }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F9FAFB',
                      }}
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
                  </RechartsLineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Статистика по времени */}
            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-200">
                  <Calendar className="h-5 w-5 text-purple-400" />
                  Статистика по времени
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-700 border border-slate-600">
                    <span className="text-sm text-slate-300">Сегодня</span>
                    <div className="text-right">
                      <div className="font-semibold text-slate-200">
                        {dashboardStats?.today_comments || 0}
                      </div>
                      <div className="text-xs text-slate-400">комментариев</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-700 border border-slate-600">
                    <span className="text-sm text-slate-300">За неделю</span>
                    <div className="text-right">
                      <div className="font-semibold text-slate-200">
                        {dashboardStats?.week_comments || 0}
                      </div>
                      <div className="text-xs text-slate-400">комментариев</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-700 border border-slate-600">
                    <span className="text-sm text-slate-300">
                      Совпадения сегодня
                    </span>
                    <div className="text-right">
                      <div className="font-semibold text-green-400">
                        {dashboardStats?.today_matches || 0}
                      </div>
                      <div className="text-xs text-slate-400">найдено</div>
                    </div>
                  </div>
                  <div className="flex justify-between items-center p-3 rounded-lg bg-slate-700 border border-slate-600">
                    <span className="text-sm text-slate-300">
                      Совпадения за неделю
                    </span>
                    <div className="text-right">
                      <div className="font-semibold text-green-400">
                        {dashboardStats?.week_matches || 0}
                      </div>
                      <div className="text-xs text-slate-400">найдено</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-200">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                Производительность групп
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <RechartsBarChart data={groupPerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" tick={{ fill: '#9CA3AF' }} />
                  <YAxis tick={{ fill: '#9CA3AF' }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1F2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#F9FAFB',
                    }}
                  />
                  <Legend />
                  <Bar dataKey="posts" fill="#3B82F6" name="Посты" />
                  <Bar dataKey="comments" fill="#10B981" name="Комментарии" />
                  <Bar dataKey="matches" fill="#F59E0B" name="Совпадения" />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="keywords" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-200">
                  <KeyRound className="h-5 w-5 text-purple-400" />
                  Распределение ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
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
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F9FAFB',
                      }}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="border-slate-700 bg-slate-800 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-200">
                  <Target className="h-5 w-5 text-orange-400" />
                  Топ ключевых слов
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {keywordData.map((keyword: any, index: number) => (
                    <div
                      key={keyword.name}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-700 border border-slate-600 animate-fade-in-up"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: keyword.color }}
                        />
                        <span className="font-medium text-slate-200">
                          {keyword.name}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-slate-200">
                          {keyword.value}
                        </div>
                        <div className="text-xs text-slate-400">совпадений</div>
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
    <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-300">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-slate-400" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-200">
          {value.toLocaleString()}
        </div>
        <div className="flex items-center gap-2 mt-1">
          <Badge
            className={`text-xs ${trendUp ? 'bg-green-900 text-green-300 border-green-700' : 'bg-red-900 text-red-300 border-red-700'}`}
          >
            {trend}
          </Badge>
          <p className="text-xs text-slate-400">{description}</p>
        </div>
      </CardContent>
    </Card>
  )
}
