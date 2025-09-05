'use client'

import { useState, useEffect } from 'react'

import { formatDistanceToNow, differenceInSeconds } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
 Clock,
 Zap,
 FileText,
 Users,
 MessageSquare,
 TrendingUp,
 Activity
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Progress } from '@/shared/ui'

import type { ParserState } from '@/entities/parser'

interface ParserProgressProps {
 state?: ParserState | null
 isRunning: boolean
}

export function ParserProgress({ state, isRunning }: ParserProgressProps) {
 const [elapsedTime, setElapsedTime] = useState(0)
 const [currentTime] = useState(new Date())

 // Обновляем время выполнения каждую секунду
 useEffect(() => {
  if (!isRunning || !state?.last_activity) {
   setElapsedTime(0)
   return
  }

  const interval = setInterval(() => {
   const startTime = new Date(state?.last_activity || Date.now())
   const now = new Date()
   setElapsedTime(differenceInSeconds(now, startTime))
  }, 1000)

  return () => clearInterval(interval)
 }, [isRunning, state?.last_activity])

 const formatElapsedTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
   return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
 }

 const calculateSpeed = () => {
  if (!state?.total_posts_found || elapsedTime === 0) return 0
  return Math.round((state.total_posts_found / elapsedTime) * 60) // постов в минуту
 }

 const getEstimatedTimeRemaining = () => {
  // В новом API нет информации о прогрессе, возвращаем null
  return null
 }

 if (!isRunning && !state?.is_running) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Activity className="h-5 w-5" />
      Прогресс парсинга
     </CardTitle>
    </CardHeader>
    <CardContent className="space-y-6">
     <div className="flex flex-col items-center justify-center py-8 text-center">
      <Clock className="h-12 w-12 text-muted-foreground mb-4" />
      <p className="text-muted-foreground">Парсер не запущен</p>
      <p className="text-sm text-muted-foreground">
       Запустите парсинг, чтобы увидеть детальный прогресс
      </p>
     </div>

     {/* Дополнительная информация для заполнения пространства */}
     <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
       <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
        <FileText className="h-4 w-4 text-green-500" />
        <div>
         <p className="text-sm font-medium">Обработано постов</p>
         <p className="text-lg font-bold">0</p>
        </div>
       </div>

       <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
        <Zap className="h-4 w-4 text-purple-500" />
        <div>
         <p className="text-sm font-medium">Скорость</p>
         <p className="text-lg font-bold">0/мин</p>
        </div>
       </div>
      </div>

      <div className="p-3 bg-muted/50 rounded-lg border">
       <div className="flex items-center gap-2 mb-2">
        <Users className="h-4 w-4 text-indigo-500" />
        <span className="text-sm font-medium">Готов к работе</span>
       </div>
       <p className="text-sm text-muted-foreground">
        Парсер готов к запуску. Выберите группы для парсинга и нажмите кнопку "Запустить парсер".
       </p>
      </div>
     </div>
    </CardContent>
   </Card>
  )
 }

 const progress = 0 // В новом API нет информации о прогрессе
 const speed = calculateSpeed()
 const estimatedTime = getEstimatedTimeRemaining()

 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Activity className="h-5 w-5" />
     Прогресс парсинга
     <Badge variant="default" className="ml-auto animate-pulse">
      Активный
     </Badge>
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-6">
    {/* Основной прогресс */}
    <div className="space-y-2">
     <div className="flex justify-between text-sm">
      <span>Общий прогресс</span>
      <span className="font-medium">{progress.toFixed(1)}%</span>
     </div>
     <Progress value={progress} className="w-full h-3" />
    </div>

    {/* Время выполнения */}
    <div className="grid grid-cols-2 gap-4">
     <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
      <Clock className="h-4 w-4 text-blue-500" />
      <div>
       <p className="text-sm font-medium text-muted-foreground">Время выполнения</p>
       <p className="text-lg font-bold">
        {formatElapsedTime(elapsedTime)}
       </p>
      </div>
     </div>

     {estimatedTime && (
      <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
       <TrendingUp className="h-4 w-4 text-orange-500" />
       <div>
        <p className="text-sm font-medium text-muted-foreground">Осталось</p>
        <p className="text-lg font-bold">
         {estimatedTime}
        </p>
       </div>
      </div>
     )}
    </div>

    {/* Статистика обработки */}
    <div className="grid grid-cols-2 gap-4">
     <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
      <FileText className="h-4 w-4 text-green-500" />
      <div>
       <p className="text-sm font-medium text-muted-foreground">Обработано постов</p>
       <p className="text-lg font-bold">
        {state?.total_posts_found || 0}
       </p>
      </div>
     </div>

     <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
      <Zap className="h-4 w-4 text-purple-500" />
      <div>
       <p className="text-sm font-medium text-muted-foreground">Скорость</p>
       <p className="text-lg font-bold">
        {speed} постов/мин
       </p>
      </div>
     </div>
    </div>

    {/* Информация о группе */}
    <div className="p-3 bg-muted/50 rounded-lg border border-border">
     <div className="flex items-center gap-2 mb-2">
      <Users className="h-4 w-4 text-indigo-500" />
      <span className="text-sm font-medium">Текущая группа</span>
     </div>
     <p className="text-sm">
      <span className="text-muted-foreground">Парсер запущен</span>
     </p>
     <p className="text-xs text-muted-foreground mt-1">
      Начало: {state?.last_activity ? formatDistanceToNow(new Date(state.last_activity), {
       addSuffix: true,
       locale: ru
      }) : 'Неизвестно'}
     </p>
    </div>

    {/* Анимированная индикация активности */}
    <div className="flex items-center justify-center gap-2 py-2">
     <div className="flex gap-1">
      {[0, 1, 2].map((i) => (
       <div
        key={i}
        className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
        style={{
         animationDelay: `${i * 0.2}s`,
         animationDuration: '1.4s'
        }}
       />
      ))}
     </div>
     <span className="text-sm text-muted-foreground">Парсинг активен</span>
    </div>
   </CardContent>
  </Card>
 )
}
