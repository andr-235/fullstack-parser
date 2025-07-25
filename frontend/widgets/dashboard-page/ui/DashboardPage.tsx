'use client'

import { useDashboardData } from '@/features/dashboard/hooks/use-dashboard-data'
import { useGlobalStats } from '@/features/dashboard/hooks/use-stats'
import { LoadingSpinner } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import {
  Activity,
  Users,
  MessageSquare,
  Hash,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  Settings,
} from 'lucide-react'
import type { DashboardStats } from '@/types/api'

export function DashboardPage() {
  const {
    activityData,
    topGroups,
    topKeywords,
    recentComments,
    systemStatus,
    parsingProgress,
    isLoading,
    error,
  } = useDashboardData()

  const { data: globalStats } = useGlobalStats()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Ошибка загрузки
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Не удалось загрузить данные дашборда. Попробуйте обновить
              страницу.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Извлекаем данные из единого эндпоинта /stats/dashboard
  const dashboardStats = activityData?.data as DashboardStats | undefined
  const topGroupsData = dashboardStats?.top_groups || []
  const topKeywordsData = dashboardStats?.top_keywords || []
  const recentActivityData = dashboardStats?.recent_activity || []

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Дашборд</h1>
          <p className="text-muted-foreground">
            Обзор активности и статистики системы
          </p>
        </div>
      </div>

      {/* Основная статистика */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Комментарии сегодня
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardStats?.today_comments || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              +{dashboardStats?.today_matches || 0} совпадений
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Комментарии за неделю
            </CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardStats?.week_comments || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              +{dashboardStats?.week_matches || 0} совпадений
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Активных групп
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {globalStats?.data?.active_groups || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              из {globalStats?.data?.total_groups || 0} всего
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ключевых слов</CardTitle>
            <Hash className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {globalStats?.data?.active_keywords || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              из {globalStats?.data?.total_keywords || 0} всего
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Виджеты */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Статус системы */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Статус системы
            </CardTitle>
          </CardHeader>
          <CardContent>
            {systemStatus?.data ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Система работает</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">
                    Последняя проверка: {new Date().toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                <span className="text-sm">Нет данных о статусе</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Прогресс парсинга */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Прогресс парсинга
            </CardTitle>
          </CardHeader>
          <CardContent>
            {parsingProgress?.data ? (
              <div className="space-y-2">
                <div className="text-sm font-medium">
                  {parsingProgress.data.status === 'running'
                    ? 'Выполняется'
                    : 'Остановлен'}
                </div>
                {parsingProgress.data.task && (
                  <div className="text-xs text-muted-foreground">
                    Группа:{' '}
                    {parsingProgress.data.task.group_name || 'Неизвестно'}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                Нет активных задач
              </div>
            )}
          </CardContent>
        </Card>

        {/* Топ групп */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Топ групп
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topGroupsData.length > 0 ? (
              <div className="space-y-2">
                {topGroupsData.slice(0, 3).map((group, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="truncate">{group.name}</span>
                    <span className="text-muted-foreground">{group.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            )}
          </CardContent>
        </Card>

        {/* Топ ключевых слов */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-5 w-5" />
              Топ ключевых слов
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topKeywordsData.length > 0 ? (
              <div className="space-y-2">
                {topKeywordsData.slice(0, 3).map((keyword, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="truncate">{keyword.word}</span>
                    <span className="text-muted-foreground">
                      {keyword.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">Нет данных</div>
            )}
          </CardContent>
        </Card>

        {/* Последняя активность */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Последняя активность
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentActivityData.length > 0 ? (
              <div className="space-y-2">
                {recentActivityData.slice(0, 3).map((activity, index) => (
                  <div key={index} className="text-sm">
                    <div className="font-medium">{activity.message}</div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                Нет активности
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
