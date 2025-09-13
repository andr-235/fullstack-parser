'use client'

import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { MessageSquare, ExternalLink, Clock, CheckCircle, AlertCircle, Users } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'

import { RecentActivityItem } from '@/entities/dashboard'

interface RecentCommentsProps {
  comments: RecentActivityItem[]
}

export function RecentComments({ comments }: RecentCommentsProps) {
  // Фильтруем только комментарии из активности
  const recentComments = comments
    .filter(activity => activity.type === 'comment' || activity.type === 'match')
    .slice(0, 8)

  if (recentComments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Последние комментарии
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Нет новых комментариев</p>
            <p className="text-sm text-muted-foreground">
              Комментарии появятся здесь после запуска парсера
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'match':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'comment':
        return <MessageSquare className="h-4 w-4 text-blue-500" />
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getActivityBadge = (type: string) => {
    switch (type) {
      case 'match':
        return { label: 'Совпадение', variant: 'default' as const }
      case 'comment':
        return { label: 'Комментарий', variant: 'secondary' as const }
      default:
        return { label: 'Активность', variant: 'outline' as const }
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Последние комментарии
          {recentComments.length > 0 && (
            <Badge variant="outline" className="ml-auto">
              {recentComments.length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {recentComments.map(comment => {
            const badge = getActivityBadge(comment.type)
            const icon = getActivityIcon(comment.type)

            return (
              <div
                key={comment.id}
                className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/30 transition-colors"
              >
                <div className="flex-shrink-0 mt-0.5">{icon}</div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground mb-2">{comment.message}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={badge.variant} className="text-xs">
                        {badge.label}
                      </Badge>
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span className="text-xs">
                          {formatDistanceToNow(new Date(comment.timestamp), {
                            addSuffix: true,
                            locale: ru,
                          })}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(comment.timestamp), 'HH:mm', { locale: ru })}
                    </span>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  className="flex-shrink-0 opacity-0 group-hover:opacity-100"
                >
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            )
          })}
        </div>

        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-muted-foreground">
              Показано {recentComments.length} последних
            </p>
            <Badge variant="outline" className="text-xs">
              <Users className="h-3 w-3 mr-1" />
              Активность
            </Badge>
          </div>
          <Button variant="outline" className="w-full">
            Показать все комментарии
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
