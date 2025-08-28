'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { useNumberFormat } from '@/shared/hooks'
import { BADGE_VARIANTS } from '@/shared/constants'
import { LucideIcon, TrendingUp, TrendingDown, MoreHorizontal } from 'lucide-react'

export interface MetricCardProps {
 /** Заголовок метрики */
 title: string
 /** Значение метрики */
 value: number | string
 /** Иконка метрики */
 icon?: LucideIcon
 /** Описание метрики */
 description?: string
 /** Тренд (например, "+12%", "-5%") */
 trend?: string
 /** Направление тренда */
 trendUp?: boolean
 /** Цвет метрики */
 color?: 'blue' | 'green' | 'purple' | 'red' | 'yellow' | 'cyan' | 'orange' | 'gray'
 /** Процентное значение */
 percentage?: number
 /** Дополнительные действия */
 actions?: React.ReactNode
 /** Дочерний контент (график и т.д.) */
 children?: React.ReactNode
 /** Классы для стилизации */
 className?: string
 /** Размер карточки */
 size?: 'default' | 'large'
 /** Показывать ли градиентный фон */
 gradient?: boolean
}

/**
 * Универсальный компонент для больших метрик с трендами и графиками
 * Заменяет повторяющиеся паттерны карточек в DashboardPage
 */
export function MetricCard({
 title,
 value,
 icon: Icon,
 description,
 trend,
 trendUp,
 color = 'blue',
 percentage,
 actions,
 children,
 className,
 size = 'default',
 gradient = false,
}: MetricCardProps) {
 const formattedValue = useNumberFormat(typeof value === 'number' ? value : 0, {
  compact: true,
  decimals: 0,
 })

 const TrendIcon = trendUp ? TrendingUp : TrendingDown
 const trendColor = trendUp ? 'text-green-500' : 'text-red-500'

 const cardClasses = cn(
  'transition-all duration-300 hover:shadow-lg',
  gradient && 'bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600',
  size === 'large' && 'col-span-2 md:col-span-2',
  className
 )

 const titleClasses = cn(
  'text-lg font-semibold',
  gradient ? 'text-white' : 'text-foreground'
 )

 const valueClasses = cn(
  'text-3xl font-bold',
  gradient ? 'text-white' : 'text-foreground'
 )

 const descriptionClasses = cn(
  'text-sm',
  gradient ? 'text-slate-300' : 'text-muted-foreground'
 )

 return (
  <Card className={cardClasses}>
   <CardHeader className="pb-3">
    <div className="flex items-center justify-between">
     <CardTitle className={titleClasses}>
      <div className="flex items-center gap-2">
       {Icon && (
        <div className={cn(
         'p-2 rounded-lg',
         gradient ? 'bg-white/10' : 'bg-muted'
        )}>
         <Icon className={cn(
          'h-5 w-5',
          gradient ? 'text-white' : 'text-muted-foreground'
         )} />
        </div>
       )}
       <span>{title}</span>
      </div>
     </CardTitle>

     <div className="flex items-center gap-2">
      {trend && (
       <Badge
        className={cn(
         'text-xs flex items-center gap-1',
         trendUp ? BADGE_VARIANTS.success : BADGE_VARIANTS.error
        )}
       >
        <TrendIcon className="h-3 w-3" />
        {trend}
       </Badge>
      )}

      {actions && (
       <Button variant="ghost" size="icon" className="h-8 w-8">
        <MoreHorizontal className="h-4 w-4" />
       </Button>
      )}
     </div>
    </div>

    {description && (
     <p className={descriptionClasses}>{description}</p>
    )}
   </CardHeader>

   <CardContent className="space-y-4">
    <div className="flex items-center justify-between">
     <div className={valueClasses}>
      {typeof value === 'number' ? formattedValue : value}
     </div>

     {percentage !== undefined && (
      <div className="text-right">
       <div className={cn('text-2xl font-bold', trendColor)}>
        {percentage.toFixed(1)}%
       </div>
       <div className={descriptionClasses}>от общего</div>
      </div>
     )}
    </div>

    {children && (
     <div className="mt-4">
      {children}
     </div>
    )}
   </CardContent>
  </Card>
 )
}

/**
 * Компонент для сетки метрик
 */
export function MetricsGrid({
 children,
 columns = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
 className,
}: {
 children: React.ReactNode
 columns?: string
 className?: string
}) {
 return (
  <div className={cn('grid gap-6', columns, className)}>
   {children}
  </div>
 )
}

/**
 * Простая версия MetricCard для обратной совместимости
 */
export function SimpleMetricCard({
 title,
 value,
 icon: Icon,
 trend,
 trendUp,
 color = 'blue',
 description,
}: Omit<MetricCardProps, 'children' | 'actions' | 'size' | 'gradient'>) {
 const TrendIcon = trendUp ? TrendingUp : TrendingDown

 return (
  <Card className="transition-shadow hover:shadow-md">
   <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
    <CardTitle className="text-sm font-medium text-muted-foreground">
     {title}
    </CardTitle>
    {Icon && (
     <div className={cn('p-2 rounded-lg bg-muted')}>
      <Icon className="h-4 w-4 text-muted-foreground" />
     </div>
    )}
   </CardHeader>
   <CardContent>
    <div className="text-2xl font-bold">{value}</div>
    <div className="flex items-center gap-2 mt-1">
     {trend && (
      <Badge
       className={cn(
        'text-xs flex items-center gap-1',
        trendUp ? BADGE_VARIANTS.success : BADGE_VARIANTS.error
       )}
      >
       <TrendIcon className="h-3 w-3" />
       {trend}
      </Badge>
     )}
     {description && (
      <p className="text-xs text-muted-foreground">{description}</p>
     )}
    </div>
   </CardContent>
  </Card>
 )
}
