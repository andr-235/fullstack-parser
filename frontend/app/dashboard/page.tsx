'use client'

import { useDashboardStats, useGlobalStats } from '@/hooks/use-stats'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner, LoadingSpinnerWithText } from '@/components/ui/loading-spinner'
import { 
  BarChart3, 
  Users, 
  KeyRound, 
  MessageSquare,
  TrendingUp,
  Activity,
  AlertCircle
} from 'lucide-react'
import { formatNumber, formatRelativeTime } from '@/lib/utils'

export default function DashboardPage() {
  const { data: dashboardStats, isLoading: isDashboardLoading, error: dashboardError } = useDashboardStats()
  const { data: globalStats, isLoading: isGlobalLoading } = useGlobalStats()

  if (isDashboardLoading || isGlobalLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinnerWithText text="Загрузка статистики..." size="lg" />
      </div>
    )
  }

  if (dashboardError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Ошибка загрузки данных
          </h3>
          <p className="text-gray-600">
            Не удалось подключиться к API. Проверьте backend.
          </p>
        </div>
      </div>
    )
  }

  const stats = globalStats || {
    total_groups: 0,
    active_groups: 0,
    total_keywords: 0,
    active_keywords: 0,
    total_comments: 0,
    comments_with_keywords: 0,
    last_parse_time: null
  }

  const dashboard = dashboardStats || {
    today_comments: 0,
    today_matches: 0,
    week_comments: 0,
    week_matches: 0,
    top_groups: [],
    top_keywords: [],
    recent_activity: []
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Дашборд</h1>
        <p className="text-gray-600 mt-2">
          Общая статистика и мониторинг системы парсинга VK комментариев
        </p>
      </div>

      {/* Main Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активных групп</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.active_groups)}</div>
            <p className="text-xs text-gray-600">
              из {formatNumber(stats.total_groups)} всего
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ключевых слов</CardTitle>
            <KeyRound className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.active_keywords)}</div>
            <p className="text-xs text-gray-600">
              из {formatNumber(stats.total_keywords)} всего
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Найдено комментариев</CardTitle>
            <MessageSquare className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.total_comments)}</div>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-600">Сегодня:</span>
              <Badge variant="secondary" className="text-xs">
                +{formatNumber(dashboard.today_comments)}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Совпадений</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(stats.comments_with_keywords)}</div>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-600">Сегодня:</span>
              <Badge variant="success" className="text-xs">
                +{formatNumber(dashboard.today_matches)}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Активность парсинга
            </CardTitle>
            <CardDescription>
              Последняя активность: {stats.last_parse_time ? formatRelativeTime(stats.last_parse_time) : 'Никогда'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
              <div className="text-center">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 font-medium">График активности</p>
                <p className="text-sm text-gray-400">Будет реализован в следующих обновлениях</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Последние действия</CardTitle>
            <CardDescription>Актуальная активность системы</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboard.recent_activity.length > 0 ? (
                dashboard.recent_activity.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`h-2 w-2 rounded-full mt-2 ${
                      activity.type === 'parse' ? 'bg-green-500' :
                      activity.type === 'comment' ? 'bg-blue-500' : 'bg-purple-500'
                    }`}></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500">
                        {formatRelativeTime(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="h-2 w-2 bg-green-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">Система запущена</p>
                      <p className="text-xs text-gray-500">Только что</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">Подключение к API установлено</p>
                      <p className="text-xs text-gray-500">1 минуту назад</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="h-2 w-2 bg-purple-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">Фронтенд готов к работе</p>
                      <p className="text-xs text-gray-500">2 минуты назад</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Keywords and Groups */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Топ ключевых слов</CardTitle>
            <CardDescription>Самые активные ключевые слова за неделю</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.top_keywords.length > 0 ? (
                dashboard.top_keywords.map((keyword, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{keyword.word}</span>
                    <Badge variant="outline">{formatNumber(keyword.count)}</Badge>
                  </div>
                ))
              ) : (
                <div className="text-center py-6">
                  <KeyRound className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Нет данных о ключевых словах</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Топ групп</CardTitle>
            <CardDescription>Самые активные группы за неделю</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.top_groups.length > 0 ? (
                dashboard.top_groups.map((group, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{group.name}</span>
                    <Badge variant="outline">{formatNumber(group.count)}</Badge>
                  </div>
                ))
              ) : (
                <div className="text-center py-6">
                  <Users className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Нет данных о группах</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 