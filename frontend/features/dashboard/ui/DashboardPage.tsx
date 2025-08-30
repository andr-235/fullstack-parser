'use client'

import { StatsCards } from '@/features/dashboard/ui/StatsCards'
import { RecentComments } from '@/features/dashboard/ui/RecentComments'
import { TopGroups } from '@/features/dashboard/ui/TopGroups'
import { TopKeywords } from '@/features/dashboard/ui/TopKeywords'
import { ActivityFeed } from '@/features/dashboard/ui/ActivityFeed'
import { useGlobalStats, useDashboardStats } from '@/entities/dashboard'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'
import { RefreshCw } from 'lucide-react'
import { Button } from '@/shared/ui'

export function DashboardPage() {
 const { stats: globalStats, loading: globalLoading, error: globalError, refetch: refetchGlobal } = useGlobalStats()
 const { stats: dashboardStats, loading: dashboardLoading, error: dashboardError, refetch: refetchDashboard } = useDashboardStats()

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

    {/* Stats Cards Skeleton */}
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

    {/* Content Grid Skeleton */}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
     <Card className="col-span-4">
      <CardHeader>
       <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent>
       <Skeleton className="h-64 w-full" />
      </CardContent>
     </Card>
     <Card className="col-span-3">
      <CardHeader>
       <Skeleton className="h-6 w-32" />
      </CardHeader>
      <CardContent>
       <Skeleton className="h-64 w-full" />
      </CardContent>
     </Card>
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
      <Button
       variant="outline"
       size="sm"
       onClick={handleRefresh}
       className="ml-4"
      >
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
   {/* Header */}
   <div className="flex items-center justify-between">
    <div>
     <h1 className="text-3xl font-bold tracking-tight">Панель управления</h1>
     <p className="text-muted-foreground">
      Мониторинг и аналитика вашего парсера комментариев VK
     </p>
    </div>
    <Button
     variant="outline"
     onClick={handleRefresh}
     disabled={isLoading}
     className="gap-2"
    >
     <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
     {isLoading ? 'Обновление...' : 'Обновить'}
    </Button>
   </div>

   {/* Stats Cards */}
   {globalStats && <StatsCards stats={globalStats} />}

   {/* Quick Stats Row */}
   {dashboardStats && (
    <div className="grid gap-4 md:grid-cols-3">
     <Card className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Сегодня</p>
        <p className="text-2xl font-bold">{dashboardStats.today_comments}</p>
        <p className="text-xs text-muted-foreground">
         комментариев • {dashboardStats.today_matches} совпадений
        </p>
       </div>
       <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
        <RefreshCw className="h-6 w-6 text-blue-600" />
       </div>
      </div>
     </Card>

     <Card className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">За неделю</p>
        <p className="text-2xl font-bold">{dashboardStats.week_comments}</p>
        <p className="text-xs text-muted-foreground">
         комментариев • {dashboardStats.week_matches} совпадений
        </p>
       </div>
       <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
        <RefreshCw className="h-6 w-6 text-green-600" />
       </div>
      </div>
     </Card>

     <Card className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Активность</p>
        <p className="text-2xl font-bold">{globalStats?.active_groups || 0}</p>
        <p className="text-xs text-muted-foreground">
         групп • {globalStats?.active_keywords || 0} слов
        </p>
       </div>
       <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
        <RefreshCw className="h-6 w-6 text-purple-600" />
       </div>
      </div>
     </Card>
    </div>
   )}

   {/* Main Content Grid */}
   <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
    {/* Left Column */}
    <div className="col-span-4 space-y-4">
     {dashboardStats && (
      <>
       <RecentComments comments={dashboardStats.recent_activity} />
       <TopGroups groups={dashboardStats.top_groups} />
      </>
     )}
    </div>

    {/* Right Column */}
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
