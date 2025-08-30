'use client'

import { RecentActivityItem } from '@/entities/dashboard'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { formatDistanceToNow } from 'date-fns'
import { Activity, MessageSquare, Search, Settings, AlertCircle, Play, Pause } from 'lucide-react'

interface ActivityFeedProps {
  activities: RecentActivityItem[]
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'parse':
        return Play
      case 'comment':
        return MessageSquare
      case 'match':
        return Search
      case 'settings':
        return Settings
      case 'error':
        return AlertCircle
      case 'stop':
        return Pause
      default:
        return Activity
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'parse':
        return 'text-green-500'
      case 'comment':
        return 'text-blue-500'
      case 'match':
        return 'text-orange-500'
      case 'settings':
        return 'text-purple-500'
      case 'error':
        return 'text-red-500'
      case 'stop':
        return 'text-yellow-500'
      default:
        return 'text-gray-500'
    }
  }

  const getActivityBadge = (type: string) => {
    switch (type) {
      case 'parse':
        return { label: 'Парсинг', variant: 'default' as const }
      case 'comment':
        return { label: 'Комментарий', variant: 'secondary' as const }
      case 'match':
        return { label: 'Совпадение', variant: 'destructive' as const }
      case 'settings':
        return { label: 'Настройки', variant: 'outline' as const }
      case 'error':
        return { label: 'Ошибка', variant: 'destructive' as const }
      case 'stop':
        return { label: 'Остановка', variant: 'secondary' as const }
      default:
        return { label: 'Активность', variant: 'outline' as const }
    }
  }

  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Лента активности
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Activity className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Нет недавней активности</p>
            <p className="text-sm text-muted-foreground">
              Активность появится здесь после запуска парсера
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Лента активности
          <Badge variant="outline" className="ml-auto">
            {activities.slice(0, 8).length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.slice(0, 8).map((activity) => {
            const Icon = getActivityIcon(activity.type)
            const badge = getActivityBadge(activity.type)

            return (
              <div key={activity.id} className="flex items-start gap-3">
                <div className={`flex-shrink-0 mt-0.5 ${getActivityColor(activity.type)}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">
                    {activity.message}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={badge.variant} className="text-xs">
                      {badge.label}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-4 pt-4 border-t">
          <Button variant="outline" className="w-full">
            Показать всю активность
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
