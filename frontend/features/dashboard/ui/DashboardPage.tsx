'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useGlobalStats } from '@/hooks/use-stats'
import { Users, MessageSquare, KeyRound, Activity } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useGlobalStats()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-full">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-red-500">Ошибка</CardTitle>
          </CardHeader>
          <CardContent>
            <p>
              Не удалось загрузить статистику. Попробуйте обновить страницу.
            </p>
            <p className="text-sm text-slate-400 mt-2">
              {error instanceof Error ? error.message : String(error)}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1">
            <CardTitle className="text-xs font-bold">Группы</CardTitle>
            <Users className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">{stats?.total_groups || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1">
            <CardTitle className="text-xs font-bold">Комментарии</CardTitle>
            <MessageSquare className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">
              {stats?.total_comments || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-1">
            <CardTitle className="text-xs font-bold">Ключевые слова</CardTitle>
            <KeyRound className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold">
              {stats?.total_keywords || 0}
            </div>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm font-bold">
            <Activity className="h-5 w-5" /> Активность комментариев
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex justify-center items-center bg-slate-800 border border-slate-700 rounded-sm">
            <p className="text-slate-400">График скоро появится здесь</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
