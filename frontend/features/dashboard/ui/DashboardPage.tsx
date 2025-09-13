'use client'

import { RefreshCw } from 'lucide-react'

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Alert,
  AlertDescription,
  Skeleton,
  Button,
  StatCard,
} from '@/shared/ui'
import { useGlobalStats, useDashboardStats } from '@/entities/dashboard'
import {
  ActivityFeed,
  RecentComments,
  StatsCards,
  TopGroups,
  TopKeywords,
} from '@/features/dashboard'

export function DashboardPage() {
  const {
    stats: globalStats,
    loading: globalLoading,
    error: globalError,
    refetch: refetchGlobal,
  } = useGlobalStats()
  const {
    stats: dashboardStats,
    loading: dashboardLoading,
    error: dashboardError,
    refetch: refetchDashboard,
  } = useDashboardStats()

  const isLoading = globalLoading || dashboardLoading
  const hasError = globalError || dashboardError

  const handleRefresh = () => {
    refetchGlobal()
    refetchDashboard()
  }

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-24" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16 mb-1" />
                <Skeleton className="h-3 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="container mx-auto py-6">
        <Alert className="border-destructive">
          <AlertDescription>
            Ошибка загрузки данных дашборда: {globalError || dashboardError}
            <Button variant="outline" size="sm" onClick={handleRefresh} className="ml-4">
              <RefreshCw className="mr-2 h-4 w-4" />
              Попробовать снова
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Панель управления</h1>
          <p className="text-muted-foreground">
            Мониторинг и аналитика вашего парсера комментариев VK
          </p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={isLoading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? 'Обновление...' : 'Обновить'}
        </Button>
      </div>

      {globalStats && <StatsCards stats={globalStats} />}

      {dashboardStats && globalStats && (
        <div className="grid gap-4 md:grid-cols-3">
          {[
            {
              title: 'Сегодня',
              value: dashboardStats.today_comments,
              description: `комментариев • ${dashboardStats.today_matches} совпадений`,
              icon: RefreshCw,
              iconColor: 'text-blue-600',
            },
            {
              title: 'За неделю',
              value: dashboardStats.week_comments,
              description: `комментариев • ${dashboardStats.week_matches} совпадений`,
              icon: RefreshCw,
              iconColor: 'text-green-600',
            },
            {
              title: 'Активность',
              value: globalStats.active_groups || 0,
              description: `групп • ${globalStats.active_keywords || 0} слов`,
              icon: RefreshCw,
              iconColor: 'text-purple-600',
            },
          ].map((card, index) => (
            <StatCard
              key={index}
              title={card.title}
              value={card.value}
              description={card.description}
              icon={card.icon}
              iconColor={card.iconColor}
              className="p-4"
            />
          ))}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 space-y-4">
          {dashboardStats && (
            <>
              <RecentComments comments={dashboardStats.recent_activity} />
              <TopGroups groups={dashboardStats.top_groups} />
            </>
          )}
        </div>

        <div className="col-span-3 space-y-4">
          {dashboardStats && (
            <>
              <TopKeywords keywords={dashboardStats.top_keywords} />
              <ActivityFeed activities={dashboardStats.recent_activity} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
