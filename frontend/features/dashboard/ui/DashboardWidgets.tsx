'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Progress } from '@/shared/ui'
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Users,
  MessageSquare,
  Target,
  BarChart3,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

/**
 * Виджет быстрой статистики
 */
interface QuickStatsWidgetProps {
  title: string
  value: number
  change: number
  changeType: 'increase' | 'decrease'
  icon: React.ComponentType<{ className?: string }>
  description: string
}

export function QuickStatsWidget({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  description,
}: QuickStatsWidgetProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-slate-400" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        <div className="flex items-center gap-2 mt-1">
          <Badge
            variant={changeType === 'increase' ? 'default' : 'destructive'}
            className="text-xs"
          >
            {changeType === 'increase' ? '+' : ''}
            {change}%
          </Badge>
          <p className="text-xs text-slate-500">{description}</p>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Виджет статуса системы
 */
interface SystemStatusWidgetProps {
  status: 'healthy' | 'warning' | 'error'
  message: string
  lastCheck: string
  uptime: string
}

export function SystemStatusWidget({
  status,
  message,
  lastCheck,
  uptime,
}: SystemStatusWidgetProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'healthy':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Статус системы
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <p className={`font-medium ${getStatusColor()}`}>
              {status === 'healthy'
                ? 'Система работает'
                : status === 'warning'
                  ? 'Внимание'
                  : 'Ошибка'}
            </p>
            <p className="text-sm text-slate-600">{message}</p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Последняя проверка:</span>
            <span>
              {formatDistanceToNow(new Date(lastCheck), {
                addSuffix: true,
                locale: ru,
              })}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Время работы:</span>
            <span>{uptime}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Виджет прогресса парсинга
 */
interface ParsingProgressWidgetProps {
  currentTask: string
  progress: number
  totalItems: number
  processedItems: number
  estimatedTime: string
}

export function ParsingProgressWidget({
  currentTask,
  progress,
  totalItems,
  processedItems,
  estimatedTime,
}: ParsingProgressWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Прогресс парсинга
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-sm font-medium text-slate-900">{currentTask}</p>
          <p className="text-xs text-slate-500">Обработка группы</p>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Прогресс</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-600">Обработано</p>
            <p className="font-semibold">{processedItems.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-slate-600">Всего</p>
            <p className="font-semibold">{totalItems.toLocaleString()}</p>
          </div>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Осталось времени:</span>
          <span>{estimatedTime}</span>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Виджет последних действий
 */
interface RecentActivityWidgetProps {
  activities: Array<{
    id: number
    type: 'parse' | 'comment' | 'group' | 'keyword'
    message: string
    timestamp: string
    status: 'success' | 'warning' | 'error'
  }>
}

export function RecentActivityWidget({
  activities,
}: RecentActivityWidgetProps) {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'parse':
        return <BarChart3 className="h-4 w-4 text-blue-500" />
      case 'comment':
        return <MessageSquare className="h-4 w-4 text-green-500" />
      case 'group':
        return <Users className="h-4 w-4 text-purple-500" />
      case 'keyword':
        return <Target className="h-4 w-4 text-orange-500" />
      default:
        return <Activity className="h-4 w-4 text-slate-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-slate-600'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Последние действия
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-slate-50"
            >
              <div className="flex-shrink-0 mt-0.5">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p
                  className={`text-sm font-medium ${getStatusColor(activity.status)}`}
                >
                  {activity.message}
                </p>
                <p className="text-xs text-slate-500">
                  {formatDistanceToNow(new Date(activity.timestamp), {
                    addSuffix: true,
                    locale: ru,
                  })}
                </p>
              </div>
            </div>
          ))}
        </div>

        <Button variant="outline" size="sm" className="w-full mt-4">
          Показать все
        </Button>
      </CardContent>
    </Card>
  )
}

/**
 * Виджет быстрых действий
 */
export function QuickActionsWidget() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Быстрые действия
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          <Button variant="outline" size="sm" className="h-12">
            <Users className="h-4 w-4 mr-2" />
            Добавить группу
          </Button>
          <Button variant="outline" size="sm" className="h-12">
            <Target className="h-4 w-4 mr-2" />
            Добавить ключевое слово
          </Button>
          <Button variant="outline" size="sm" className="h-12">
            <BarChart3 className="h-4 w-4 mr-2" />
            Запустить парсинг
          </Button>
          <Button variant="outline" size="sm" className="h-12">
            <MessageSquare className="h-4 w-4 mr-2" />
            Просмотр комментариев
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
