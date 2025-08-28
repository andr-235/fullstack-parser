'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { useChartColors } from '../hooks/use-chart-colors'
import { BADGE_VARIANTS } from '@/shared/constants'
import {
 LucideIcon,
 TrendingUp,
 TrendingDown,
 Download,
 Maximize2,
 MoreHorizontal,
 RefreshCw
} from 'lucide-react'

export interface ChartCardProps {
 /** Заголовок графика */
 title: string
 /** Описание графика */
 description?: string
 /** Иконка графика */
 icon?: LucideIcon
 /** Дочерний контент (сам график) */
 children: React.ReactNode
 /** Действия с графиком */
 actions?: Array<{
  label: string
  onClick: () => void
  icon?: LucideIcon
  variant?: 'default' | 'outline' | 'ghost'
 }>
 /** Тренд графика */
 trend?: {
  value: string
  direction: 'up' | 'down'
  description?: string
 }
 /** Период данных */
 period?: string
 /** Статус загрузки */
 isLoading?: boolean
 /** Высота графика */
 height?: number
 /** Классы для стилизации */
 className?: string
 /** Показывать ли градиентный фон */
 gradient?: boolean
}

/**
 * Универсальный компонент для отображения графиков
 * Заменяет повторяющиеся паттерны карточек с графиками
 */
export function ChartCard({
 title,
 description,
 icon: Icon,
 children,
 actions = [],
 trend,
 period,
 isLoading = false,
 height = 300,
 className,
 gradient = false,
}: ChartCardProps) {
 const TrendIcon = trend?.direction === 'up' ? TrendingUp : TrendingDown

 const cardClasses = cn(
  'transition-all duration-300 hover:shadow-lg',
  gradient && 'bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600',
  className
 )

 const titleClasses = cn(
  'text-lg font-semibold flex items-center gap-2',
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
      <div className="flex-1">
       <div className="flex items-center gap-2">
        <span>{title}</span>
        {period && (
         <Badge variant="outline" className="text-xs">
          {period}
         </Badge>
        )}
       </div>
       {description && (
        <p className={descriptionClasses}>{description}</p>
       )}
      </div>
     </CardTitle>

     <div className="flex items-center gap-2">
      {trend && (
       <Badge
        className={cn(
         'text-xs flex items-center gap-1',
         trend.direction === 'up' ? BADGE_VARIANTS.success : BADGE_VARIANTS.error
        )}
       >
        <TrendIcon className="h-3 w-3" />
        {trend.value}
        {trend.description && (
         <span className="ml-1 opacity-75">{trend.description}</span>
        )}
       </Badge>
      )}

      {actions.map((action, index) => {
       const ActionIcon = action.icon
       return (
        <Button
         key={index}
         onClick={action.onClick}
         variant={action.variant || 'ghost'}
         size="icon"
         className="h-8 w-8"
         title={action.label}
        >
         {ActionIcon && <ActionIcon className="h-4 w-4" />}
        </Button>
       )
      })}

      <Button variant="ghost" size="icon" className="h-8 w-8">
       <MoreHorizontal className="h-4 w-4" />
      </Button>
     </div>
    </div>
   </CardHeader>

   <CardContent>
    {isLoading ? (
     <div
      className="flex items-center justify-center bg-muted/30 rounded-lg"
      style={{ height }}
     >
      <div className="flex items-center gap-2 text-muted-foreground">
       <RefreshCw className="h-4 w-4 animate-spin" />
       <span className="text-sm">Загрузка графика...</span>
      </div>
     </div>
    ) : (
     <div style={{ height }}>
      {children}
     </div>
    )}
   </CardContent>
  </Card>
 )
}

/**
 * Компонент для сетки графиков
 */
export function ChartsGrid({
 children,
 columns = 'grid-cols-1 lg:grid-cols-2',
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
 * Хук для создания унифицированных настроек графика
 */
export function useChartConfig(options: {
 colors?: string[]
 showGrid?: boolean
 showLegend?: boolean
 height?: number
} = {}) {
 const {
  colors,
  showGrid = true,
  showLegend = true,
  height = 300,
 } = options

 const chartColors = useChartColors(colors?.length || 5, colors)

 const gridProps = showGrid ? {
  strokeDasharray: '3 3',
  stroke: 'hsl(var(--border))',
 } : {}

 const axisProps = {
  tick: { fill: 'hsl(var(--muted-foreground))', fontSize: 12 },
  axisLine: { stroke: 'hsl(var(--border))' },
 }

 const tooltipProps = {
  contentStyle: {
   backgroundColor: 'hsl(var(--popover))',
   border: `1px solid hsl(var(--border))`,
   borderRadius: 'var(--radius)',
   color: 'hsl(var(--popover-foreground))',
   boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  },
 }

 return {
  colors: chartColors,
  gridProps,
  axisProps,
  tooltipProps,
  legendProps: showLegend ? {} : { show: false },
  height,
 }
}
