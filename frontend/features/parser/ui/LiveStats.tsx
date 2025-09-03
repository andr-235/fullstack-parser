'use client'

import { useState, useEffect } from 'react'

import {
 BarChart3,
 TrendingUp,
 TrendingDown,
 Activity,
 MessageSquare,
 Users,
 FileText,
 Zap,
 Target,
 RefreshCw
} from 'lucide-react'
import {
 BarChart,
 Bar,
 XAxis,
 YAxis,
 CartesianGrid,
 Tooltip,
 ResponsiveContainer,
 PieChart,
 Pie,
 Cell,
 LineChart,
 Line,
 Area,
 AreaChart
} from 'recharts'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'

import type { ParserStats, ParserGlobalStats, ParserState } from '@/entities/parser'

interface LiveStatsProps {
 stats?: ParserStats | null
 globalStats?: ParserGlobalStats | null
 state?: ParserState | null
 loading?: boolean
 isRunning?: boolean
}

export function LiveStats({ stats, globalStats, state, loading, isRunning }: LiveStatsProps) {
 const [animatedValues, setAnimatedValues] = useState({
  totalComments: 0,
  totalPosts: 0,
  successRate: 0,
  avgDuration: 0
 })

 // Анимируем значения при изменении
 useEffect(() => {
  if (!stats) return

  const targetValues = {
   totalComments: globalStats?.total_comments_found || 0,
   totalPosts: stats.total_posts_found || 0,
   successRate: stats.total_tasks > 0
    ? Math.round((stats.completed_tasks / stats.total_tasks) * 100)
    : 0,
   avgDuration: Math.round(stats.average_task_duration || 0)
  }

  const animateValue = (key: keyof typeof animatedValues, start: number, end: number, duration: number = 1500) => {
   const startTime = Date.now()
   const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    return Math.round(start + (end - start) * easeOutQuart)
   }

   const interval = setInterval(() => {
    const current = animate()
    setAnimatedValues(prev => ({ ...prev, [key]: current }))

    if (Date.now() - startTime >= duration) {
     clearInterval(interval)
     setAnimatedValues(prev => ({ ...prev, [key]: end }))
    }
   }, 50)
  }

  // Анимируем каждое значение
  Object.entries(targetValues).forEach(([key, target]) => {
   const current = animatedValues[key as keyof typeof animatedValues]
   if (current !== target) {
    animateValue(key as keyof typeof animatedValues, current, target)
   }
  })
 }, [stats, globalStats])

 const formatNumber = (num: number) => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
 }

 const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${seconds} сек`
  if (seconds < 3600) return `${Math.round(seconds / 60)} мин`
  return `${Math.round(seconds / 3600)} ч`
 }

 // Данные для графиков
 const chartData = [
  {
   name: 'Комментарии',
   value: globalStats?.total_comments_found || 0,
   color: '#3b82f6'
  },
  {
   name: 'Посты',
   value: stats?.total_posts_found || 0,
   color: '#10b981'
  },
  {
   name: 'Ключевые слова',
   value: globalStats?.total_comments_found || 0, // В новом API нет comments_with_keywords
   color: '#f59e0b'
  }
 ]

 const pieData = [
  { name: 'Успешные', value: stats?.completed_tasks || 0, color: '#10b981' },
  { name: 'Ошибки', value: stats?.failed_tasks || 0, color: '#ef4444' }
 ]

 const trendData = [
  { time: '00:00', posts: Math.floor((stats?.total_posts_found || 0) * 0.1) },
  { time: '04:00', posts: Math.floor((stats?.total_posts_found || 0) * 0.25) },
  { time: '08:00', posts: Math.floor((stats?.total_posts_found || 0) * 0.5) },
  { time: '12:00', posts: Math.floor((stats?.total_posts_found || 0) * 0.75) },
  { time: '16:00', posts: Math.floor((stats?.total_posts_found || 0) * 0.9) },
  { time: '20:00', posts: stats?.total_posts_found || 0 }
 ]

 if (loading) {
  return (
   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <Card>
     <CardHeader>
      <CardTitle className="flex items-center gap-2">
       <BarChart3 className="h-5 w-5" />
       Статистика парсинга
      </CardTitle>
     </CardHeader>
     <CardContent>
      <div className="h-64 flex items-center justify-center">
       <Skeleton className="h-full w-full rounded-lg" />
      </div>
     </CardContent>
    </Card>

    <Card>
     <CardHeader>
      <CardTitle className="flex items-center gap-2">
       <Activity className="h-5 w-5" />
       Активность
      </CardTitle>
     </CardHeader>
     <CardContent>
      <div className="h-64 flex items-center justify-center">
       <Skeleton className="h-full w-full rounded-lg" />
      </div>
     </CardContent>
    </Card>
   </div>
  )
 }

 return (
  <div className="space-y-6">
   {/* Основные метрики */}
   <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
    <Card className="relative overflow-hidden">
     <CardContent className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Комментарии</p>
        <p className="text-2xl font-bold">{formatNumber(animatedValues.totalComments)}</p>
       </div>
       <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
        <MessageSquare className="h-5 w-5 text-blue-600 dark:text-blue-400" />
       </div>
      </div>
      {globalStats?.total_comments_found && globalStats.total_comments_found > 0 && (
       <Badge variant="secondary" className="mt-2 text-xs">
        <TrendingUp className="h-3 w-3 mr-1" />
        Активно
       </Badge>
      )}
     </CardContent>
    </Card>

    <Card className="relative overflow-hidden">
     <CardContent className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Обработано постов</p>
        <p className="text-2xl font-bold">{formatNumber(animatedValues.totalPosts)}</p>
       </div>
       <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
        <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
       </div>
      </div>
      {stats?.total_posts_found && stats.total_posts_found > 0 && (
       <Badge variant="secondary" className="mt-2 text-xs">
        <TrendingUp className="h-3 w-3 mr-1" />
        Растет
       </Badge>
      )}
     </CardContent>
    </Card>

    <Card className="relative overflow-hidden">
     <CardContent className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Успешность</p>
        <p className="text-2xl font-bold">{animatedValues.successRate}%</p>
       </div>
       <div className={`p-2 rounded-lg ${animatedValues.successRate >= 80 ? 'bg-green-100 dark:bg-green-900/20' : animatedValues.successRate >= 50 ? 'bg-orange-100 dark:bg-orange-900/20' : 'bg-red-100 dark:bg-red-900/20'}`}>
        <Target className={`h-5 w-5 ${animatedValues.successRate >= 80 ? 'text-green-600 dark:text-green-400' : animatedValues.successRate >= 50 ? 'text-orange-600 dark:text-orange-400' : 'text-red-600 dark:text-red-400'}`} />
       </div>
      </div>
      {animatedValues.successRate >= 80 ? (
       <Badge variant="secondary" className="mt-2 text-xs bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400">
        Отлично
       </Badge>
      ) : animatedValues.successRate >= 50 ? (
       <Badge variant="secondary" className="mt-2 text-xs bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400">
        Хорошо
       </Badge>
      ) : (
       <Badge variant="destructive" className="mt-2 text-xs">
        Низкая
       </Badge>
      )}
     </CardContent>
    </Card>

    <Card className="relative overflow-hidden">
     <CardContent className="p-4">
      <div className="flex items-center justify-between">
       <div>
        <p className="text-sm font-medium text-muted-foreground">Среднее время</p>
        <p className="text-2xl font-bold">{formatDuration(animatedValues.avgDuration)}</p>
       </div>
       <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
        <Activity className="h-5 w-5 text-purple-600 dark:text-purple-400" />
       </div>
      </div>
      {stats?.average_task_duration && (
       <Badge variant="outline" className="mt-2 text-xs">
        <RefreshCw className="h-3 w-3 mr-1" />
        Обновлено
       </Badge>
      )}
     </CardContent>
    </Card>
   </div>

   {/* Графики */}
   <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    {/* Столбчатая диаграмма */}
    <Card>
     <CardHeader>
      <CardTitle className="flex items-center gap-2">
       <BarChart3 className="h-5 w-5" />
       Статистика обработки
      </CardTitle>
     </CardHeader>
     <CardContent>
      <div className="h-64">
       <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
         <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
         <XAxis
          dataKey="name"
          fontSize={12}
          className="text-muted-foreground"
         />
         <YAxis
          fontSize={12}
          className="text-muted-foreground"
         />
         <Tooltip
          contentStyle={{
           backgroundColor: 'hsl(var(--background))',
           border: '1px solid hsl(var(--border))',
           borderRadius: '6px'
          }}
          labelStyle={{ color: 'hsl(var(--foreground))' }}
         />
         <Bar
          dataKey="value"
          fill="#3b82f6"
          radius={[4, 4, 0, 0]}
          className="fill-primary"
         />
        </BarChart>
       </ResponsiveContainer>
      </div>
     </CardContent>
    </Card>

    {/* Круговая диаграмма успешности */}
    <Card>
     <CardHeader>
      <CardTitle className="flex items-center gap-2">
       <Target className="h-5 w-5" />
       Успешность парсинга
      </CardTitle>
     </CardHeader>
     <CardContent>
      <div className="h-64 flex items-center justify-center">
       <ResponsiveContainer width="100%" height="100%">
        <PieChart>
         <Pie
          data={pieData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={5}
          dataKey="value"
         >
          {pieData.map((entry, index) => (
           <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
         </Pie>
         <Tooltip
          contentStyle={{
           backgroundColor: 'hsl(var(--background))',
           border: '1px solid hsl(var(--border))',
           borderRadius: '6px'
          }}
         />
        </PieChart>
       </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-4 mt-4">
       {pieData.map((entry, index) => (
        <div key={index} className="flex items-center gap-2">
         <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: entry.color }}
         />
         <span className="text-sm text-muted-foreground">
          {entry.name}: {entry.value}
         </span>
        </div>
       ))}
      </div>
     </CardContent>
    </Card>
   </div>

   {/* График трендов */}
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Activity className="h-5 w-5" />
      Тренд обработки постов
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
       <AreaChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <defs>
         <linearGradient id="colorPosts" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
         </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
        <XAxis
         dataKey="time"
         fontSize={12}
         className="text-muted-foreground"
        />
        <YAxis
         fontSize={12}
         className="text-muted-foreground"
        />
        <Tooltip
         contentStyle={{
          backgroundColor: 'hsl(var(--background))',
          border: '1px solid hsl(var(--border))',
          borderRadius: '6px'
         }}
         labelStyle={{ color: 'hsl(var(--foreground))' }}
        />
        <Area
         type="monotone"
         dataKey="posts"
         stroke="#3b82f6"
         fillOpacity={1}
         fill="url(#colorPosts)"
         strokeWidth={2}
        />
       </AreaChart>
      </ResponsiveContainer>
     </div>
    </CardContent>
   </Card>

   {/* Дополнительная информация */}
   <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    <Card>
     <CardContent className="p-4">
      <div className="flex items-center gap-3">
       <div className="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg">
        <Users className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
       </div>
       <div>
        <p className="text-sm font-medium text-muted-foreground">Активные группы</p>
        <p className="text-xl font-bold">
         0
         <span className="text-sm text-muted-foreground ml-1">
          / 0
         </span>
        </p>
       </div>
      </div>
     </CardContent>
    </Card>

    <Card>
     <CardContent className="p-4">
      <div className="flex items-center gap-3">
       <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
        <Target className="h-5 w-5 text-orange-600 dark:text-orange-400" />
       </div>
       <div>
        <p className="text-sm font-medium text-muted-foreground">Ключевые слова</p>
        <p className="text-xl font-bold">
         0
         <span className="text-sm text-muted-foreground ml-1">
          / 0
         </span>
        </p>
       </div>
      </div>
     </CardContent>
    </Card>

    <Card>
     <CardContent className="p-4">
      <div className="flex items-center gap-3">
       <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
        <Zap className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
       </div>
       <div>
        <p className="text-sm font-medium text-muted-foreground">Найдено совпадений</p>
        <p className="text-xl font-bold">
         {formatNumber(globalStats?.total_comments_found || 0)}
        </p>
       </div>
      </div>
     </CardContent>
    </Card>
   </div>

   {/* Время последнего парсинга */}
   {state?.last_activity && (
    <Card>
     <CardContent className="p-4">
      <div className="flex items-center gap-3">
       <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
        <Activity className="h-5 w-5 text-green-600 dark:text-green-400" />
       </div>
       <div>
        <p className="text-sm font-medium text-muted-foreground">Последняя активность</p>
        <p className="text-lg font-semibold">
         {new Date(state.last_activity).toLocaleString('ru-RU')}
        </p>
        {isRunning && (
         <Badge variant="default" className="mt-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1" />
          Активен сейчас
         </Badge>
        )}
       </div>
      </div>
     </CardContent>
    </Card>
   )}
  </div>
 )
}
