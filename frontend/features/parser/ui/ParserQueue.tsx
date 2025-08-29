'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Progress } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'
import {
 List,
 CheckCircle,
 Clock,
 AlertCircle,
 Play,
 Pause,
 Users,
 FileText,
 ArrowRight
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { ParserTasksResponse, ParseTaskResponse } from '@/entities/parser'

interface ParserQueueProps {
 tasks?: ParserTasksResponse | null
 loading?: boolean
 currentTaskId?: string
}

export function ParserQueue({ tasks, loading, currentTaskId }: ParserQueueProps) {
 const getStatusIcon = (status: string) => {
  switch (status) {
   case 'completed':
    return <CheckCircle className="h-4 w-4 text-green-500" />
   case 'running':
    return <Play className="h-4 w-4 text-blue-500 animate-pulse" />
   case 'stopped':
    return <Pause className="h-4 w-4 text-orange-500" />
   case 'failed':
    return <AlertCircle className="h-4 w-4 text-red-500" />
   default:
    return <Clock className="h-4 w-4 text-gray-400" />
  }
 }

 const getStatusBadgeVariant = (status: string) => {
  switch (status) {
   case 'completed':
    return 'default' as const
   case 'running':
    return 'default' as const
   case 'stopped':
    return 'secondary' as const
   case 'failed':
    return 'destructive' as const
   default:
    return 'outline' as const
  }
 }

 const getStatusText = (status: string) => {
  switch (status) {
   case 'completed':
    return 'Завершена'
   case 'running':
    return 'Выполняется'
   case 'stopped':
    return 'Остановлена'
   case 'failed':
    return 'Ошибка'
   default:
    return 'Ожидает'
  }
 }

 const getQueueStatus = (task: ParseTaskResponse, index: number) => {
  if (task.task_id === currentTaskId) return 'current'
  if (task.status === 'running') return 'current'
  if (task.status === 'completed') return 'completed'
  if (task.status === 'failed') return 'failed'
  if (index < 3) return 'queued' // Показываем первые 3 как в очереди
  return 'pending'
 }

 if (loading) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <List className="h-5 w-5" />
      Очередь задач
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="space-y-3">
      {[...Array(3)].map((_, i) => (
       <div key={i} className="flex items-center gap-3 p-3 rounded-lg border">
        <Skeleton className="h-4 w-4 rounded" />
        <div className="flex-1 space-y-2">
         <Skeleton className="h-4 w-32" />
         <Skeleton className="h-3 w-24" />
        </div>
        <Skeleton className="h-6 w-16" />
       </div>
      ))}
     </div>
    </CardContent>
   </Card>
  )
 }

 const displayTasks = tasks?.items?.slice(0, 10) || [] // Показываем максимум 10 задач

 if (displayTasks.length === 0) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <List className="h-5 w-5" />
      Очередь задач
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="flex flex-col items-center justify-center py-8 text-center">
      <List className="h-12 w-12 text-muted-foreground mb-4" />
      <p className="text-muted-foreground">Очередь пуста</p>
      <p className="text-sm text-muted-foreground">
       Задачи парсинга появятся здесь после запуска
      </p>
     </div>
    </CardContent>
   </Card>
  )
 }

 // Группируем задачи по статусу
 const runningTasks = displayTasks.filter(task => task.status === 'running')
 const queuedTasks = displayTasks.filter(task => task.status === 'stopped')
 const completedTasks = displayTasks.filter(task => task.status === 'completed')
 const failedTasks = displayTasks.filter(task => task.status === 'failed')

 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <List className="h-5 w-5" />
     Очередь задач
     <Badge variant="outline" className="ml-auto">
      {displayTasks.length}
     </Badge>
    </CardTitle>
   </CardHeader>
   <CardContent>
    <div className="space-y-4">
     {/* Статистика по статусам */}
     <div className="grid grid-cols-4 gap-2 text-center">
      <div className="p-2 bg-muted/50 rounded-lg border">
       <p className="text-xs text-muted-foreground font-medium">Завершено</p>
       <p className="text-lg font-bold text-green-600">{completedTasks.length}</p>
      </div>
      <div className="p-2 bg-muted/50 rounded-lg border">
       <p className="text-xs text-muted-foreground font-medium">Выполняется</p>
       <p className="text-lg font-bold text-blue-600">{runningTasks.length}</p>
      </div>
      <div className="p-2 bg-muted/50 rounded-lg border">
       <p className="text-xs text-muted-foreground font-medium">В очереди</p>
       <p className="text-lg font-bold text-orange-600">{queuedTasks.length}</p>
      </div>
      <div className="p-2 bg-muted/50 rounded-lg border">
       <p className="text-xs text-muted-foreground font-medium">Ошибки</p>
       <p className="text-lg font-bold text-red-600">{failedTasks.length}</p>
      </div>
     </div>

     {/* Список задач */}
     <div className="space-y-3 max-h-96 overflow-y-auto">
      {displayTasks.map((task, index) => {
       const queueStatus = getQueueStatus(task, index)

       return (
        <div
         key={task.task_id}
         className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${queueStatus === 'current'
          ? 'border-blue-200 bg-blue-50/50 shadow-sm'
          : queueStatus === 'queued'
           ? 'border-orange-200 bg-orange-50/50'
           : 'hover:bg-muted/30'
          }`}
        >
         {/* Статус и позиция в очереди */}
         <div className="flex flex-col items-center gap-1">
          {getStatusIcon(task.status)}
          {queueStatus === 'queued' && (
           <Badge variant="outline" className="text-xs px-1 py-0">
            #{index + 1}
           </Badge>
          )}
          {queueStatus === 'current' && (
           <ArrowRight className="h-3 w-3 text-blue-500 animate-pulse" />
          )}
         </div>

         {/* Информация о задаче */}
         <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
           <p className="text-sm font-medium truncate">
            {task.group_name ? `Парсинг: ${task.group_name}` : `Задача #${task.task_id.slice(-8)}`}
           </p>
           <Badge
            variant={getStatusBadgeVariant(task.status)}
            className="text-xs"
           >
            {getStatusText(task.status)}
           </Badge>
          </div>

          <div className="flex items-center gap-4 text-xs text-muted-foreground">
           <div className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            ID: {task.group_id}
           </div>
           <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatDistanceToNow(new Date(task.started_at), {
             addSuffix: true,
             locale: ru
            })}
           </div>
          </div>

          {/* Прогресс бар для активных задач */}
          {task.status === 'running' && task.progress !== undefined && (
           <div className="mt-2">
            <div className="flex justify-between text-xs mb-1">
             <span>Прогресс</span>
             <span>{(task.progress * 100).toFixed(1)}%</span>
            </div>
            <Progress value={task.progress * 100} className="h-1" />
           </div>
          )}

          {/* Статистика для завершенных задач */}
          {task.status === 'completed' && task.stats && (
           <div className="flex items-center gap-3 mt-2 text-xs">
            <div className="flex items-center gap-1">
             <FileText className="h-3 w-3 text-green-500" />
             <span className="text-green-600">{task.stats.posts_processed} постов</span>
            </div>
            {task.stats.comments_found > 0 && (
             <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3 text-blue-500" />
              <span className="text-blue-600">{task.stats.comments_found} комментариев</span>
             </div>
            )}
           </div>
          )}

          {/* Сообщение об ошибке */}
          {task.status === 'failed' && task.error_message && (
           <div className="mt-2 p-2 bg-red-50/50 border border-red-200 rounded text-xs text-red-700 dark:bg-red-950/50 dark:text-red-300">
            {task.error_message}
           </div>
          )}
         </div>
        </div>
       )
      })}
     </div>

     {/* Индикатор загрузки большего количества задач */}
     {tasks && tasks.total > displayTasks.length && (
      <div className="pt-4 border-t">
       <p className="text-sm text-muted-foreground text-center">
        Показано {displayTasks.length} из {tasks.total} задач
       </p>
      </div>
     )}
    </div>
   </CardContent>
  </Card>
 )
}
