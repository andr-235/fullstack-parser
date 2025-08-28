'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { ICON_BACKGROUND_COLORS, STATS_ICON_COLORS, BADGE_VARIANTS } from '@/shared/constants'
import { cn } from '@/shared/lib/utils'
import { LucideIcon } from 'lucide-react'

export interface StatsCardProps {
 title: string
 value: number | string
 icon: LucideIcon
 description?: string
 trend?: string
 trendUp?: boolean
 color?: 'blue' | 'green' | 'purple' | 'red' | 'yellow' | 'cyan' | 'orange' | 'gray'
 percentage?: number
 className?: string
 variant?: 'default' | 'compact'
}

/**
 * Универсальный компонент для отображения статистики
 * Заменяет повторяющиеся паттерны карточек с иконками и значениями
 */
export function StatsCard({
 title,
 value,
 icon: Icon,
 description,
 trend,
 trendUp,
 color = 'blue',
 percentage,
 className,
 variant = 'default',
}: StatsCardProps) {
 const iconBgColor = ICON_BACKGROUND_COLORS[color]
 const iconTextColor = STATS_ICON_COLORS[color as keyof typeof STATS_ICON_COLORS] || STATS_ICON_COLORS[0]

 if (variant === 'compact') {
  return (
   <Card className={cn('transition-shadow hover:shadow-md', className)}>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
     <CardTitle className="text-sm font-medium text-muted-foreground">
      {title}
     </CardTitle>
     <Icon className={cn('h-4 w-4', iconTextColor)} />
    </CardHeader>
    <CardContent>
     <div className="text-2xl font-bold">{value}</div>
     {description && (
      <p className="text-xs text-muted-foreground mt-1">{description}</p>
     )}
    </CardContent>
   </Card>
  )
 }

 return (
  <Card className={cn('transition-shadow hover:shadow-md', className)}>
   <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
    <CardTitle className="text-sm font-medium text-muted-foreground">
     {title}
    </CardTitle>
    <div className={cn('p-2 rounded-lg', iconBgColor)}>
     <Icon className="h-4 w-4 text-white" />
    </div>
   </CardHeader>
   <CardContent>
    <div className="text-2xl font-bold">{value}</div>
    <div className="flex items-center gap-2 mt-1">
     {trend && (
      <Badge
       className={cn(
        'text-xs',
        trendUp ? BADGE_VARIANTS.success : BADGE_VARIANTS.error
       )}
      >
       {trend}
      </Badge>
     )}
     {description && (
      <p className="text-xs text-muted-foreground">{description}</p>
     )}
    </div>
    {percentage !== undefined && (
     <p className="text-xs text-muted-foreground mt-1">
      {percentage.toFixed(1)}% от общего
     </p>
    )}
   </CardContent>
  </Card>
 )
}

/**
 * Компонент для отображения списка статистики в сетке
 */
export function StatsGrid({
 stats,
 columns = 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
 className,
}: {
 stats: StatsCardProps[]
 columns?: string
 className?: string
}) {
 return (
  <div className={cn('grid gap-4', columns, className)}>
   {stats.map((stat, index) => (
    <StatsCard key={stat.title} {...stat} />
   ))}
  </div>
 )
}
