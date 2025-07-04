'use client'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { useGlobalStats } from '@/hooks/use-stats'
import { Users, MessageSquare, KeyRound } from 'lucide-react'
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
      <Card className="bg-destructive/10 text-destructive-foreground">
        <CardHeader>
          <CardTitle>Ошибка</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Не удалось загрузить статистику: {error.message}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Группы</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_groups || 0}</div>
            <p className="text-xs text-muted-foreground">Отслеживаемых групп</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Комментарии</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_comments || 0}
            </div>
            <p className="text-xs text-muted-foreground">Всего комментариев</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Ключевые слова
            </CardTitle>
            <KeyRound className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_keywords || 0}
            </div>
            <p className="text-xs text-muted-foreground">Отслеживаемых слов</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Активность комментариев</CardTitle>
          <CardDescription>
            График активности комментариев за последнее время.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex justify-center items-center bg-secondary/20 rounded-md">
            <p className="text-muted-foreground">(График в разработке)</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
