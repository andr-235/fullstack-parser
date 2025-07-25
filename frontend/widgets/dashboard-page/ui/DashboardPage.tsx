'use client'

import { useDashboardData } from '@/features/dashboard/hooks/use-dashboard-data'
import { useGlobalStats } from '@/features/dashboard/hooks/use-stats'
import { DashboardWidgets } from '@/features/dashboard/ui/DashboardWidgets'
import { DashboardFilters } from '@/features/dashboard/ui/DashboardFilters'
import { DashboardExport } from '@/features/dashboard/ui/DashboardExport'
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
  Settings
} from 'lucide-react'

export function DashboardPage() {
  const {
    activityData,
    topGroups,
    topKeywords,
    recentComments,
    systemStatus,
    parsingProgress,
    isLoading,
    error
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
              Не удалось загрузить данные дашборда. Попробуйте обновить страницу.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Дашборд</h1>
          <p className="text-muted-foreground">
            Обзор активности и статистики парсера
          </p>
        </div>
      </div>

      {/* Основные метрики */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего групп</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{globalStats?.data?.total_groups || 0}</div>
            <p className="text-xs text-muted-foreground">
              Активных: {globalStats?.data?.active_groups || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ключевые слова</CardTitle>
            <Hash className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{globalStats?.data?.total_keywords || 0}</div>
            <p className="text-xs text-muted-foreground">
              Активных: {globalStats?.data?.active_keywords || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Комментарии</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{globalStats?.data?.total_comments || 0}</div>
            <p className="text-xs text-muted-foreground">
              С ключевыми словами: {globalStats?.data?.comments_with_keywords || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активность</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {activityData?.data ? 'Активна' : 'Нет данных'}
            </div>
            <p className="text-xs text-muted-foreground">
              Последний парсинг: {globalStats?.data?.last_parse_time ? new Date(globalStats.data.last_parse_time).toLocaleDateString() : 'Неизвестно'}
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
                    Последняя проверка: {new Date(systemStatus.data.timestamp).toLocaleTimeString()}
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
                  {parsingProgress.data.status === 'running' ? 'Выполняется' : 'Остановлен'}
                </div>
                {parsingProgress.data.task && (
                  <div className="text-xs text-muted-foreground">
                    Группа: {parsingProgress.data.task.group_name}
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
            {topGroups?.data && topGroups.data.length > 0 ? (
              <div className="space-y-2">
                {topGroups.data.slice(0, 3).map((group, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="truncate">{group.name}</span>
                    <span className="text-muted-foreground">{group.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                Нет данных
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Дополнительные виджеты */}
      <DashboardWidgets />
    </div>
  )
}
