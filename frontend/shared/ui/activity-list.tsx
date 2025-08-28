'use client'

import * as React from 'react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { RefreshCw, MessageSquare, Users } from 'lucide-react'
import { cn } from '@/shared/lib/utils'

export interface ActivityItem {
  id: string
  type: 'parse' | 'comment' | 'group' | 'keyword'
  message: string
  timestamp: string
}

export interface ActivityListProps {
  activities: ActivityItem[]
  maxItems?: number
  className?: string
}

const getActivityIcon = (type: ActivityItem['type']) => {
  switch (type) {
    case 'parse':
      return RefreshCw
    case 'comment':
      return MessageSquare
    case 'group':
      return Users
    case 'keyword':
      return MessageSquare
    default:
      return MessageSquare
  }
}

const getActivityColor = (type: ActivityItem['type']) => {
  switch (type) {
    case 'parse':
      return 'text-primary'
    case 'comment':
      return 'text-primary'
    case 'group':
      return 'text-secondary-foreground'
    case 'keyword':
      return 'text-primary'
    default:
      return 'text-primary'
  }
}

export function ActivityList({
  activities,
  maxItems = 5,
  className
}: ActivityListProps) {
  const safeActivities = Array.isArray(activities) ? activities : []
  const displayActivities = safeActivities.slice(0, maxItems)

  if (displayActivities.length === 0) {
    return (
      <div className={cn('flex items-center justify-center py-8 text-muted-foreground', className)}>
        Нет активности
      </div>
    )
  }

  return (
    <div className={cn('space-y-3', className)}>
      {displayActivities.map((activity, index) => {
        const Icon = getActivityIcon(activity.type)
        const iconColor = getActivityColor(activity.type)

        return (
          <div
            key={activity.id}
            className="flex items-center gap-3 p-3 rounded-lg bg-card border animate-fade-in-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex-shrink-0">
              <Icon className={cn('h-4 w-4', iconColor)} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground">
                {activity.message}
              </p>
              <p className="text-xs text-muted-foreground">
                {(() => {
                  try {
                    const date = new Date(activity.timestamp)
                    return isNaN(date.getTime())
                      ? 'Неверная дата'
                      : formatDistanceToNow(date, {
                        addSuffix: true,
                        locale: ru,
                      })
                  } catch {
                    return 'Неверная дата'
                  }
                })()}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
